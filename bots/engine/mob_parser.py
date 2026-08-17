"""
mob_parser.py
Parseia mob_db.yml do rAthena e extrai drops com taxas de drop.
Calcula raridade de cada item dropável.
"""

import yaml
import json
from pathlib import Path
from typing import Optional

MOB_DB_PATH    = Path(r"C:\rAthena\rathena\db\pre-re\mob_db.yml")
DROP_CACHE_PATH = Path(r"C:\rAthena\bots\market\drop_cache.json")
TRAIT_CACHE_PATH = Path(r"C:\rAthena\bots\market\mob_traits.json")

# Defaults do rAthena quando o campo é omitido no mob_db
DEFAULT_RACE    = "Formless"
DEFAULT_ELEMENT = "Neutral"
DEFAULT_SIZE    = "Medium"

# Raridade por taxa de drop (Rate em base 10000 = 100%)
RARITY_TIERS = [
    (1000, "common"),    # > 10%
    (100,  "uncommon"),  # 1% – 10%
    (10,   "rare"),      # 0.1% – 1%
    (0,    "epic"),      # < 0.1%
]

RARITY_MULTIPLIER = {
    "common":   2,
    "uncommon": 10,
    "rare":     50,
    "epic":     200,
}


def get_rarity(rate: int) -> str:
    """Retorna tier de raridade dado Rate (base 10000)."""
    for threshold, tier in RARITY_TIERS:
        if rate > threshold:
            return tier
    return "epic"


def parse_mob_db(path: Path = MOB_DB_PATH) -> tuple[dict, dict]:
    """
    Parseia mob_db.yml.
    Retorna:
      mobs: dict mob_id → {id, name, drops: [{item_id, rate}]}
      item_rarity: dict item_id → {rarity, max_rate, mob_names}
    """
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    mobs = {}
    item_rarity: dict[int, dict] = {}

    body = data.get("Body", [])
    for entry in body:
        mob_id   = entry.get("Id")
        mob_name = entry.get("Name", entry.get("AegisName", str(mob_id)))

        drops_raw = entry.get("Drops", []) or []
        drops = []
        for d in drops_raw:
            item_id = d.get("Item")
            rate    = d.get("Rate", 0) or 0
            if not item_id or rate == 0:
                continue
            drops.append({"item_id": item_id, "rate": rate})

            # Atualizar raridade global do item (usar a maior taxa entre todos os mobs)
            if item_id not in item_rarity:
                item_rarity[item_id] = {
                    "rarity":    get_rarity(rate),
                    "max_rate":  rate,
                    "mob_names": [mob_name],
                }
            else:
                existing = item_rarity[item_id]
                if rate > existing["max_rate"]:
                    existing["max_rate"] = rate
                    existing["rarity"]   = get_rarity(rate)
                if mob_name not in existing["mob_names"]:
                    existing["mob_names"].append(mob_name)

        mobs[mob_id] = {
            "id":    mob_id,
            "name":  mob_name,
            "drops": drops,
        }

    return mobs, item_rarity


def norm_mob_key(name: str) -> str:
    """Normaliza nome de mob para lookup: 'Soldier_Skeleton' == 'Soldier Skeleton'."""
    return "".join(ch for ch in name.upper() if ch.isalnum())


def parse_mob_traits(path: Path = MOB_DB_PATH) -> dict:
    """
    Extrai raça/elemento/tamanho de cada mob, indexado por nome normalizado
    (tanto AegisName quanto Name apontam para a mesma entrada).
    Usado para pontuar cartas com bônus condicional contra os alvos da build.
    """
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    traits: dict[str, dict] = {}
    for entry in data.get("Body", []):
        aegis = entry.get("AegisName", "")
        name  = entry.get("Name", aegis)
        modes = entry.get("Modes") or {}

        t = {
            "name":    name,
            "race":    entry.get("Race")    or DEFAULT_RACE,
            "element": entry.get("Element") or DEFAULT_ELEMENT,
            "size":    entry.get("Size")    or DEFAULT_SIZE,
            "level":   entry.get("Level", 1) or 1,
            "boss":    bool(modes.get("Mvp") or entry.get("Class") == "Boss"),
        }
        for key in (aegis, name):
            if key:
                traits[norm_mob_key(key)] = t

    return traits


def save_trait_cache(traits: dict, path: Path = TRAIT_CACHE_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(traits, f, ensure_ascii=False, indent=2)


def get_mob_traits(force_refresh: bool = False) -> dict:
    """Retorna dict {nome_normalizado: {race, element, size, level, boss}}."""
    if not force_refresh and TRAIT_CACHE_PATH.exists():
        with open(TRAIT_CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    traits = parse_mob_traits()
    save_trait_cache(traits)
    return traits


def price_from_rarity(rarity: str, base_buy: int) -> int:
    """Calcula preço sugerido de venda com base na raridade e buy price do item."""
    mult = RARITY_MULTIPLIER.get(rarity, 2)
    return max(base_buy * mult, 100)  # mínimo 100z


def save_drop_cache(item_rarity: dict, path: Path = DROP_CACHE_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(item_rarity, f, ensure_ascii=False, indent=2)


def load_drop_cache(path: Path = DROP_CACHE_PATH) -> Optional[dict]:
    # As chaves são AegisNames (mob_db.yml usa `Item: Emveretarcon`, não IDs
    # numéricos), então ficam como string. Consumidores devem buscar pelo
    # campo "aegis" do item, não pelo Id.
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_item_rarity(force_refresh: bool = False) -> dict:
    if not force_refresh:
        cached = load_drop_cache()
        if cached:
            return cached
    _, item_rarity = parse_mob_db()
    save_drop_cache(item_rarity)
    return item_rarity


if __name__ == "__main__":
    print("Parseando mob_db.yml...")
    mobs, item_rarity = parse_mob_db()
    save_drop_cache(item_rarity)

    print(f"  {len(mobs)} mobs carregados.")
    print(f"  {len(item_rarity)} itens com dados de drop.")

    by_rarity = {}
    for v in item_rarity.values():
        r = v["rarity"]
        by_rarity[r] = by_rarity.get(r, 0) + 1
    for tier, count in sorted(by_rarity.items()):
        print(f"  {tier}: {count} itens")

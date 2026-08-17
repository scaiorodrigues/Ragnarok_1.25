"""
item_parser.py
Parseia item_db_equip.yml e item_db.yml do rAthena.
Extrai equipamentos E cartas (incluindo variantes customizadas do import).
"""

import re
import json
import yaml
from pathlib import Path
from typing import Optional

ITEM_DB_PATH      = Path(r"C:\rAthena\rathena\db\pre-re\item_db_equip.yml")
# Cartas: item_db_etc.yml (cartas padrão Pre-RE) + item_db.yml import (variantes custom)
CARD_DB_PATH      = Path(r"C:\rAthena\rathena\db\pre-re\item_db_etc.yml")
CARD_IMPORT_PATH  = Path(r"C:\rAthena\rathena\db\import\item_db.yml")
CACHE_PATH        = Path(r"C:\rAthena\bots\market\item_cache.json")
CARD_CACHE_PATH   = Path(r"C:\rAthena\bots\market\card_cache.json")

# Mapeamento job_name → bit no campo Jobs do rAthena
JOB_BITS = {
    "Novice":       0,
    "Swordman":     1,
    "Mage":         2,
    "Archer":       3,
    "Acolyte":      4,
    "Merchant":     5,
    "Thief":        6,
    "Knight":       7,
    "Priest":       8,
    "Wizard":       9,
    "Blacksmith":  10,
    "Hunter":      11,
    "Assassin":    12,
    "Crusader":    14,
    "Monk":        15,
    "Sage":        16,
    "Rogue":       17,
    "Alchemist":   18,
    "Bard":        19,
    "Dancer":      20,
    "LordKnight":  23,
    "HighPriest":  24,
    "HighWizard":  25,
    "Sniper":      26,
    "Whitesmith":  27,
    "SinX":        28,
    "Paladin":     30,
    "Champion":    31,
    "Professor":   32,
    "Stalker":     33,
    "Creator":     34,
    "Clown":       35,
    "Gypsy":       36,
}

# Bônus de script → stat legível
# Os nomes precisam bater EXATAMENTE com os usados nos scripts do rAthena.
# bBaseAtk era o caso mais grave: 38 cartas dao ATK por essa chave e o mapa
# so tinha "bAtk", que nao aparece em script de carta nenhum — o bonus de
# ataque dessas cartas simplesmente nao era contado.
BONUS_MAP = {
    "bStr":         "STR",
    "bAgi":         "AGI",
    "bVit":         "VIT",
    "bInt":         "INT",
    "bDex":         "DEX",
    "bLuk":         "LUK",
    "bAllStats":    "AllStats",
    "bAtk":         "ATK",
    "bBaseAtk":     "ATK",
    "bMatk":        "MATK",
    "bDef":         "DEF",
    "bMdef":        "MDEF",
    "bHit":         "HIT",
    "bFlee":        "FLEE",
    "bMaxHP":       "MaxHP",
    "bMaxSP":       "MaxSP",
    "bAspd":        "ASPD",
    "bCritical":    "CRIT",
    "bFlee2":       "PerfectFlee",
    # percentuais — o rAthena mistura maiuscula e minuscula no "rate"
    "bAtkRate":     "ATK%",
    "bMatkRate":    "MATK%",
    "bDefRate":     "DEF%",
    "bMaxHPRate":   "MaxHP%",
    "bMaxHPrate":   "MaxHP%",
    "bMaxSPrate":   "MaxSP%",
    "bAspdRate":    "ASPD%",
    "bCritAtkRate": "CritDmg%",
}

# ─────────────────────────────────────────────────────────────────────────────
# Bônus CONDICIONAIS (bonus2/bonus3) — dependem do alvo, não são stats fixos.
# São 63% das cartas Pre-RE (Hydra, Raydric, Thara Frog...), e só fazem sentido
# pontuados contra o que a build realmente caça. Ver decision_engine.ThreatProfile.
#
# Formato de saída: {"atk_race": {"Demihuman": 20}, "def_ele": {"Neutral": 30}, ...}
# ─────────────────────────────────────────────────────────────────────────────
COND_MAP = {
    # ofensivos — % de dano a mais contra o alvo
    "bAddRace":          ("atk_race",   "RC_"),
    "bMagicAddRace":     ("matk_race",  "RC_"),
    "bCriticalAddRace":  ("crit_race",  "RC_"),
    "bAddEle":           ("atk_ele",    "Ele_"),
    "bMagicAddEle":      ("matk_ele",   "Ele_"),
    "bAddSize":          ("atk_size",   "Size_"),
    "bAddClass":         ("atk_class",  "Class_"),
    # defensivos — % de dano a menos vindo do alvo
    "bSubRace":          ("def_race",   "RC_"),
    "bSubEle":           ("def_ele",    "Ele_"),
    "bSubSize":          ("def_size",   "Size_"),
    "bSubClass":         ("def_class",  "Class_"),
    "bMagicSubRace":     ("mdef_race",  "RC_"),
    # utilidade
    "bExpAddRace":       ("exp_race",   "RC_"),
    "bSPGainRace":       ("sp_race",    "RC_"),
}

# Raças de player: no Pre-RE o jogador é Demihuman. Cartas anti-player
# (bAddRace,RC_Player_Human) valem contra Demihuman também para fins de score.
RACE_ALIASES = {
    "Player_Human": "Demihuman",
    "Player_Doram": "Brute",
    "DemiHuman":    "Demihuman",
    "DemiPlayer":   "Demihuman",
}

_COND_RE = re.compile(
    r'bonus[23]\s+(b\w+)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*,\s*(-?\d+)', re.IGNORECASE)
# bonus bDefEle,Ele_Ghost;  → muda o elemento da própria armadura
_DEFELE_RE = re.compile(r'bonus\s+bDefEle\s*,\s*Ele_(\w+)', re.IGNORECASE)


def parse_conditional_bonuses(script: str) -> dict:
    """Extrai bônus condicionais (por raça/elemento/tamanho) de um script."""
    cond: dict = {}
    if not script:
        return cond

    for m in _COND_RE.finditer(script):
        bkey, target, val = m.group(1), m.group(2), int(m.group(3))
        entry = COND_MAP.get(bkey)
        if not entry:
            continue
        field, prefix = entry
        if not target.startswith(prefix):
            continue
        name = target[len(prefix):]
        name = RACE_ALIASES.get(name, name)
        bucket = cond.setdefault(field, {})
        # max, não soma: RC_DemiHuman e RC_Player_Human são linhas separadas no
        # script (mob vs jogador) e colapsam no mesmo alvo depois do alias.
        # Contra um mob Demihuman só uma das duas aplica.
        bucket[name] = max(bucket.get(name, 0), val, key=abs) if name in bucket else val

    m = _DEFELE_RE.search(script)
    if m:
        cond["armor_ele"] = m.group(1)

    return cond


# Chaves conforme o schema real do item_db_equip.yml. As antigas
# ("Weapon"/"Shield"/"Accessory") não existem no YAML — deixavam 957 dos 2017
# equipamentos sem slot, ou seja, toda arma, escudo e acessório era inavaliável.
EQUIP_SLOTS = {
    "Head_Top":         "EQI_HEAD_TOP",
    "Head_Mid":         "EQI_HEAD_MID",
    "Head_Low":         "EQI_HEAD_LOW",
    "Armor":            "EQI_ARMOR",
    "Right_Hand":       "EQI_HAND_R",
    "Left_Hand":        "EQI_HAND_L",
    "Both_Hand":        "EQI_HAND_R",   # duas mãos: ocupa a direita e trava a esquerda
    "Garment":          "EQI_GARMENT",
    "Shoes":            "EQI_SHOES",
    "Both_Accessory":   "EQI_ACC_L",    # encaixa em qualquer um dos dois slots
    "Costume_Head_Top": "EQI_COSTUME_HEAD_TOP",
    "Costume_Head_Mid": "EQI_COSTUME_HEAD_MID",
    "Costume_Head_Low": "EQI_COSTUME_HEAD_LOW",
}


def parse_script_bonuses(script: str) -> dict:
    """Extrai bônus de stats de um script de item rAthena."""
    bonuses = {}
    if not script:
        return bonuses

    pattern = re.compile(r'bonus\s+(b\w+)\s*,\s*(-?\d+)', re.IGNORECASE)
    for match in pattern.finditer(script):
        bkey, val = match.group(1), int(match.group(2))
        stat = BONUS_MAP.get(bkey)
        if stat:
            bonuses[stat] = bonuses.get(stat, 0) + val

    return bonuses


# O campo Jobs do item_db lista só CLASSES BASE — não existe "LordKnight",
# "SinX", "Champion" etc. no YAML. Sem expandir, todo bot transcendente falha
# no can_equip() e não consegue usar nenhum equipamento com restrição de job.
# "BardDancer" é uma chave combinada, e "All" libera geral.
JOB_EQUIP_EXPANSION = {
    "Novice":      ["Novice"],
    "SuperNovice": ["Novice"],
    "Swordman":    ["Swordman"],
    "Knight":      ["Knight", "LordKnight"],
    "Crusader":    ["Crusader", "Paladin"],
    "Mage":        ["Mage"],
    "Wizard":      ["Wizard", "HighWizard"],
    "Sage":        ["Sage", "Professor"],
    "Archer":      ["Archer"],
    "Hunter":      ["Hunter", "Sniper"],
    "BardDancer":  ["Bard", "Dancer", "Clown", "Gypsy"],
    "Acolyte":     ["Acolyte"],
    "Priest":      ["Priest", "HighPriest"],
    "Monk":        ["Monk", "Champion"],
    "Merchant":    ["Merchant"],
    "Blacksmith":  ["Blacksmith", "Whitesmith"],
    "Alchemist":   ["Alchemist", "Creator"],
    "Thief":       ["Thief"],
    "Assassin":    ["Assassin", "SinX"],
    "Rogue":       ["Rogue", "Stalker"],
}


def parse_jobs(jobs_node) -> list[str]:
    """Converte o nó Jobs do YAML na lista de job names que o motor usa."""
    if not jobs_node:
        return list(JOB_BITS.keys())  # sem restrição = todos

    allowed: list[str] = []
    for key, flag in jobs_node.items():
        if not flag:
            continue
        if key == "All":
            return list(JOB_BITS.keys())
        for name in JOB_EQUIP_EXPANSION.get(key, [key]):
            if name not in allowed:
                allowed.append(name)
    return allowed


def parse_locations(loc_node) -> list[str]:
    """Converte o nó Locations do YAML em lista de slots EQI."""
    if not loc_node:
        return []
    slots = []
    for loc_name, active in loc_node.items():
        if not active or loc_name not in EQUIP_SLOTS:
            continue
        slots.append(EQUIP_SLOTS[loc_name])
        # Both_Accessory entra em qualquer um dos dois slots de acessório —
        # sem isso todo equip_prio que usa EQI_ACC_R era considerado inválido.
        if loc_name == "Both_Accessory":
            slots.append("EQI_ACC_R")
    return slots


def parse_item_db(path: Path = ITEM_DB_PATH) -> dict:
    """Parseia item_db_equip.yml e retorna dict por item Id."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    items = {}
    body = data.get("Body", [])

    for entry in body:
        item_id   = entry.get("Id")
        aegis     = entry.get("AegisName", "")
        name      = entry.get("Name", aegis)
        buy_price = entry.get("Buy", 0) or 0
        weight    = entry.get("Weight", 0) or 0
        slots     = entry.get("Slots", 0) or 0
        script    = entry.get("Script", "") or ""
        jobs_node = entry.get("Jobs")
        loc_node  = entry.get("Locations")
        # O schema usa WeaponLevel; "Level" não existe nesse YAML e devolvia
        # sempre 0. Attack/Defense também nunca eram lidos — o ATK base da arma,
        # que é o fator dominante de uma build física, ficava fora do score.
        weapon_lv = entry.get("WeaponLevel", 0) or 0

        item_type = entry.get("Type", "")

        items[item_id] = {
            "id":        item_id,
            "aegis":     aegis,
            "name":      name,
            "type":      item_type,
            "subtype":   entry.get("SubType", "") or "",
            "buy":       buy_price,
            "weight":    weight,
            "slots":     slots,
            "weapon_lv": weapon_lv,
            "atk":       entry.get("Attack", 0) or 0,
            "matk":      entry.get("MagicAttack", 0) or 0,
            "def":       entry.get("Defense", 0) or 0,
            "range":     entry.get("Range", 0) or 0,
            "equip_lv":  entry.get("EquipLevelMin", 0) or 0,
            "jobs":      parse_jobs(jobs_node),
            "locations": parse_locations(loc_node),
            "bonuses":   parse_script_bonuses(script),
            "cond":      parse_conditional_bonuses(script),
        }

    return items


def parse_card_db(paths: list[Path]) -> dict:
    """
    Parseia arquivos item_db.yml para extrair APENAS cartas (Type: Card).
    Retorna dict {item_id: {aegis, name, bonuses, slot_location}}.
    slot_location indica em qual slot de equipamento a carta pode ser inserida.
    """
    cards: dict = {}

    CARD_SLOT_MAP = {
        "Right_Hand":       "EQI_HAND_R",
        "Left_Hand":        "EQI_HAND_L",
        "Armor":            "EQI_ARMOR",
        "Garment":          "EQI_GARMENT",
        "Shoes":            "EQI_SHOES",
        "Accessory":        "EQI_ACC_L",
        "Both_Accessory":   "EQI_ACC_L",
        "Head_Top":         "EQI_HEAD_TOP",
        "Head_Mid":         "EQI_HEAD_MID",
        "Head_Low":         "EQI_HEAD_LOW",
    }

    for path in paths:
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        body = data.get("Body", []) if data else []
        for entry in body:
            if entry.get("Type") != "Card":
                continue
            item_id = entry.get("Id")
            if not item_id:
                continue

            # O import do rAthena faz merge parcial: campos ausentes na entrada
            # de import mantêm o valor do item_db base. Ex.: os reworks de MVP
            # card (4040/4128/4144/4174/4302) só redefinem Script, e herdam
            # Locations do pre-re. Espelhamos isso aqui.
            prev = cards.get(item_id, {})

            aegis    = entry.get("AegisName") or prev.get("aegis", "")
            script   = entry.get("Script")
            loc_node = entry.get("Locations")

            if loc_node is None:
                slot = prev.get("slot")
            else:
                slot = None
                for loc_name, active in loc_node.items():
                    if active and loc_name in CARD_SLOT_MAP:
                        slot = CARD_SLOT_MAP[loc_name]
                        break

            if script is None:
                bonuses = prev.get("bonuses", {})
                cond    = prev.get("cond", {})
            else:
                bonuses = parse_script_bonuses(script)
                cond    = parse_conditional_bonuses(script)

            cards[item_id] = {
                "id":       item_id,
                "aegis":    aegis,
                "name":     entry.get("Name") or prev.get("name", aegis),
                "bonuses":  bonuses,
                "cond":     cond,
                "slot":     slot,
                # SubType: Enchant = pedra de encantamento (4700-4785), não é
                # carta de drop de mob. Não deve entrar no pool de cartas do bot.
                "enchant":  (entry.get("SubType") or prev.get("_subtype")) == "Enchant",
                "_subtype": entry.get("SubType") or prev.get("_subtype"),
            }

    return cards


def build_name_index(items: dict) -> dict:
    """Índice secundário: AegisName → item_id."""
    return {v["aegis"]: k for k, v in items.items()}


def save_cache(items: dict, path: Path = CACHE_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def load_cache(path: Path = CACHE_PATH) -> Optional[dict]:
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return {int(k): v for k, v in raw.items()}


def get_items(force_refresh: bool = False) -> dict:
    """Retorna equipamentos do cache ou faz parse completo."""
    if not force_refresh:
        cached = load_cache()
        if cached:
            return cached
    items = parse_item_db()
    save_cache(items)
    return items


def get_cards(force_refresh: bool = False) -> dict:
    """Retorna cartas (incluindo variantes customizadas) do cache ou faz parse."""
    if not force_refresh:
        cached = load_cache(CARD_CACHE_PATH)
        if cached:
            return cached
    cards = parse_card_db([CARD_DB_PATH, CARD_IMPORT_PATH])
    save_cache(cards, CARD_CACHE_PATH)
    return cards


if __name__ == "__main__":
    print("Parseando item_db_equip.yml...")
    items = parse_item_db()
    save_cache(items)
    print(f"  {len(items)} equipamentos carregados.")

    print("Parseando cartas...")
    cards = get_cards(force_refresh=True)
    print(f"  {len(cards)} cartas carregadas.")

    sample = next(iter(items.values()))
    print(f"\nExemplo equip: {sample['name']} (ID {sample['id']})")
    print(f"  Jobs: {sample['jobs'][:5]}...")
    print(f"  Bônus: {sample['bonuses']}")
    print(f"  Slots: {sample['locations']}")

    card_sample = next((c for c in cards.values() if c["bonuses"]), None)
    if card_sample:
        print(f"\nExemplo carta: {card_sample['name']} (ID {card_sample['id']})")
        print(f"  Bônus: {card_sample['bonuses']}")
        print(f"  Slot: {card_sample['slot']}")

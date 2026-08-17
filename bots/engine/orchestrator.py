"""
orchestrator.py
Orquestrador central: coordena todos os bots, decide trades e parties.
Roda como serviço contínuo com loop de 30 segundos.
"""

import json
import time
import re
import threading
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Union

from decision_engine import BotProfile, MarketDecision, load_profile
from item_parser      import get_items

BOTS_DIR     = Path(r"C:\rAthena\bots")
PROFILES_DIR = BOTS_DIR / "profiles"
MARKET_DIR   = BOTS_DIR / "market"
LOGS_DIR     = BOTS_DIR / "logs"
CONFIG_DIR   = BOTS_DIR / "config"

TRADE_POINTS_FILE = CONFIG_DIR / "trade_points.json"
KNOWN_BOTS_FILE   = CONFIG_DIR / "known_bots.txt"

LOOP_INTERVAL   = 30   # segundos
SELL_TIMER      = 600  # bot fica na loja 10 minutos

logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "orchestrator.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger("orchestrator")


# ---------------------------------------------------------------------------
# Utilitários de arquivo com lock
# ---------------------------------------------------------------------------

def read_json_safe(path: Path) -> Optional[Union[dict, list]]:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def write_macro(bot_name: str, command: str):
    """Escreve comando no arquivo dynamic.txt do bot."""
    macro_path = BOTS_DIR / bot_name / "macros" / "dynamic.txt"
    macro_path.parent.mkdir(parents=True, exist_ok=True)
    with open(macro_path, "w", encoding="utf-8") as f:
        f.write(f"# gerado em {datetime.now().isoformat()}\n")
        f.write(command + "\n")


def append_macro(bot_name: str, command: str):
    macro_path = BOTS_DIR / bot_name / "macros" / "dynamic.txt"
    macro_path.parent.mkdir(parents=True, exist_ok=True)
    with open(macro_path, "a", encoding="utf-8") as f:
        f.write(command + "\n")


def clear_macro(bot_name: str):
    macro_path = BOTS_DIR / bot_name / "macros" / "dynamic.txt"
    if macro_path.exists():
        macro_path.write_text("# aguardando comandos\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Dados de mercado
# ---------------------------------------------------------------------------

def load_vends() -> list[dict]:
    data = read_json_safe(MARKET_DIR / "vends.json")
    return data if isinstance(data, list) else []


def load_chats() -> list[dict]:
    data = read_json_safe(MARKET_DIR / "chats.json")
    return data if isinstance(data, list) else []


# ---------------------------------------------------------------------------
# Leitura de log OpenKore — detectar loot de itens raros
# ---------------------------------------------------------------------------

LOOT_PATTERN = re.compile(
    r"You picked up (\d+) x (.+?) from",
    re.IGNORECASE
)

LOOT_ALT_PATTERN = re.compile(
    r"Item: (.+?) \((\d+)\) x\d+ @ loot",
    re.IGNORECASE
)

_last_log_pos: dict[str, int] = {}


def scan_bot_log(bot_name: str, items_index: dict) -> list[dict]:
    """Lê log do bot e retorna novos itens coletados desde última leitura."""
    log_path = LOGS_DIR / f"{bot_name}.log"
    if not log_path.exists():
        return []

    last_pos  = _last_log_pos.get(bot_name, 0)
    new_loots = []

    with open(log_path, encoding="utf-8", errors="ignore") as f:
        f.seek(last_pos)
        for line in f:
            m = LOOT_PATTERN.search(line)
            if m:
                qty, name = int(m.group(1)), m.group(2).strip()
                # Buscar item_id pelo nome
                for item_id, item in items_index.items():
                    if item["name"].lower() == name.lower() or item["aegis"].lower() == name.lower():
                        new_loots.append({"item_id": item_id, "qty": qty, "name": name})
                        break
        _last_log_pos[bot_name] = f.tell()

    return new_loots


# ---------------------------------------------------------------------------
# Lógica de trade
# ---------------------------------------------------------------------------

def find_nearest_trade_point(current_map: str) -> dict:
    points = read_json_safe(TRADE_POINTS_FILE) or {}
    # Se o bot já está num mapa com ponto de comércio, usar esse
    if current_map in points:
        return points[current_map]
    # Senão usar Prontera
    return points.get("prontera", {"map": "prontera", "x": 156, "y": 183})


def dispatch_sell(bot_name: str, profile: BotProfile, item_id: int, price: int, item_name: str):
    """Manda bot ir ao ponto de comércio e abrir chat/vend."""
    tp   = find_nearest_trade_point(profile.current_map)
    is_merchant = profile.job_name in ("Merchant", "Blacksmith", "Whitesmith", "Alchemist", "Creator")

    log.info(f"[{bot_name}] → VENDER {item_name} por {price}z em {tp['map']}")

    if is_merchant:
        write_macro(bot_name, f"go_vend {tp['map']} {tp['x']} {tp['y']} {item_id} {price}")
    else:
        write_macro(bot_name, f"open_chat WTS [{item_name}] {price}z {tp['map']} {tp['x']} {tp['y']} {item_id} {price} {SELL_TIMER}")


def dispatch_buy(bot_name: str, profile: BotProfile, item_id: int, price: int,
                 source_type: str, source_id: str, source_map: str, source_x: int, source_y: int):
    """Manda bot comprar item de vend shop ou direct trade."""
    log.info(f"[{bot_name}] → COMPRAR item {item_id} por {price}z de {source_type}:{source_id}")

    if source_type == "vend":
        write_macro(bot_name, f"buy_vend {source_id} {item_id} 1 {source_map} {source_x} {source_y}")
    else:
        write_macro(bot_name, f"buy_from_chat {source_id} {item_id} {price} {source_map} {source_x} {source_y}")


# ---------------------------------------------------------------------------
# Lógica de party
# ---------------------------------------------------------------------------

def group_bots_by_map(profiles: list[BotProfile]) -> dict[str, list[str]]:
    """Agrupa bots que estão no mesmo mapa."""
    groups: dict[str, list[str]] = {}
    for p in profiles:
        groups.setdefault(p.current_map, []).append(p.name)
    return groups


def dispatch_party_create(leader: str, members: list[str]):
    log.info(f"[{leader}] → CRIAR PARTY com {members}")
    write_macro(leader, f"party_create {' '.join(members)}")
    for m in members:
        write_macro(m, f"party_accept {leader}")


def dispatch_party_leave(bot_name: str):
    append_macro(bot_name, "party_leave")


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------

class Orchestrator:

    def __init__(self):
        self.engine   = MarketDecision()
        self.items    = get_items()
        self.known_bots = self._load_known_bots()
        log.info(f"Orquestrador iniciado. Bots conhecidos: {len(self.known_bots)}")

    def _load_known_bots(self) -> list[str]:
        path = KNOWN_BOTS_FILE
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").splitlines()
        return [l.strip() for l in lines if l.strip() and not l.startswith("#")]

    def _load_all_profiles(self) -> list[BotProfile]:
        profiles = []
        for p in PROFILES_DIR.glob("*.json"):
            try:
                profiles.append(BotProfile.from_file(p))
            except Exception as e:
                log.warning(f"Erro ao carregar {p.name}: {e}")
        return profiles

    def tick_economy(self, profiles: list[BotProfile]):
        """Verifica logs por novos loots e busca compradores."""
        vends = load_vends()
        chats = load_chats()

        for profile in profiles:
            if profile.in_combat:
                continue

            # 1. Verificar se bot tem item novo (log)
            new_loots = scan_bot_log(profile.name, self.items)
            for loot in new_loots:
                item_id   = loot["item_id"]
                sell_dec  = self.engine.should_sell(profile, item_id)
                if not sell_dec["decision"]:
                    continue

                price = sell_dec["price"]
                log.info(f"[{profile.name}] lootou {loot['name']} (rarity={sell_dec['rarity']}, preço={price}z)")

                # Procurar comprador entre outros bots
                buyer = self._find_buyer(profile.name, profiles, item_id, price)
                if buyer:
                    dispatch_sell(profile.name, profile, item_id, price, loot["name"])
                    dispatch_buy(
                        buyer.name, buyer, item_id, price,
                        "chat", profile.name,
                        find_nearest_trade_point(profile.current_map)["map"],
                        find_nearest_trade_point(profile.current_map)["x"],
                        find_nearest_trade_point(profile.current_map)["y"],
                    )
                else:
                    # Nenhum bot quer — abrir para jogadores reais também
                    dispatch_sell(profile.name, profile, item_id, price, loot["name"])

            # 2. Verificar mercado ativo (vends + chats) para compras
            self._scan_market_for_profile(profile, vends, chats)

    def _find_buyer(self, seller_name: str, profiles: list[BotProfile],
                    item_id: int, price: int) -> Optional[BotProfile]:
        candidates = []
        for p in profiles:
            if p.name == seller_name or p.in_combat:
                continue
            dec = self.engine.should_buy(p, item_id, price)
            if dec["decision"]:
                candidates.append((dec["score"], p))

        if not candidates:
            return None
        # Retorna o bot com maior score de utilidade para o item
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    def _scan_market_for_profile(self, profile: BotProfile,
                                  vends: list[dict], chats: list[dict]):
        """Verifica se há algo para comprar nas lojas/chats ativos."""
        # Vending shops
        for vend in vends:
            for itm in vend.get("items", []):
                item_id = itm.get("item_id")
                price   = itm.get("price", 0)
                if not item_id:
                    continue
                dec = self.engine.should_buy(profile, item_id, price)
                if dec["decision"]:
                    dispatch_buy(
                        profile.name, profile, item_id, price,
                        "vend", vend.get("vendor_id", ""),
                        vend.get("map", "prontera"),
                        vend.get("x", 156), vend.get("y", 183),
                    )
                    return  # Uma compra por tick para não sobrecarregar

        # Chat rooms (non-merchant sellers)
        for chat in chats:
            item_id = chat.get("item_id")
            price   = chat.get("price", 0)
            if not item_id:
                continue
            dec = self.engine.should_buy(profile, item_id, price)
            if dec["decision"]:
                dispatch_buy(
                    profile.name, profile, item_id, price,
                    "chat", chat.get("owner_id", ""),
                    chat.get("map", "prontera"),
                    chat.get("x", 156), chat.get("y", 183),
                )
                return

    def tick_parties(self, profiles: list[BotProfile]):
        """Forma parties com bots no mesmo mapa (máx 6 por grupo)."""
        groups = group_bots_by_map(profiles)
        for map_name, bot_names in groups.items():
            if len(bot_names) < 2:
                continue
            # Dividir em chunks de 6
            for i in range(0, len(bot_names), 6):
                chunk = bot_names[i:i+6]
                if len(chunk) < 2:
                    continue
                # Líder = primeiro bot do chunk
                leader  = chunk[0]
                members = chunk[1:]
                dispatch_party_create(leader, members)

    def run(self):
        log.info("=== Orquestrador iniciado ===")
        while True:
            try:
                profiles = self._load_all_profiles()
                if not profiles:
                    log.warning("Nenhum perfil encontrado em profiles/")
                else:
                    self.tick_economy(profiles)
                    self.tick_parties(profiles)
                    log.info(f"Tick concluido — {len(profiles)} bots ativos")
            except Exception as e:
                log.error(f"Erro no tick: {e}", exc_info=True)

            time.sleep(LOOP_INTERVAL)


if __name__ == "__main__":
    Orchestrator().run()

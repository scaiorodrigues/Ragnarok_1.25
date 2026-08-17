"""
decision_engine.py
Motor de decisão: avalia se um bot deve comprar/vender um item
com base em seu job, build e equipamentos atuais.
"""

import json
import threading
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

from item_parser import get_items, get_cards, JOB_BITS
from mob_parser  import (get_item_rarity, price_from_rarity,
                         get_mob_traits, norm_mob_key)

PROFILES_DIR = Path(r"C:\rAthena\bots\profiles")

# Stats primários e secundários por job_name (e variantes de build).
# Chave: "{ClassName}" (genérico) ou "{ClassName}_{Variante}" (específico).
# BotProfile.primary_stats/secondary_stats são baked no JSON na criação,
# então este dict é apenas fonte de verdade para profile_generator.py.
JOB_BUILDS: dict[str, dict] = {
    # ─── NOVICE / BASE ─────────────────────────────────────────────────
    "Novice":               {"primary": ["VIT", "STR"],      "secondary": ["DEF", "MaxHP"]},
    "Swordman":             {"primary": ["STR", "VIT"],      "secondary": ["DEF", "ATK"]},
    "Mage":                 {"primary": ["INT", "MATK"],     "secondary": ["MDEF", "MaxSP"]},
    "Archer":               {"primary": ["DEX", "AGI"],      "secondary": ["HIT", "FLEE"]},
    "Acolyte":              {"primary": ["INT", "VIT"],      "secondary": ["MDEF", "MaxSP"]},
    "Merchant":             {"primary": ["STR", "DEX"],      "secondary": ["VIT", "LUK"]},
    "Thief":                {"primary": ["AGI", "STR"],      "secondary": ["FLEE", "CRIT"]},

    # ─── KNIGHT ────────────────────────────────────────────────────────
    "Knight":               {"primary": ["STR", "VIT"],      "secondary": ["DEF", "ATK"]},
    "Knight_STR":           {"primary": ["STR", "ATK"],      "secondary": ["VIT", "DEF"]},
    "Knight_AGI":           {"primary": ["AGI", "FLEE"],     "secondary": ["STR", "CRIT"]},
    "Knight_VIT":           {"primary": ["VIT", "DEF"],      "secondary": ["STR", "MaxHP"]},

    # ─── LORD KNIGHT ───────────────────────────────────────────────────
    "LordKnight":              {"primary": ["STR", "VIT"],      "secondary": ["DEF", "ATK"]},
    "LordKnight_STR":          {"primary": ["STR", "ATK"],      "secondary": ["VIT", "DEF"]},
    "LordKnight_AGI":          {"primary": ["AGI", "FLEE"],     "secondary": ["STR", "CRIT"]},
    "LordKnight_VIT":          {"primary": ["VIT", "DEF"],      "secondary": ["STR", "MaxHP"]},
    "LordKnight_Spiral":       {"primary": ["VIT", "DEX"],      "secondary": ["AGI", "DEF"]},
    "LordKnight_Muramasa":     {"primary": ["AGI", "STR"],      "secondary": ["CRIT", "ATK"]},

    # ─── CRUSADER ──────────────────────────────────────────────────────
    "Crusader":             {"primary": ["VIT", "STR"],      "secondary": ["DEF", "MDEF"]},
    "Crusader_VIT":         {"primary": ["VIT", "DEF"],      "secondary": ["STR", "MDEF"]},
    "Crusader_Spear":       {"primary": ["STR", "ATK"],      "secondary": ["VIT", "DEF"]},

    # ─── PALADIN ───────────────────────────────────────────────────────
    "Paladin":              {"primary": ["VIT", "STR"],      "secondary": ["DEF", "MDEF"]},
    "Paladin_VIT":          {"primary": ["VIT", "MDEF"],     "secondary": ["STR", "MaxHP"]},
    "Paladin_GC":           {"primary": ["INT", "MATK"],     "secondary": ["VIT", "MDEF"]},
    "Paladin_Devotion":     {"primary": ["VIT", "DEF"],      "secondary": ["DEX", "MaxHP"]},

    # ─── WIZARD ────────────────────────────────────────────────────────
    "Wizard":               {"primary": ["INT", "MATK"],     "secondary": ["MDEF", "MaxSP"]},
    "Wizard_INT":           {"primary": ["INT", "MATK"],     "secondary": ["MDEF", "MaxSP"]},
    "Wizard_VIT":           {"primary": ["INT", "VIT"],      "secondary": ["MATK", "MaxHP"]},

    # ─── HIGH WIZARD ───────────────────────────────────────────────────
    "HighWizard":              {"primary": ["INT", "MATK"],     "secondary": ["MDEF", "MaxSP"]},
    "HighWizard_INT":          {"primary": ["INT", "MATK"],     "secondary": ["MDEF", "MaxSP"]},
    "HighWizard_VIT":          {"primary": ["INT", "VIT"],      "secondary": ["MATK", "MaxHP"]},
    "HighWizard_Soul":         {"primary": ["INT", "MATK"],     "secondary": ["MaxSP", "MDEF"]},
    "HighWizard_FirePillar":   {"primary": ["INT", "VIT"],      "secondary": ["MATK", "MaxHP"]},

    # ─── PRIEST ────────────────────────────────────────────────────────
    "Priest":               {"primary": ["INT", "VIT"],      "secondary": ["MDEF", "MaxHP"]},
    "Priest_Support":       {"primary": ["INT", "VIT"],      "secondary": ["MDEF", "MaxSP"]},
    "Priest_Battle":        {"primary": ["STR", "INT"],      "secondary": ["VIT", "ATK"]},

    # ─── HIGH PRIEST ───────────────────────────────────────────────────
    "HighPriest":           {"primary": ["INT", "VIT"],      "secondary": ["MDEF", "MaxHP"]},
    "HighPriest_Support":   {"primary": ["INT", "VIT"],      "secondary": ["MDEF", "MaxHP"]},
    "HighPriest_Battle":    {"primary": ["STR", "INT"],      "secondary": ["VIT", "ATK"]},
    "HighPriest_TU":        {"primary": ["INT", "LUK"],      "secondary": ["VIT", "MDEF"]},

    # ─── HUNTER ────────────────────────────────────────────────────────
    "Hunter":               {"primary": ["AGI", "DEX"],      "secondary": ["HIT", "FLEE"]},
    "Hunter_DEX":           {"primary": ["DEX", "HIT"],      "secondary": ["AGI", "ATK"]},
    "Hunter_AGI":           {"primary": ["AGI", "FLEE"],     "secondary": ["DEX", "CRIT"]},

    # ─── SNIPER ────────────────────────────────────────────────────────
    "Sniper":               {"primary": ["DEX", "AGI"],      "secondary": ["HIT", "CRIT"]},
    "Sniper_DEX":           {"primary": ["DEX", "HIT"],      "secondary": ["AGI", "ATK"]},
    "Sniper_Falcon":        {"primary": ["AGI", "DEX"],      "secondary": ["CRIT", "FLEE"]},
    "Sniper_Trap":          {"primary": ["DEX", "INT"],      "secondary": ["VIT", "MaxSP"]},

    # ─── ASSASSIN ──────────────────────────────────────────────────────
    "Assassin":             {"primary": ["AGI", "STR"],      "secondary": ["FLEE", "CRIT"]},
    "Assassin_AGI":         {"primary": ["AGI", "FLEE"],     "secondary": ["STR", "CRIT"]},
    "Assassin_SB":          {"primary": ["STR", "AGI"],      "secondary": ["ATK", "CRIT"]},

    # ─── SIN X ─────────────────────────────────────────────────────────
    "SinX":                 {"primary": ["AGI", "STR"],      "secondary": ["FLEE", "CRIT"]},
    "SinX_AGI":             {"primary": ["AGI", "FLEE"],     "secondary": ["STR", "CRIT"]},
    "SinX_EDP":             {"primary": ["STR", "ATK"],      "secondary": ["AGI", "CRIT"]},
    "SinX_Grimtooth":       {"primary": ["AGI", "LUK"],      "secondary": ["STR", "CRIT"]},

    # ─── MONK ──────────────────────────────────────────────────────────
    "Monk":                 {"primary": ["STR", "VIT"],      "secondary": ["AGI", "ATK"]},
    "Monk_Asura":           {"primary": ["STR", "INT"],      "secondary": ["VIT", "MaxSP"]},
    "Monk_AGI":             {"primary": ["AGI", "STR"],      "secondary": ["FLEE", "ATK"]},

    # ─── CHAMPION ──────────────────────────────────────────────────────
    "Champion":             {"primary": ["STR", "VIT"],      "secondary": ["AGI", "ATK"]},
    "Champion_Asura":       {"primary": ["STR", "INT"],      "secondary": ["VIT", "MaxSP"]},
    "Champion_Tiger":       {"primary": ["STR", "AGI"],      "secondary": ["ATK", "FLEE"]},
    "Champion_Snap":        {"primary": ["INT", "STR"],      "secondary": ["VIT", "MaxSP"]},

    # ─── BLACKSMITH ────────────────────────────────────────────────────
    "Blacksmith":           {"primary": ["STR", "DEX"],      "secondary": ["VIT", "ATK"]},
    "Blacksmith_STR":       {"primary": ["STR", "ATK"],      "secondary": ["VIT", "DEX"]},
    "Blacksmith_WS":        {"primary": ["DEX", "STR"],      "secondary": ["VIT", "LUK"]},

    # ─── WHITESMITH ────────────────────────────────────────────────────
    "Whitesmith":           {"primary": ["STR", "DEX"],      "secondary": ["VIT", "ATK"]},
    "Whitesmith_STR":       {"primary": ["STR", "ATK"],      "secondary": ["VIT", "DEX"]},
    "Whitesmith_Cart":      {"primary": ["STR", "VIT"],      "secondary": ["DEX", "ATK"]},
    "Whitesmith_MaxPow":    {"primary": ["VIT", "STR"],      "secondary": ["MaxHP", "DEF"]},

    # ─── SAGE ──────────────────────────────────────────────────────────
    "Sage":                 {"primary": ["INT", "DEX"],      "secondary": ["MDEF", "MATK"]},
    "Sage_INT":             {"primary": ["INT", "MATK"],     "secondary": ["MDEF", "MaxSP"]},
    "Sage_DEX":             {"primary": ["DEX", "INT"],      "secondary": ["MATK", "HIT"]},

    # ─── PROFESSOR ─────────────────────────────────────────────────────
    "Professor":            {"primary": ["INT", "DEX"],      "secondary": ["MDEF", "MATK"]},
    "Professor_INT":        {"primary": ["INT", "MATK"],     "secondary": ["MDEF", "MaxSP"]},
    "Professor_VIT":        {"primary": ["INT", "VIT"],      "secondary": ["MDEF", "MaxHP"]},

    # ─── ROGUE ─────────────────────────────────────────────────────────
    "Rogue":                {"primary": ["AGI", "STR"],      "secondary": ["FLEE", "DEX"]},
    "Rogue_AGI":            {"primary": ["AGI", "FLEE"],     "secondary": ["STR", "CRIT"]},
    "Rogue_STR":            {"primary": ["STR", "ATK"],      "secondary": ["AGI", "DEX"]},

    # ─── STALKER ───────────────────────────────────────────────────────
    "Stalker":              {"primary": ["AGI", "STR"],      "secondary": ["FLEE", "DEX"]},
    "Stalker_AGI":          {"primary": ["AGI", "FLEE"],     "secondary": ["STR", "DEX"]},
    "Stalker_Chase":        {"primary": ["AGI", "STR"],      "secondary": ["FLEE", "DEX"]},
    "Stalker_Snatcher":     {"primary": ["AGI", "LUK"],      "secondary": ["STR", "FLEE"]},

    # ─── ALCHEMIST ─────────────────────────────────────────────────────
    "Alchemist":            {"primary": ["INT", "VIT"],      "secondary": ["DEX", "STR"]},
    "Alchemist_INT":        {"primary": ["INT", "VIT"],      "secondary": ["DEX", "STR"]},
    "Alchemist_STR":        {"primary": ["STR", "INT"],      "secondary": ["VIT", "DEX"]},

    # ─── CREATOR ───────────────────────────────────────────────────────
    "Creator":              {"primary": ["INT", "VIT"],      "secondary": ["DEX", "STR"]},
    "Creator_INT":          {"primary": ["INT", "VIT"],      "secondary": ["DEX", "MaxSP"]},
    "Creator_VIT":          {"primary": ["VIT", "INT"],      "secondary": ["DEX", "MDEF"]},
    "Creator_FCP":          {"primary": ["DEX", "VIT"],      "secondary": ["MDEF", "MaxHP"]},
    "Creator_Vani":         {"primary": ["INT", "LUK"],      "secondary": ["STR", "DEX"]},

    # ─── BARD / CLOWN ──────────────────────────────────────────────────
    "Bard":                 {"primary": ["DEX", "AGI"],      "secondary": ["INT", "HIT"]},
    "Bard_DEX":             {"primary": ["DEX", "INT"],      "secondary": ["AGI", "HIT"]},
    "Clown":                {"primary": ["DEX", "AGI"],      "secondary": ["INT", "HIT"]},
    "Clown_DEX":            {"primary": ["DEX", "INT"],      "secondary": ["AGI", "HIT"]},

    # ─── DANCER / GYPSY ────────────────────────────────────────────────
    "Dancer":               {"primary": ["AGI", "DEX"],      "secondary": ["INT", "FLEE"]},
    "Dancer_AGI":           {"primary": ["AGI", "DEX"],      "secondary": ["INT", "FLEE"]},
    "Gypsy":                {"primary": ["AGI", "DEX"],      "secondary": ["INT", "FLEE"]},
    "Gypsy_AGI":            {"primary": ["AGI", "DEX"],      "secondary": ["INT", "FLEE"]},
}

# Classes de arma que cada job realmente usa nas skills da build. O campo Jobs
# do item_db é permissivo demais — um Champion "pode" equipar cajado, mas
# nenhuma skill de Champion funciona com ele. Sem isso o avaliador chegava a
# recomendar Lich Bone Wand para Asura Strike e machado para Creator.
JOB_WEAPONS: dict[str, set[str]] = {
    "Novice":     {"1hSword", "Dagger", "Mace", "1hAxe"},
    "Swordman":   {"1hSword", "2hSword", "1hSpear", "2hSpear", "Dagger"},
    "Knight":     {"1hSword", "2hSword", "1hSpear", "2hSpear", "Dagger"},
    "LordKnight": {"1hSword", "2hSword", "1hSpear", "2hSpear", "Dagger"},
    "Crusader":   {"1hSword", "2hSword", "1hSpear", "2hSpear", "Mace", "Dagger"},
    "Paladin":    {"1hSword", "2hSword", "1hSpear", "2hSpear", "Mace", "Dagger"},
    "Mage":       {"Staff", "2hStaff", "Dagger"},
    "Wizard":     {"Staff", "2hStaff", "Dagger"},
    "HighWizard": {"Staff", "2hStaff", "Dagger"},
    "Sage":       {"Staff", "2hStaff", "Dagger", "Book"},
    "Professor":  {"Staff", "2hStaff", "Dagger", "Book"},
    "Archer":     {"Bow"},
    "Hunter":     {"Bow", "Dagger"},
    "Sniper":     {"Bow", "Dagger"},
    "Bard":       {"Bow", "Musical", "Dagger"},
    "Clown":      {"Bow", "Musical", "Dagger"},
    "Dancer":     {"Bow", "Whip", "Dagger"},
    "Gypsy":      {"Bow", "Whip", "Dagger"},
    "Acolyte":    {"Mace", "Staff"},
    "Priest":     {"Mace", "Staff", "2hStaff", "Book"},
    "HighPriest": {"Mace", "Staff", "2hStaff", "Book"},
    # Monk/Champion pode equipar cajado no item_db, mas nenhuma build Pre-RE
    # usa — sem excluir, o avaliador recomendava Lich Bone Wand para Asura.
    "Monk":       {"Knuckle", "Mace"},
    "Champion":   {"Knuckle", "Mace"},
    "Merchant":   {"1hAxe", "2hAxe", "Mace", "Dagger", "1hSword"},
    "Blacksmith": {"1hAxe", "2hAxe", "Mace", "Dagger", "1hSword"},
    "Whitesmith": {"1hAxe", "2hAxe", "Mace", "Dagger", "1hSword"},
    "Alchemist":  {"1hAxe", "2hAxe", "Mace", "Dagger", "1hSword"},
    "Creator":    {"1hAxe", "2hAxe", "Mace", "Dagger", "1hSword"},
    "Thief":      {"Dagger", "1hSword", "Bow"},
    "Assassin":   {"Dagger", "Katar", "1hSword"},
    "SinX":       {"Dagger", "Katar", "1hSword"},
    "Rogue":      {"Dagger", "1hSword", "Bow"},
    "Stalker":    {"Dagger", "1hSword", "Bow"},
}

_lock = threading.Lock()


@dataclass
class BotProfile:
    name:           str
    job:            int
    job_name:       str
    base_level:     int
    zeny:           int
    primary_stats:  list[str]
    secondary_stats: list[str]
    current_equips: dict[str, Optional[int]]        = field(default_factory=dict)
    # Cartas slotadas por slot: {"EQI_ARMOR": [card_id, ...], ...}
    # Cada lista tem MAX_SLOTS entradas (0 = slot vazio)
    slotted_cards:  dict[str, list[Optional[int]]]  = field(default_factory=dict)
    in_combat:      bool                            = False
    current_map:    str                             = "prontera"
    build:          str                             = ""

    # ── Jornada de classe ────────────────────────────────────────────────
    # Nenhum bot nasce transcendente: para virar LordKnight ele precisa
    # passar por Knight, chegar a 99/50 e renascer, como qualquer jogador.
    # job_alvo guarda o destino final; job_name e onde ele esta agora.
    job_level:      int                             = 1
    job_alvo:       str                             = ""     # "" = job_name
    renasceu:       bool                            = False
    # Maior base_level ja atingido. O renascimento zera base_level para 1,
    # entao sem isto nao da para saber se um Knight lv40 esta subindo pela
    # primeira vez ou ja passou por 99.
    peak_base_level: int                            = 0

    @classmethod
    def from_file(cls, path: Path) -> "BotProfile":
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        d.setdefault("build", "")
        d.setdefault("slotted_cards", {})
        # Perfis antigos nao tem os campos de jornada
        d.setdefault("job_level", 1)
        d.setdefault("job_alvo", "")
        d.setdefault("renasceu", False)
        d.setdefault("peak_base_level", d.get("base_level", 0))
        return cls(**d)

    def objetivo(self) -> dict:
        """O que este bot deve fazer agora na jornada de classe."""
        from progression import proximo_objetivo
        return proximo_objetivo(self.job_name, self.base_level, self.job_level,
                                self.zeny, self.job_alvo or self.job_name,
                                self.renasceu)

    def jornada(self) -> str:
        from progression import resumo_jornada
        return resumo_jornada(self.job_name, self.base_level,
                              self.job_alvo or self.job_name, self.renasceu)

    def save(self, path: Optional[Path] = None):
        if path is None:
            path = PROFILES_DIR / f"{self.name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with _lock:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, ensure_ascii=False, indent=2)

    def can_equip(self, item: dict) -> bool:
        # nível mínimo do equipamento (EquipLevelMin) — sem isso o bot
        # "prefere" gear que ainda não consegue vestir
        if item.get("equip_lv", 0) > self.base_level:
            return False
        # arma de classe que o job não usa nas skills (ver JOB_WEAPONS)
        if item.get("type") == "Weapon":
            usable = JOB_WEAPONS.get(self.job_name)
            sub    = item.get("subtype", "")
            if usable and sub and sub not in usable:
                return False
        allowed_jobs = item.get("jobs", [])
        if not allowed_jobs:
            return True
        return self.job_name in allowed_jobs

    def slot_for_item(self, item: dict) -> Optional[str]:
        locs = item.get("locations", [])
        if not locs:
            return None
        return locs[0]

    def set_card(self, equip_slot: str, card_id: Optional[int], slot_index: int = 0):
        """Registra uma carta inserida num slot de equipamento."""
        cards = self.slotted_cards.setdefault(equip_slot, [None, None, None, None])
        if slot_index < len(cards):
            cards[slot_index] = card_id

    def get_cards(self, equip_slot: str) -> list[int]:
        """Retorna IDs de cartas no slot (sem Nones)."""
        return [c for c in self.slotted_cards.get(equip_slot, []) if c]


class ThreatProfile:
    """
    Traduz os hunt_mobs de uma build na distribuição de raça/elemento/tamanho
    que o bot realmente enfrenta.

    É isso que dá sentido às cartas com bônus condicional: 'Hydra +20% contra
    Demihuman' vale muito para quem farma Mummy/Anubis e zero para quem farma
    Poring. A cobertura é a fração dos alvos da build que casa com a condição.
    """

    def __init__(self, mob_names: list[str]):
        traits = get_mob_traits()
        self.mobs = []
        self.unknown = []
        for n in mob_names:
            t = traits.get(norm_mob_key(n))
            if t:
                self.mobs.append(t)
            else:
                self.unknown.append(n)

        self.races    = self._dist("race")
        self.elements = self._dist("element")
        self.sizes    = self._dist("size")
        self.in_elements = self._incoming_elements()

    # Fração do dano recebido que é ataque físico. No RO o ataque físico de
    # mob é elemento Neutral independente do elemento do próprio mob — o campo
    # Element do mob_db é a defesa dele, não o ataque. Por isso Raydric Card
    # (bSubEle,Ele_Neutral) é uma das melhores capas do Pre-RE: corta a maior
    # parte do dano recebido, venha de que mob vier.
    PHYSICAL_SHARE = 0.75

    def _incoming_elements(self) -> dict[str, float]:
        """Distribuição do elemento do dano RECEBIDO (≠ elemento dos mobs)."""
        if not self.mobs:
            return {}
        out = {"Neutral": self.PHYSICAL_SHARE}
        magic = 1.0 - self.PHYSICAL_SHARE
        for ele, frac in self.elements.items():
            out[ele] = out.get(ele, 0.0) + magic * frac
        return out

    def _dist(self, key: str) -> dict[str, float]:
        if not self.mobs:
            return {}
        n = len(self.mobs)
        out: dict[str, float] = {}
        for m in self.mobs:
            out[m[key]] = out.get(m[key], 0.0) + 1.0 / n
        return out

    def coverage(self, kind: str, target: str) -> float:
        """Fração dos alvos da build que casa com esta condição (0.0 – 1.0)."""
        if target == "All":
            return 1.0
        if kind == "race":
            return self.races.get(target, 0.0)
        if kind == "element":          # ofensivo: elemento defensivo do alvo
            return self.elements.get(target, 0.0)
        if kind == "in_element":       # defensivo: elemento do dano recebido
            return self.in_elements.get(target, 0.0)
        if kind == "size":
            return self.sizes.get(target, 0.0)
        return 0.0

    def __bool__(self) -> bool:
        return bool(self.mobs)

    def summary(self) -> str:
        top = lambda d: ", ".join(
            f"{k} {v:.0%}" for k, v in sorted(d.items(), key=lambda x: -x[1])[:3])
        return f"raças[{top(self.races)}] elem[{top(self.elements)}] tam[{top(self.sizes)}]"


class ItemEvaluator:
    """Calcula score de utilidade de um item (+ cartas nele) para um bot."""

    PRIMARY_WEIGHT   = 10
    SECONDARY_WEIGHT = 5
    OTHER_WEIGHT     = 2

    # Pesos dos bônus condicionais. Escala calibrada para ficar comparável aos
    # stats: +3 num stat primário = 30 pts; Hydra (+20% Demihuman) com 100% de
    # cobertura = 20 × 1.5 = 30 pts. Empate proposital — uma carta de raça bem
    # casada vale tanto quanto um stat primário forte.
    ATK_COND_WEIGHT   = 1.5   # dano a mais contra o alvo
    MATK_COND_WEIGHT  = 1.5
    CRIT_COND_WEIGHT  = 0.8
    DEF_COND_WEIGHT   = 1.2   # dano a menos vindo do alvo
    EXP_COND_WEIGHT   = 0.6
    SP_COND_WEIGHT    = 0.4

    # Campos de cond → (peso, tipo de alvo, é ofensivo)
    COND_FIELDS = {
        "atk_race":   (ATK_COND_WEIGHT,  "race",    True),
        "matk_race":  (MATK_COND_WEIGHT, "race",    True),
        "crit_race":  (CRIT_COND_WEIGHT, "race",    True),
        "atk_ele":    (ATK_COND_WEIGHT,  "element", True),
        "matk_ele":   (MATK_COND_WEIGHT, "element", True),
        "atk_size":   (ATK_COND_WEIGHT,  "size",    True),
        "atk_class":  (ATK_COND_WEIGHT,  "class",   True),
        "def_race":   (DEF_COND_WEIGHT,  "race",    False),
        "def_ele":    (DEF_COND_WEIGHT,  "in_element", False),
        "def_size":   (DEF_COND_WEIGHT,  "size",    False),
        "mdef_race":  (DEF_COND_WEIGHT,  "race",    False),
        "exp_race":   (EXP_COND_WEIGHT,  "race",    True),
        "sp_race":    (SP_COND_WEIGHT,   "race",    True),
    }

    # Peso da preferência de build: equipamento nomeado no equip_prio do guia
    # é o alvo de endgame daquela build. Precisa vencer gear genérico com stat
    # marginalmente melhor, sem virar infinito — 1ª escolha = 40 pts (acima de
    # um stat primário +3 = 30), caindo 10 por posição, piso 10.
    PREF_BASE  = 40
    PREF_DECAY = 10
    PREF_FLOOR = 10

    # ATK/MATK/DEF base do equipamento. São números de outra ordem de grandeza
    # que os bônus de script (uma Claymore tem 180 ATK, uma carta dá +3 STR),
    # então entram escalados: uma arma de topo rende ~45 pts, comparável à
    # preferência de build (40) — que é o peso certo, já que o ATK base é o
    # fator dominante de uma build física.
    ATK_SCALE     = 0.25   # build que valoriza ATK/STR
    ATK_SCALE_OFF = 0.05   # build que não valoriza
    DEF_SCALE     = 3.0
    DEF_SCALE_OFF = 0.5

    def _gear_score(self, profile: BotProfile, item: dict) -> int:
        """Pontua ATK/MATK/DEF base — atributos do item, não do script."""
        stats = set(profile.primary_stats) | set(profile.secondary_stats)
        phys  = bool(stats & {"ATK", "STR", "CRIT", "HIT", "AGI", "DEX"})
        magic = bool(stats & {"MATK", "INT"})
        tanky = bool(stats & {"DEF", "VIT", "MaxHP", "MDEF"})

        total  = item.get("atk", 0)  * (self.ATK_SCALE if phys  else self.ATK_SCALE_OFF)
        total += item.get("matk", 0) * (self.ATK_SCALE if magic else self.ATK_SCALE_OFF)
        total += item.get("def", 0)  * (self.DEF_SCALE if tanky else self.DEF_SCALE_OFF)
        return int(total)

    def __init__(self):
        self._items       = get_items()
        self._cards       = get_cards()
        self._item_rarity = get_item_rarity()
        self._threats: dict[str, ThreatProfile] = {}
        # índices reversos AegisName → id, para resolver equip_prio/card_prio
        self._item_by_aegis = {v["aegis"]: k for k, v in self._items.items() if v.get("aegis")}
        self._card_by_aegis = {v["aegis"]: k for k, v in self._cards.items() if v.get("aegis")}

    def build_key(self, profile: BotProfile) -> str:
        return f"{profile.job_name}_{profile.build}" if profile.build else profile.job_name

    def knowledge_for(self, profile: BotProfile) -> dict:
        """Entrada de BUILD_KNOWLEDGE da build, com fallback para o job puro."""
        from build_knowledge import BUILD_KNOWLEDGE
        return (BUILD_KNOWLEDGE.get(self.build_key(profile))
                or BUILD_KNOWLEDGE.get(profile.job_name)
                or {})

    def _pref_points(self, rank: int) -> int:
        return max(self.PREF_BASE - rank * self.PREF_DECAY, self.PREF_FLOOR)

    def equip_pref(self, profile: BotProfile, item: dict) -> int:
        """
        Pontos por o item ser o equipamento que o guia da build recomenda.
        É isso que faz o bot perseguir o gear da própria build em vez de
        aceitar qualquer coisa com stat útil.
        """
        kb = self.knowledge_for(profile)
        prio = kb.get("equip_prio") or {}
        if not prio:
            return 0
        aegis = item.get("aegis")
        if not aegis:
            return 0
        # procura em todos os slots que o item ocupa
        for slot in item.get("locations", []) or []:
            names = prio.get(slot) or []
            if aegis in names:
                return self._pref_points(names.index(aegis))
        return 0

    def card_pref(self, profile: BotProfile, card: dict) -> int:
        """Pontos por a carta estar no card_prio da build."""
        names = self.knowledge_for(profile).get("card_prio") or []
        aegis = card.get("aegis")
        if aegis and aegis in names:
            return self._pref_points(names.index(aegis))
        return 0

    def wishlist(self, profile: BotProfile) -> dict:
        """
        O que esta build quer, resolvido para IDs — o que o bot deve procurar
        no mercado. Nomes que não resolvem no item_db são reportados.
        """
        kb = self.knowledge_for(profile)
        equips, missing = {}, []
        for slot, names in (kb.get("equip_prio") or {}).items():
            ids = []
            for n in names:
                iid = self._item_by_aegis.get(n)
                (ids.append((n, iid)) if iid else missing.append(n))
            equips[slot] = ids
        cards = []
        for n in kb.get("card_prio") or []:
            cid = self._card_by_aegis.get(n)
            (cards.append((n, cid)) if cid else missing.append(n))
        return {"build": self.build_key(profile), "equips": equips,
                "cards": cards, "nao_encontrados": missing}

    def threat_for(self, profile: BotProfile) -> ThreatProfile:
        """ThreatProfile da build do bot, com cache por chave de build."""
        from build_knowledge import BUILD_KNOWLEDGE

        key = self.build_key(profile)
        if key in self._threats:
            return self._threats[key]

        kb = BUILD_KNOWLEDGE.get(key) or BUILD_KNOWLEDGE.get(profile.job_name)
        if kb:
            mobs = kb.get("hunt_mobs", [])
        else:
            # Bot sem variante de build (ex.: "Knight" puro) não tem entrada
            # própria. Usa a união dos alvos de todas as variantes do mesmo job
            # — um Knight genérico enfrenta o que os Knight_* enfrentam.
            prefix = f"{profile.job_name}_"
            mobs = []
            for k, v in BUILD_KNOWLEDGE.items():
                if k.startswith(prefix):
                    for m in v.get("hunt_mobs", []):
                        if m not in mobs:
                            mobs.append(m)

        tp = ThreatProfile(mobs)
        self._threats[key] = tp
        return tp

    def _cond_score(self, profile: BotProfile, cond: dict) -> int:
        """
        Pontua bônus condicionais contra o que a build caça.
        Sem hunt_mobs conhecidos o retorno é 0 — melhor ignorar do que chutar.
        """
        if not cond:
            return 0
        threat = self.threat_for(profile)
        if not threat:
            return 0

        total = 0.0
        for field_name, (weight, kind, _offensive) in self.COND_FIELDS.items():
            for target, pct in cond.get(field_name, {}).items():
                if pct <= 0:
                    continue
                total += pct * weight * threat.coverage(kind, target)
        return int(total)

    # Nem toda unidade de stat vale o mesmo. MaxHP/MaxSP vêm em centenas
    # enquanto STR/INT vêm em unidades — sem normalizar, um "MaxSP +300"
    # valia 1500 pts e engolia todo o resto do score.
    # Referência: 1.0 = um ponto de stat base (STR, INT, ...).
    STAT_SCALE = {
        "MaxHP": 0.01,   # 100 HP  ≈ 1 ponto de stat
        "MaxSP": 0.02,   #  50 SP  ≈ 1
        "ATK":   0.15,   #   7 ATK ≈ 1
        "MATK":  0.15,
        "DEF":   0.5,
        "MDEF":  0.5,
        "HIT":   0.2,
        "FLEE":  0.2,
        "CRIT":  0.5,
        "PerfectFlee": 0.5,
        "ASPD":  2.0,
    }

    def _bonus_score(self, profile: BotProfile, bonuses: dict) -> int:
        """Pontuação de um dict de bônus contra o perfil do bot."""
        total = 0.0
        for stat, val in bonuses.items():
            if val <= 0:
                continue
            val *= self.STAT_SCALE.get(stat, 1.0)
            if stat in profile.primary_stats:
                total += val * self.PRIMARY_WEIGHT
            elif stat in profile.secondary_stats:
                total += val * self.SECONDARY_WEIGHT
            else:
                total += val * self.OTHER_WEIGHT
        return int(total)

    def score(self, profile: BotProfile, item_id: int,
              card_ids: Optional[list[int]] = None) -> int:
        """
        Score total = bônus do equipamento + bônus de todas as cartas nele.
        card_ids: lista de IDs de cartas inseridas (None = usar profile.slotted_cards).
        """
        item = self._items.get(item_id)
        if not item:
            return 0
        if not profile.can_equip(item):
            return 0

        total = (self._bonus_score(profile, item.get("bonuses", {}))
                 + self._cond_score(profile, item.get("cond", {}))
                 + self._gear_score(profile, item)
                 + self.equip_pref(profile, item))

        # Cartas: usa a lista fornecida ou lê do perfil para esse slot
        slot = self.slot_for_equip(item)
        if card_ids is None:
            card_ids = profile.get_cards(slot) if slot else []

        for cid in card_ids:
            card = self._cards.get(cid)
            if card:
                total += (self._bonus_score(profile, card.get("bonuses", {}))
                          + self._cond_score(profile, card.get("cond", {}))
                          + self.card_pref(profile, card))

        return total

    def slot_for_equip(self, item: dict) -> Optional[str]:
        locs = item.get("locations", [])
        return locs[0] if locs else None

    def is_upgrade(self, profile: BotProfile, item_id: int) -> bool:
        """
        Verifica se item_id (sem cartas) supera o equipamento atual no slot
        considerando as cartas já slotadas no equipamento atual.
        """
        item = self._items.get(item_id)
        if not item:
            return False
        slot = self.slot_for_equip(item)
        if not slot:
            return False

        new_score = self.score(profile, item_id, card_ids=[])

        current_id = profile.current_equips.get(slot)
        if current_id is None:
            return new_score > 0

        # Score do equipamento atual inclui as cartas nele
        current_score = self.score(profile, current_id)
        return new_score > current_score

    def score_card(self, profile: BotProfile, card_id: int,
                   equip_slot: Optional[str] = None) -> int:
        """
        Score de uma carta avulsa (sem equipamento base).
        Soma stats fixos + bônus condicionais pesados pela cobertura da build.
        """
        card = self._cards.get(card_id)
        if not card:
            return 0
        if card.get("enchant"):
            return 0  # pedra de encantamento, não é carta de drop
        if equip_slot and card.get("slot") and card["slot"] != equip_slot:
            return 0  # carta não encaixa nesse tipo de equipamento
        return (self._bonus_score(profile, card.get("bonuses", {}))
                + self._cond_score(profile, card.get("cond", {}))
                + self.card_pref(profile, card))

    def explain_card(self, profile: BotProfile, card_id: int) -> dict:
        """Detalha por que uma carta pontuou o que pontuou (debug/tuning)."""
        card = self._cards.get(card_id)
        if not card:
            return {}
        threat = self.threat_for(profile)
        parts = []
        for field_name, (weight, kind, _off) in self.COND_FIELDS.items():
            for target, pct in card.get("cond", {}).get(field_name, {}).items():
                if pct <= 0:
                    continue
                cov = threat.coverage(kind, target)
                parts.append({
                    "efeito":    f"{field_name} {target} {pct:+d}%",
                    "cobertura": round(cov, 3),
                    "pontos":    int(pct * weight * cov),
                })
        return {
            "carta":      card["name"],
            "slot":       card["slot"],
            "stats":      card.get("bonuses", {}),
            "pts_stats":  self._bonus_score(profile, card.get("bonuses", {})),
            "condicoes":  parts,
            "pts_cond":   self._cond_score(profile, card.get("cond", {})),
            "total":      self.score_card(profile, card_id),
            "alvos":      threat.summary() if threat else "sem hunt_mobs",
        }

    def rarity(self, item_id: int) -> str:
        # item_rarity vem do mob_db, que indexa drops por AegisName
        item = self._items.get(item_id) or self._cards.get(item_id)
        if not item:
            return "common"
        info = self._item_rarity.get(item.get("aegis", ""))
        return info["rarity"] if info else "common"


class PriceCalculator:
    """Calcula preços de compra e venda sugeridos."""

    def __init__(self):
        self._items       = get_items()
        self._cards       = get_cards()
        self._item_rarity = get_item_rarity()

    def suggested_sell_price(self, item_id: int) -> int:
        item = self._items.get(item_id) or self._cards.get(item_id)
        if not item:
            return 100
        base_buy = item.get("buy", 0) or 0
        # item_rarity é indexado por AegisName (ver mob_parser.load_drop_cache)
        rarity   = self._item_rarity.get(item.get("aegis", ""), {}).get("rarity", "common")
        return price_from_rarity(rarity, base_buy)

    def max_buy_price(self, item_id: int) -> int:
        return int(self.suggested_sell_price(item_id) * 0.9)


class MarketDecision:
    """Decisão final: comprar ou não, a que preço."""

    ZENY_RESERVE_RATIO = 0.3

    def __init__(self):
        self.evaluator  = ItemEvaluator()
        self.pricer     = PriceCalculator()

    def should_buy(self, profile: BotProfile, item_id: int, asking_price: int,
                   card_ids: Optional[list[int]] = None) -> dict:
        """
        Decide se comprar item_id pelo asking_price.
        card_ids: cartas já inseridas no item (se vier do mercado com carta).
        """
        score = self.evaluator.score(profile, item_id, card_ids=card_ids or [])
        if score == 0:
            return {"decision": False, "reason": "item nao util para a build", "score": 0, "max_price": 0}

        if not self.evaluator.is_upgrade(profile, item_id):
            return {"decision": False, "reason": "item nao e upgrade do equipamento atual", "score": score, "max_price": 0}

        max_price = self.pricer.max_buy_price(item_id)
        budget    = int(profile.zeny * (1 - self.ZENY_RESERVE_RATIO))

        if asking_price > max_price:
            return {"decision": False, "reason": f"preco {asking_price}z acima do max {max_price}z", "score": score, "max_price": max_price}

        if asking_price > budget:
            return {"decision": False, "reason": f"zeny insuficiente (budget {budget}z)", "score": score, "max_price": max_price}

        return {"decision": True, "reason": "item util, preco ok, zeny suficiente", "score": score, "max_price": max_price}

    def should_buy_card(self, profile: BotProfile, card_id: int, asking_price: int,
                        target_slot: Optional[str] = None) -> dict:
        """Decide se vale comprar uma carta avulsa para inserir em equipamento."""
        score = self.evaluator.score_card(profile, card_id, equip_slot=target_slot)
        if score == 0:
            return {"decision": False, "reason": "carta sem bônus uteis para a build", "score": 0}

        max_price = self.pricer.max_buy_price(card_id)
        budget    = int(profile.zeny * (1 - self.ZENY_RESERVE_RATIO))

        if asking_price > max_price:
            return {"decision": False, "reason": f"preco {asking_price}z acima do max {max_price}z", "score": score}
        if asking_price > budget:
            return {"decision": False, "reason": f"zeny insuficiente (budget {budget}z)", "score": score}

        return {"decision": True, "reason": "carta util, preco ok", "score": score}

    def should_sell(self, profile: BotProfile, item_id: int) -> dict:
        """
        Decide se vender. Se item tem cartas slotadas, considera o valor combinado.
        Nunca sugere vender se o score com cartas ainda é o melhor no slot.
        """
        is_upgrade = self.evaluator.is_upgrade(profile, item_id)
        price      = self.pricer.suggested_sell_price(item_id)
        rarity     = self.evaluator.rarity(item_id)

        # Verifica se equipamento atual nesse slot tem cartas que elevam seu valor
        item = self.evaluator._items.get(item_id)
        if item:
            slot = self.evaluator.slot_for_equip(item)
            current_id = profile.current_equips.get(slot) if slot else None
            if current_id == item_id:
                # É o equipamento atual — verificar se score com cartas é alto
                score_with_cards = self.evaluator.score(profile, item_id)
                if score_with_cards > 0:
                    return {"decision": False, "reason": "equipamento atual (com cartas) ainda e o melhor no slot", "price": 0, "rarity": rarity}

        if is_upgrade:
            return {"decision": False, "reason": "item e upgrade para este bot", "price": 0, "rarity": rarity}

        return {"decision": True, "reason": "item nao e upgrade", "price": price, "rarity": rarity}


def load_profile(bot_name: str) -> Optional[BotProfile]:
    path = PROFILES_DIR / f"{bot_name}.json"
    if not path.exists():
        return None
    return BotProfile.from_file(path)


if __name__ == "__main__":
    profile = BotProfile(
        name="TestKnight",
        job=7, job_name="Knight",
        base_level=70, zeny=500_000,
        primary_stats=["STR", "ATK"],
        secondary_stats=["VIT", "DEF"],
        build="STR",
        current_equips={"EQI_HAND_R": None, "EQI_ARMOR": None},
    )

    engine = MarketDecision()
    items  = get_items()

    for item_id, item in list(items.items())[:5]:
        buy_decision  = engine.should_buy(profile, item_id, 10000)
        sell_decision = engine.should_sell(profile, item_id)
        print(f"[{item['name']}] comprar={buy_decision['decision']} vender={sell_decision['decision']}")

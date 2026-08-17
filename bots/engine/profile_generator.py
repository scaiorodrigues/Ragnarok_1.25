"""
profile_generator.py
Gera perfis JSON e config OpenKore para toda a frota de bots.
Stats baseados em guias Pre-Renewal do RateMyServer, iROWiki Classic,
TalonRO Wiki e ROGGH.
"""

from pathlib import Path
from decision_engine import BotProfile, JOB_BUILDS
from build_knowledge import get_farm_maps, get_buy_items, get_card_priorities, BUILD_KNOWLEDGE

PROFILES_DIR = Path(r"C:\rAthena\bots\profiles")
BOTS_DIR     = Path(r"C:\rAthena\bots")

# Job ID → nome da classe (Pre-RE)
JOB_ID = {
    0:  "Novice",
    1:  "Swordman",   2:  "Mage",       3:  "Archer",
    4:  "Acolyte",    5:  "Merchant",   6:  "Thief",
    7:  "Knight",     8:  "Priest",     9:  "Wizard",
    10: "Blacksmith", 11: "Hunter",     12: "Assassin",
    14: "Crusader",   15: "Monk",       16: "Sage",
    17: "Rogue",      18: "Alchemist",  19: "Bard",
    20: "Dancer",
    23: "LordKnight", 24: "HighPriest", 25: "HighWizard",
    26: "Sniper",     27: "Whitesmith", 28: "SinX",
    30: "Paladin",    31: "Champion",   32: "Professor",
    33: "Stalker",    34: "Creator",    35: "Clown",
    36: "Gypsy",
}

MERCHANT_JOBS = {"Merchant", "Blacksmith", "Whitesmith", "Alchemist", "Creator"}

# ─────────────────────────────────────────────────────────────────────────────
# BUILDS — stats baseados em guias Pre-Renewal verificados
# Chave: "{ClassName}" ou "{ClassName}_{Variante}"
# ─────────────────────────────────────────────────────────────────────────────
BUILDS: dict[str, dict] = {

    # ── NOVICE / BASE ────────────────────────────────────────────────────────
    "Novice": {
        "stats": {"str": 15, "agi": 15, "vit": 15, "int": 15, "dex": 15, "luk": 15},
        "primary": ["VIT", "STR"], "secondary": ["DEF", "MaxHP"],
    },
    "Swordman": {
        "stats": {"str": 70, "vit": 50, "agi": 20, "dex": 30, "int": 1, "luk": 1},
        "primary": ["STR", "VIT"], "secondary": ["DEF", "ATK"],
    },
    "Mage": {
        "stats": {"int": 80, "dex": 60, "vit": 20, "agi": 10, "str": 1, "luk": 1},
        "primary": ["INT", "MATK"], "secondary": ["MDEF", "MaxSP"],
    },
    "Archer": {
        "stats": {"dex": 80, "agi": 60, "str": 30, "vit": 20, "int": 1, "luk": 1},
        "primary": ["DEX", "AGI"], "secondary": ["HIT", "FLEE"],
    },
    "Acolyte": {
        "stats": {"int": 70, "vit": 50, "dex": 40, "agi": 20, "str": 1, "luk": 1},
        "primary": ["INT", "VIT"], "secondary": ["MDEF", "MaxSP"],
    },
    "Merchant": {
        "stats": {"str": 70, "dex": 60, "vit": 40, "agi": 20, "int": 1, "luk": 30},
        "primary": ["STR", "DEX"], "secondary": ["VIT", "LUK"],
    },
    "Thief": {
        "stats": {"agi": 80, "str": 50, "dex": 30, "vit": 20, "int": 1, "luk": 1},
        "primary": ["AGI", "STR"], "secondary": ["FLEE", "CRIT"],
    },

    # ── KNIGHT ───────────────────────────────────────────────────────────────
    # STR: Bowling Bash / Two-Hand Quicken (fonte: RateMyServer LK guide)
    "Knight_STR": {
        "stats": {"str": 90, "agi": 30, "vit": 60, "int": 1, "dex": 50, "luk": 1},
        "primary": ["STR", "ATK"], "secondary": ["VIT", "DEF"],
    },
    # AGI: Muramasa crit + Snake Head Hat Double Attack
    "Knight_AGI": {
        "stats": {"str": 70, "agi": 90, "vit": 30, "int": 1, "dex": 30, "luk": 30},
        "primary": ["AGI", "FLEE"], "secondary": ["STR", "CRIT"],
    },
    # VIT: spear tank, 100 total VIT = stun immune
    "Knight_VIT": {
        "stats": {"str": 60, "agi": 1, "vit": 99, "int": 20, "dex": 50, "luk": 1},
        "primary": ["VIT", "DEF"], "secondary": ["STR", "MaxHP"],
    },

    # ── LORD KNIGHT ──────────────────────────────────────────────────────────
    # STR: Executioner BB (fonte: RateMyServer Pure BB LK guide)
    "LordKnight_STR": {
        "stats": {"str": 95, "agi": 30, "vit": 80, "int": 1, "dex": 50, "luk": 1},
        "primary": ["STR", "ATK"], "secondary": ["VIT", "DEF"],
    },
    # AGI: Muramasa crit transcendente
    "LordKnight_AGI": {
        "stats": {"str": 80, "agi": 90, "vit": 30, "int": 1, "dex": 30, "luk": 30},
        "primary": ["AGI", "FLEE"], "secondary": ["STR", "CRIT"],
    },
    # VIT: WoE tank — 100 total VIT obrigatório
    "LordKnight_VIT": {
        "stats": {"str": 80, "agi": 1, "vit": 99, "int": 1, "dex": 60, "luk": 1},
        "primary": ["VIT", "DEF"], "secondary": ["STR", "MaxHP"],
    },
    # Spiral: dano escala com PESO da lança (Brocca/Gungnir), não STR — ignora DEF
    # Fonte: RateMyServer "Hybrid LK guide", TalonRO Spiral Pierce guide
    "LordKnight_Spiral": {
        "stats": {"str": 30, "agi": 40, "vit": 90, "int": 20, "dex": 70, "luk": 1},
        "primary": ["VIT", "DEX"], "secondary": ["AGI", "DEF"],
    },
    # Muramasa: LUK = BaseLV+1 garante imunidade à maldição (curse) do Muramasa
    # Fonte: iROWiki status resist formula, MyLifeInRagnarok "Mura-Knight Experience"
    "LordKnight_Muramasa": {
        "stats": {"str": 90, "agi": 99, "vit": 10, "int": 1, "dex": 14, "luk": 66},
        "primary": ["AGI", "STR"], "secondary": ["CRIT", "ATK"],
    },

    # ── CRUSADER ─────────────────────────────────────────────────────────────
    # VIT: Shield Chain — dano escala com peso do escudo
    "Crusader_VIT": {
        "stats": {"str": 80, "agi": 1, "vit": 80, "int": 30, "dex": 60, "luk": 1},
        "primary": ["VIT", "DEF"], "secondary": ["STR", "MDEF"],
    },
    # Spear: Holy Cross com 2H Spear — duplica hits vs Undead/Demon
    "Crusader_Spear": {
        "stats": {"str": 60, "agi": 40, "vit": 60, "int": 10, "dex": 60, "luk": 1},
        "primary": ["STR", "ATK"], "secondary": ["VIT", "DEF"],
    },

    # ── PALADIN ──────────────────────────────────────────────────────────────
    # VIT: Sacrifice — usa HP como dano fixo ignorando DEF do alvo
    "Paladin_VIT": {
        "stats": {"str": 25, "agi": 1, "vit": 99, "int": 25, "dex": 99, "luk": 1},
        "primary": ["VIT", "MDEF"], "secondary": ["STR", "MaxHP"],
    },
    # GC: Grand Cross — dano Holy com INT (fonte: RagnarokQuesting GC guide)
    "Paladin_GC": {
        "stats": {"str": 53, "agi": 9, "vit": 63, "int": 99, "dex": 37, "luk": 1},
        "primary": ["INT", "MATK"], "secondary": ["VIT", "MDEF"],
    },
    # Devotion: escravo de suporte WoE — desvia dano de aliados para si
    # DEX 99 para recast instantâneo de Devotion (CD curto, precisa de cast speed)
    # Fonte: RateMyServer Paladin Guide "Striving to Perfectness"
    "Paladin_Devotion": {
        "stats": {"str": 30, "agi": 10, "vit": 99, "int": 15, "dex": 99, "luk": 1},
        "primary": ["VIT", "DEF"], "secondary": ["DEX", "MaxHP"],
    },

    # ── WIZARD ───────────────────────────────────────────────────────────────
    # INT: Storm Gust — 150 DEX total = instant com Soul Link
    "Wizard_INT": {
        "stats": {"str": 1, "agi": 1, "vit": 20, "int": 99, "dex": 50, "luk": 1},
        "primary": ["INT", "MATK"], "secondary": ["MDEF", "MaxSP"],
    },
    # VIT: mais sobrevivência, Fire Wall / Earth Spike
    "Wizard_VIT": {
        "stats": {"str": 1, "agi": 1, "vit": 30, "int": 99, "dex": 60, "luk": 1},
        "primary": ["INT", "VIT"], "secondary": ["MATK", "MaxHP"],
    },

    # ── HIGH WIZARD ──────────────────────────────────────────────────────────
    # INT: Mystical Amplification +50% no próximo hit mágico
    "HighWizard_INT": {
        "stats": {"str": 1, "agi": 1, "vit": 30, "int": 99, "dex": 80, "luk": 1},
        "primary": ["INT", "MATK"], "secondary": ["MDEF", "MaxSP"],
    },
    # VIT: Meteor Storm WoE + mais HP
    "HighWizard_VIT": {
        "stats": {"str": 1, "agi": 1, "vit": 40, "int": 99, "dex": 70, "luk": 1},
        "primary": ["INT", "VIT"], "secondary": ["MATK", "MaxHP"],
    },
    # Soul: depende de Soul Link do Soul Linker parceiro para cast instantâneo
    # DEX apenas 30 — todos os pontos vão em INT. Storm Gust mais forte do jogo.
    # Fonte: RateMyServer HW Soul Link guide, TalonRO "dependent HW" builds
    "HighWizard_Soul": {
        "stats": {"str": 1, "agi": 1, "vit": 30, "int": 99, "dex": 30, "luk": 1},
        "primary": ["INT", "MATK"], "secondary": ["MaxSP", "MDEF"],
    },
    # FirePillar: coloca armadilhas Fire Pillar em choke points + Quagmire
    # DEX deliberadamente baixo — o foco é posicionamento, não spam de spells
    # Fonte: iROWiki Fire Pillar, WoE trap-layer guides
    "HighWizard_FirePillar": {
        "stats": {"str": 1, "agi": 1, "vit": 50, "int": 99, "dex": 30, "luk": 1},
        "primary": ["INT", "VIT"], "secondary": ["MATK", "MaxHP"],
    },

    # ── PRIEST ───────────────────────────────────────────────────────────────
    # Support: Heal / Buff / Resurrect (fonte: ROCharBuilds Pre-Renewal)
    "Priest_Support": {
        "stats": {"str": 1, "agi": 1, "vit": 60, "int": 80, "dex": 50, "luk": 1},
        "primary": ["INT", "VIT"], "secondary": ["MDEF", "MaxSP"],
    },
    # Battle: Magnus Exorcismus — Rosary + Sting Card (+30% ME)
    "Priest_Battle": {
        "stats": {"str": 40, "agi": 1, "vit": 60, "int": 80, "dex": 70, "luk": 1},
        "primary": ["STR", "INT"], "secondary": ["VIT", "ATK"],
    },

    # ── HIGH PRIEST ──────────────────────────────────────────────────────────
    # Support: Meditatio 10 (+2% Heal/nível), Assumptio (DEF+50%)
    "HighPriest_Support": {
        "stats": {"str": 1, "agi": 1, "vit": 60, "int": 90, "dex": 60, "luk": 1},
        "primary": ["INT", "VIT"], "secondary": ["MDEF", "MaxHP"],
    },
    # Battle: Magnus + Assumptio para sobrevivência solo
    "HighPriest_Battle": {
        "stats": {"str": 30, "agi": 1, "vit": 60, "int": 90, "dex": 70, "luk": 1},
        "primary": ["STR", "INT"], "secondary": ["VIT", "ATK"],
    },
    # TU: Turn Undead — LUK aumenta taxa de sucesso (fórmula usa LUK/10 + INT/10)
    # Gloria (+30 LUK temporário) antes de TU sobe ~3% chance. Farm GH solo.
    # Fonte: iROWiki Turn Undead, RateMyServer TU Priest forum, TalonRO Priest guide
    "HighPriest_TU": {
        "stats": {"str": 1, "agi": 1, "vit": 60, "int": 99, "dex": 60, "luk": 40},
        "primary": ["INT", "LUK"], "secondary": ["VIT", "MDEF"],
    },

    # ── HUNTER ───────────────────────────────────────────────────────────────
    # DEX: Double Strafe — Composite Bow[4] 3xAbysmal + Skel Worker
    "Hunter_DEX": {
        "stats": {"str": 10, "agi": 75, "vit": 30, "int": 1, "dex": 99, "luk": 1},
        "primary": ["DEX", "HIT"], "secondary": ["AGI", "ATK"],
    },
    # AGI: Auto-Blitz — (AGI+LUK)/10% chance, Falcon ATK = INT×5
    "Hunter_AGI": {
        "stats": {"str": 1, "agi": 90, "vit": 20, "int": 30, "dex": 40, "luk": 90},
        "primary": ["AGI", "FLEE"], "secondary": ["DEX", "CRIT"],
    },

    # ── SNIPER ───────────────────────────────────────────────────────────────
    # DEX: Sharp Shooting / True Sight (ATK+20, HIT+10)
    "Sniper_DEX": {
        "stats": {"str": 10, "agi": 75, "vit": 50, "int": 10, "dex": 99, "luk": 1},
        "primary": ["DEX", "HIT"], "secondary": ["AGI", "ATK"],
    },
    # Falcon: True Sight + Wind Walk, AGI+LUK build
    "Sniper_Falcon": {
        "stats": {"str": 1, "agi": 99, "vit": 20, "int": 30, "dex": 40, "luk": 80},
        "primary": ["AGI", "DEX"], "secondary": ["CRIT", "FLEE"],
    },
    # Trap: dano de armadilhas escala com (DEX+INT), não ATK — STR/AGI = 1
    # INT 80 atinge checkpoint ×(1+80/35) — grande spike de dano. Ankle Snare + Claymore.
    # Fonte: ROGGH "Trap Hunter/Sniper Leveling Guide", RateMyServer Hunter FAQ
    "Sniper_Trap": {
        "stats": {"str": 1, "agi": 1, "vit": 65, "int": 80, "dex": 99, "luk": 1},
        "primary": ["DEX", "INT"], "secondary": ["VIT", "MaxSP"],
    },

    # ── ASSASSIN ─────────────────────────────────────────────────────────────
    # AGI: Katar crit — Infiltrator (AGI+5, STR+1), katar duplica crit
    "Assassin_AGI": {
        "stats": {"str": 60, "agi": 90, "vit": 20, "int": 1, "dex": 30, "luk": 30},
        "primary": ["AGI", "FLEE"], "secondary": ["STR", "CRIT"],
    },
    # SB: Sonic Blow — 800% ATK, EDP ×3.2
    "Assassin_SB": {
        "stats": {"str": 90, "agi": 40, "vit": 40, "int": 1, "dex": 60, "luk": 1},
        "primary": ["STR", "AGI"], "secondary": ["ATK", "CRIT"],
    },

    # ── ASSASSIN CROSS ───────────────────────────────────────────────────────
    # AGI: EDP + Sonic Blow principal
    "SinX_AGI": {
        "stats": {"str": 90, "agi": 80, "vit": 30, "int": 1, "dex": 50, "luk": 1},
        "primary": ["AGI", "FLEE"], "secondary": ["STR", "CRIT"],
    },
    # EDP: Enchant Deadly Poison — Sonic Blow burst, sem crit
    "SinX_EDP": {
        "stats": {"str": 99, "agi": 70, "vit": 30, "int": 1, "dex": 50, "luk": 1},
        "primary": ["STR", "ATK"], "secondary": ["AGI", "CRIT"],
    },
    # Grimtooth: WoE disruptor cloaked — ataca em 3×3 de 6 cells com Cloaking ativo
    # VIT 15 intencional — nunca deve tomar hits (sempre cloaked)
    # LUK 45 converte em crit no Grimtooth. AGI alto para spam enquanto oculto.
    # Fonte: RateMyServer "A Comprehensive Guide to Grimtoothing"
    "SinX_Grimtooth": {
        "stats": {"str": 75, "agi": 85, "vit": 15, "int": 10, "dex": 75, "luk": 45},
        "primary": ["AGI", "LUK"], "secondary": ["STR", "CRIT"],
    },

    # ── MONK ─────────────────────────────────────────────────────────────────
    # Asura: Guillotine Fist — SP cap ≈ 6000, STR+INT para dano
    "Monk_Asura": {
        "stats": {"str": 100, "agi": 20, "vit": 40, "int": 90, "dex": 70, "luk": 1},
        "primary": ["STR", "INT"], "secondary": ["VIT", "MaxSP"],
    },
    # AGI: Combo — Trifecta > Quadruple > Thrust > Tiger Knuckle
    "Monk_AGI": {
        "stats": {"str": 80, "agi": 80, "vit": 30, "int": 20, "dex": 50, "luk": 1},
        "primary": ["AGI", "STR"], "secondary": ["FLEE", "ATK"],
    },

    # ── CHAMPION ─────────────────────────────────────────────────────────────
    # Asura: Snap + Guillotine Fist, Zen para esferas instantâneas
    "Champion_Asura": {
        "stats": {"str": 110, "agi": 20, "vit": 40, "int": 90, "dex": 70, "luk": 1},
        "primary": ["STR", "INT"], "secondary": ["VIT", "MaxSP"],
    },
    # Tiger: Body Relocation + Raging Trifecta, AGI alto
    "Champion_Tiger": {
        "stats": {"str": 80, "agi": 80, "vit": 40, "int": 1, "dex": 50, "luk": 1},
        "primary": ["STR", "AGI"], "secondary": ["ATK", "FLEE"],
    },
    # Snap: INT alto (~90) aumenta SP máximo → Asura mais forte + mobilidade via Snap
    # Diferente do Asura puro: troca STR por INT, output mais estável com SP parcial
    # Fonte: TalonRO "Lino's Vanilla Champion Guide", Origins Wiki Champion
    "Champion_Snap": {
        "stats": {"str": 90, "agi": 10, "vit": 70, "int": 90, "dex": 50, "luk": 1},
        "primary": ["INT", "STR"], "secondary": ["VIT", "MaxSP"],
    },

    # ── BLACKSMITH ───────────────────────────────────────────────────────────
    # STR: Mammonite — Battle Axe[4]: Orc Lady×2 + Hydra + Vadon (OHKO High Orcs)
    "Blacksmith_STR": {
        "stats": {"str": 99, "agi": 40, "vit": 40, "int": 1, "dex": 40, "luk": 1},
        "primary": ["STR", "ATK"], "secondary": ["VIT", "DEX"],
    },
    # WS: Weapon Perfection, forja de armas raras — LUK para forge chance
    "Blacksmith_WS": {
        "stats": {"str": 50, "agi": 1, "vit": 30, "int": 30, "dex": 99, "luk": 50},
        "primary": ["DEX", "STR"], "secondary": ["VIT", "LUK"],
    },

    # ── WHITESMITH ───────────────────────────────────────────────────────────
    # STR: Cart Termination — Giant Axe, usar Zipper Bear/Andre/Porcelio (flat ATK)
    "Whitesmith_STR": {
        "stats": {"str": 99, "agi": 50, "vit": 50, "int": 1, "dex": 50, "luk": 1},
        "primary": ["STR", "ATK"], "secondary": ["VIT", "DEX"],
    },
    # Cart: Cart Revolution AoE + Mammonite para bosses
    "Whitesmith_Cart": {
        "stats": {"str": 90, "agi": 40, "vit": 50, "int": 1, "dex": 40, "luk": 1},
        "primary": ["STR", "VIT"], "secondary": ["DEX", "ATK"],
    },
    # MaxPow: Maximize Power elimina variância de dano (min=max ATK). VIT 99 para
    # tankar Earthquake de MVPs (requer ~15500 HP). Solo MVP Baphomet/Valkyrie.
    # Fonte: iROWiki Maximize Power, WS MVP solo guides
    "Whitesmith_MaxPow": {
        "stats": {"str": 70, "agi": 50, "vit": 99, "int": 1, "dex": 55, "luk": 1},
        "primary": ["VIT", "STR"], "secondary": ["MaxHP", "DEF"],
    },

    # ── SAGE ─────────────────────────────────────────────────────────────────
    # INT: Land Protector Lv3-4, 130+ DEX para LP rápido (fonte: ROGGH Sage guide)
    "Sage_INT": {
        "stats": {"str": 1, "agi": 1, "vit": 40, "int": 80, "dex": 99, "luk": 1},
        "primary": ["INT", "MATK"], "secondary": ["MDEF", "MaxSP"],
    },
    # DEX: Hindsight auto-cast Cold Bolt, Battle Sage
    "Sage_DEX": {
        "stats": {"str": 60, "agi": 80, "vit": 30, "int": 85, "dex": 45, "luk": 1},
        "primary": ["DEX", "INT"], "secondary": ["MATK", "HIT"],
    },

    # ── PROFESSOR ────────────────────────────────────────────────────────────
    # INT: Soul Burn (drena 20000 SP), Fiber Lock + Heaven's Drive
    "Professor_INT": {
        "stats": {"str": 1, "agi": 1, "vit": 50, "int": 90, "dex": 99, "luk": 1},
        "primary": ["INT", "MATK"], "secondary": ["MDEF", "MaxSP"],
    },
    # VIT: Fiber Lock tank, MVP holder em WoE
    "Professor_VIT": {
        "stats": {"str": 1, "agi": 1, "vit": 99, "int": 80, "dex": 99, "luk": 1},
        "primary": ["INT", "VIT"], "secondary": ["MDEF", "MaxHP"],
    },

    # ── ROGUE ────────────────────────────────────────────────────────────────
    # AGI: Snatcher — Main Gauche[4] + 4x Sidewinder = Double Attack Lv5
    "Rogue_AGI": {
        "stats": {"str": 70, "agi": 90, "vit": 20, "int": 1, "dex": 50, "luk": 1},
        "primary": ["AGI", "FLEE"], "secondary": ["STR", "CRIT"],
    },
    # STR: Backstab — 700% ATK, ignora flee, deve atacar pelas costas
    "Rogue_STR": {
        "stats": {"str": 90, "agi": 60, "vit": 30, "int": 1, "dex": 60, "luk": 1},
        "primary": ["STR", "ATK"], "secondary": ["AGI", "DEX"],
    },

    # ── STALKER ──────────────────────────────────────────────────────────────
    # AGI: Chase Walk + Plagiarism (copia ME do HP para farm solo)
    "Stalker_AGI": {
        "stats": {"str": 70, "agi": 90, "vit": 30, "int": 1, "dex": 60, "luk": 1},
        "primary": ["AGI", "FLEE"], "secondary": ["STR", "DEX"],
    },
    # Chase: Full Strip WoE — remove todos os 4 slots do alvo
    "Stalker_Chase": {
        "stats": {"str": 70, "agi": 80, "vit": 40, "int": 1, "dex": 60, "luk": 1},
        "primary": ["AGI", "STR"], "secondary": ["FLEE", "DEX"],
    },
    # Snatcher: Snatcher Lv10 roda Steal em todo ataque físico. LUK melhora taxa
    # de sucesso do Steal. AGI alto = mais ataques por segundo = mais roubos.
    # Chase Walk ATK bonus após sair do stealth mata mob antes de fugir.
    # Fonte: RateMyServer Stalker/Rogue Guide, TalonRO Snatcher builds
    "Stalker_Snatcher": {
        "stats": {"str": 60, "agi": 90, "vit": 30, "int": 10, "dex": 60, "luk": 45},
        "primary": ["AGI", "LUK"], "secondary": ["STR", "FLEE"],
    },

    # ── ALCHEMIST ────────────────────────────────────────────────────────────
    # INT: Homunculus + Potion Pitcher, mass produce Condensed White Potion
    "Alchemist_INT": {
        "stats": {"str": 30, "agi": 1, "vit": 40, "int": 80, "dex": 50, "luk": 1},
        "primary": ["INT", "VIT"], "secondary": ["DEX", "STR"],
    },
    # STR: Acid Bomb tanque físico
    "Alchemist_STR": {
        "stats": {"str": 60, "agi": 30, "vit": 30, "int": 70, "dex": 40, "luk": 1},
        "primary": ["STR", "INT"], "secondary": ["VIT", "DEX"],
    },

    # ── CREATOR ──────────────────────────────────────────────────────────────
    # INT: Acid Demo — INT 99 + Lex Aeterna = dano enorme vs VIT alto
    "Creator_INT": {
        "stats": {"str": 1, "agi": 1, "vit": 40, "int": 99, "dex": 50, "luk": 1},
        "primary": ["INT", "VIT"], "secondary": ["DEX", "MaxSP"],
    },
    # VIT: Chemical Protection WoE + Homunculus tank
    "Creator_VIT": {
        "stats": {"str": 1, "agi": 1, "vit": 99, "int": 70, "dex": 60, "luk": 1},
        "primary": ["VIT", "INT"], "secondary": ["DEX", "MDEF"],
    },
    # FCP: Full Chemical Protection slave WoE — apenas spamma FCP nos aliados
    # DEX 99 para recast rápido (FCP tem cast time variável). STR 1 intencional.
    # Fonte: RateMyServer Creator Guide for WoE, OriginsRO Creator wiki
    "Creator_FCP": {
        "stats": {"str": 1, "agi": 1, "vit": 70, "int": 20, "dex": 99, "luk": 1},
        "primary": ["DEX", "VIT"], "secondary": ["MDEF", "MaxHP"],
    },
    # Vanilmirth: Caprice (Homunculus) dispara bolt aleatório com MATK do pet
    # Feather Mace (Creator exclusivo) dá MATK+20 com Mace Mastery
    # Fonte: RateMyServer "Big Fat Homunculus Bible", iROWiki Vanilmirth
    "Creator_Vani": {
        "stats": {"str": 70, "agi": 1, "vit": 60, "int": 75, "dex": 50, "luk": 40},
        "primary": ["INT", "LUK"], "secondary": ["STR", "DEX"],
    },

    # ── BARD ─────────────────────────────────────────────────────────────────
    # DEX: Poem of Bragi — DEX reduz delay (cada 10 pts), INT reduz cast
    "Bard_DEX": {
        "stats": {"str": 1, "agi": 30, "vit": 40, "int": 40, "dex": 99, "luk": 1},
        "primary": ["DEX", "INT"], "secondary": ["AGI", "HIT"],
    },

    # ── CLOWN ────────────────────────────────────────────────────────────────
    # DEX: Poem of Bragi transcendente + Tarot Card of Fate
    "Clown_DEX": {
        "stats": {"str": 1, "agi": 30, "vit": 50, "int": 50, "dex": 99, "luk": 1},
        "primary": ["DEX", "INT"], "secondary": ["AGI", "HIT"],
    },

    # ── DANCER ───────────────────────────────────────────────────────────────
    # AGI: Arrow Shower AoE + Slow Grace (ASPD inimigo -30%)
    "Dancer_AGI": {
        "stats": {"str": 10, "agi": 90, "vit": 30, "int": 1, "dex": 80, "luk": 1},
        "primary": ["AGI", "DEX"], "secondary": ["INT", "FLEE"],
    },

    # ── GYPSY ────────────────────────────────────────────────────────────────
    # AGI: Marionette Control — transfere metade dos stats base para aliado
    "Gypsy_AGI": {
        "stats": {"str": 10, "agi": 90, "vit": 40, "int": 1, "dex": 99, "luk": 1},
        "primary": ["AGI", "DEX"], "secondary": ["INT", "FLEE"],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# FROTA COMPLETA
# Formato: (bot_name, job_id, build_key, base_level, zeny)
# ─────────────────────────────────────────────────────────────────────────────
FLEET: list[tuple[str, int, str, int, int]] = [
    # ── CLASSES BASE ─────────────────────────────────────────────────────────
    ("HC_Novice01",    0, "Novice",               10,  5_000),
    ("HC_Swordman01",  1, "Swordman",             30,  20_000),
    ("HC_Mage01",      2, "Mage",                 30,  20_000),
    ("HC_Archer01",    3, "Archer",               30,  20_000),
    ("HC_Acolyte01",   4, "Acolyte",              30,  20_000),
    ("HC_Merchant01",  5, "Merchant",             40,  80_000),
    ("HC_Thief01",     6, "Thief",                30,  20_000),

    # ── KNIGHT ───────────────────────────────────────────────────────────────
    ("HC_Knight_STR01", 7, "Knight_STR",          70,  200_000),
    ("HC_Knight_AGI01", 7, "Knight_AGI",          68,  180_000),
    ("HC_Knight_VIT01", 7, "Knight_VIT",          72,  220_000),

    # ── LORD KNIGHT ──────────────────────────────────────────────────────────
    ("HC_LK_STR01",      23, "LordKnight_STR",      85,  500_000),
    ("HC_LK_AGI01",      23, "LordKnight_AGI",      83,  480_000),
    ("HC_LK_VIT01",      23, "LordKnight_VIT",      87,  550_000),
    ("HC_LK_Spiral01",   23, "LordKnight_Spiral",   84,  510_000),
    ("HC_LK_Mura01",     23, "LordKnight_Muramasa", 65,  320_000),

    # ── CRUSADER ─────────────────────────────────────────────────────────────
    ("HC_Crusader_VIT01",   14, "Crusader_VIT",   65,  150_000),
    ("HC_Crusader_Spear01", 14, "Crusader_Spear", 63,  140_000),

    # ── PALADIN ──────────────────────────────────────────────────────────────
    ("HC_Paladin_VIT01",  30, "Paladin_VIT",       82,  450_000),
    ("HC_Paladin_GC01",   30, "Paladin_GC",        80,  420_000),
    ("HC_Paladin_Dev01",  30, "Paladin_Devotion",  85,  460_000),

    # ── WIZARD ───────────────────────────────────────────────────────────────
    ("HC_Wizard_INT01",  9, "Wizard_INT",         68,  180_000),
    ("HC_Wizard_VIT01",  9, "Wizard_VIT",         66,  160_000),

    # ── HIGH WIZARD ──────────────────────────────────────────────────────────
    ("HC_HW_INT01",        25, "HighWizard_INT",        84,  500_000),
    ("HC_HW_VIT01",        25, "HighWizard_VIT",        82,  470_000),
    ("HC_HW_Soul01",       25, "HighWizard_Soul",       86,  520_000),
    ("HC_HW_FirePillar01", 25, "HighWizard_FirePillar", 83,  490_000),

    # ── PRIEST ───────────────────────────────────────────────────────────────
    ("HC_Priest_Supp01",  8, "Priest_Support",    72,  150_000),
    ("HC_Priest_Btl01",   8, "Priest_Battle",     68,  130_000),

    # ── HIGH PRIEST ──────────────────────────────────────────────────────────
    ("HC_HP_Supp01",    24, "HighPriest_Support", 86,  480_000),
    ("HC_HP_Btl01",     24, "HighPriest_Battle",  83,  450_000),
    ("HC_HP_TU01",      24, "HighPriest_TU",      85,  470_000),

    # ── HUNTER ───────────────────────────────────────────────────────────────
    ("HC_Hunter_DEX01", 11, "Hunter_DEX",         74,  200_000),
    ("HC_Hunter_AGI01", 11, "Hunter_AGI",         70,  180_000),

    # ── SNIPER ───────────────────────────────────────────────────────────────
    ("HC_Sniper_DEX01",    26, "Sniper_DEX",      85,  520_000),
    ("HC_Sniper_Falcon01", 26, "Sniper_Falcon",   83,  490_000),
    ("HC_Sniper_Trap01",   26, "Sniper_Trap",     84,  500_000),

    # ── ASSASSIN ─────────────────────────────────────────────────────────────
    ("HC_Assassin_AGI01", 12, "Assassin_AGI",     69,  170_000),
    ("HC_Assassin_SB01",  12, "Assassin_SB",      67,  160_000),

    # ── SIN X ────────────────────────────────────────────────────────────────
    ("HC_SinX_AGI01",      28, "SinX_AGI",        84,  520_000),
    ("HC_SinX_EDP01",      28, "SinX_EDP",        82,  500_000),
    ("HC_SinX_Grim01",     28, "SinX_Grimtooth",  83,  510_000),

    # ── MONK ─────────────────────────────────────────────────────────────────
    ("HC_Monk_Asura01", 15, "Monk_Asura",         70,  200_000),
    ("HC_Monk_AGI01",   15, "Monk_AGI",           67,  170_000),

    # ── CHAMPION ─────────────────────────────────────────────────────────────
    ("HC_Champ_Asura01", 31, "Champion_Asura",    85,  530_000),
    ("HC_Champ_Tiger01", 31, "Champion_Tiger",    82,  490_000),
    ("HC_Champ_Snap01",  31, "Champion_Snap",     84,  515_000),

    # ── BLACKSMITH ───────────────────────────────────────────────────────────
    ("HC_BS_STR01", 10, "Blacksmith_STR",         60,  300_000),
    ("HC_BS_WS01",  10, "Blacksmith_WS",          58,  280_000),

    # ── WHITESMITH ───────────────────────────────────────────────────────────
    ("HC_WS_STR01",    27, "Whitesmith_STR",      80,  600_000),
    ("HC_WS_Cart01",   27, "Whitesmith_Cart",     78,  560_000),
    ("HC_WS_MaxPow01", 27, "Whitesmith_MaxPow",   82,  620_000),

    # ── SAGE ─────────────────────────────────────────────────────────────────
    ("HC_Sage_INT01", 16, "Sage_INT",             64,  150_000),
    ("HC_Sage_DEX01", 16, "Sage_DEX",             62,  140_000),

    # ── PROFESSOR ────────────────────────────────────────────────────────────
    ("HC_Prof_INT01", 32, "Professor_INT",        82,  470_000),
    ("HC_Prof_VIT01", 32, "Professor_VIT",        80,  450_000),

    # ── ROGUE ────────────────────────────────────────────────────────────────
    ("HC_Rogue_AGI01", 17, "Rogue_AGI",           60,  140_000),
    ("HC_Rogue_STR01", 17, "Rogue_STR",           58,  130_000),

    # ── STALKER ──────────────────────────────────────────────────────────────
    ("HC_Stalker_AGI01",      33, "Stalker_AGI",      80,  430_000),
    ("HC_Stalker_Chase01",    33, "Stalker_Chase",    78,  410_000),
    ("HC_Stalker_Snatch01",   33, "Stalker_Snatcher", 79,  420_000),

    # ── ALCHEMIST ────────────────────────────────────────────────────────────
    ("HC_Alch_INT01", 18, "Alchemist_INT",        62,  180_000),
    ("HC_Alch_STR01", 18, "Alchemist_STR",        60,  160_000),

    # ── CREATOR ──────────────────────────────────────────────────────────────
    ("HC_Creator_INT01",  34, "Creator_INT",      82,  600_000),
    ("HC_Creator_VIT01",  34, "Creator_VIT",      80,  560_000),
    ("HC_Creator_FCP01",  34, "Creator_FCP",      84,  580_000),
    ("HC_Creator_Vani01", 34, "Creator_Vani",     78,  540_000),

    # ── BARD ─────────────────────────────────────────────────────────────────
    ("HC_Bard_DEX01",   19, "Bard_DEX",           62,  160_000),

    # ── CLOWN ────────────────────────────────────────────────────────────────
    ("HC_Clown_DEX01",  35, "Clown_DEX",          82,  480_000),

    # ── DANCER ───────────────────────────────────────────────────────────────
    ("HC_Dancer_AGI01", 20, "Dancer_AGI",         60,  150_000),

    # ── GYPSY ────────────────────────────────────────────────────────────────
    ("HC_Gypsy_AGI01",  36, "Gypsy_AGI",          80,  460_000),
]


# ─────────────────────────────────────────────────────────────────────────────
# Geração
# ─────────────────────────────────────────────────────────────────────────────

def _build_variant(build_key: str) -> str:
    parts = build_key.split("_", 1)
    return parts[1] if len(parts) == 2 else ""


def generate_profile(bot_name: str, job_id: int, build_key: str,
                     base_level: int = 1, zeny: int = 5_000) -> BotProfile:
    job_name  = JOB_ID.get(job_id, "Novice")
    build_def = BUILDS.get(build_key) or BUILDS.get(job_name) or BUILDS["Novice"]

    return BotProfile(
        name            = bot_name,
        job             = job_id,
        job_name        = job_name,
        base_level      = base_level,
        zeny            = zeny,
        primary_stats   = build_def["primary"],
        secondary_stats = build_def["secondary"],
        build           = _build_variant(build_key),
        current_equips  = {
            "EQI_HEAD_TOP": None, "EQI_HEAD_MID": None, "EQI_HEAD_LOW": None,
            "EQI_ARMOR":    None, "EQI_GARMENT":  None, "EQI_SHOES":    None,
            "EQI_HAND_R":   None, "EQI_HAND_L":   None,
            "EQI_ACC_L":    None, "EQI_ACC_R":    None,
        },
        in_combat   = False,
        current_map = "prontera",
    )


def generate_openkore_config(profile: BotProfile, build_key: str) -> str:
    build_def   = BUILDS.get(build_key) or BUILDS.get(profile.job_name) or BUILDS["Novice"]
    s           = build_def["stats"]
    is_merchant = profile.job_name in MERCHANT_JOBS

    stats_block = "\n".join([
        f"statsAddStr {s.get('str', 1)}",
        f"statsAddAgi {s.get('agi', 1)}",
        f"statsAddVit {s.get('vit', 1)}",
        f"statsAddInt {s.get('int', 1)}",
        f"statsAddDex {s.get('dex', 1)}",
        f"statsAddLuk {s.get('luk', 1)}",
    ])

    # Mapa de farm principal
    farm_maps    = get_farm_maps(profile.job_name, profile.build)
    lock_map     = farm_maps[0] if farm_maps else "prontera"

    # Itens para comprar (primeiros 6 para não poluir config)
    buy_items    = get_buy_items(profile.job_name, profile.build)
    buy_block    = "\n".join(
        f"buyAuto {item} 50" for item in buy_items[:6]
    ) if buy_items else ""

    # Cartas prioritárias para o motor de decisão (comentário informativo)
    cards        = get_card_priorities(profile.job_name, profile.build)
    card_comment = "# Cards prioritários: " + ", ".join(cards[:5]) if cards else ""

    vend_block = ""
    if is_merchant:
        vend_block = f"""
# Merchant: abrir vending shop no ponto de comércio
vendOn 1
vendTitle Shop [{profile.job_name}] items
"""

    return f"""# OpenKore config — {profile.name} | {profile.job_name} [{profile.build}] Lv{profile.base_level}

# Conexão
master Ragnarok Hardcore
char {profile.name}

# Sem teleporte (servidor Hardcore)
teleportAuto 0
attackAuto 2
attackAuto_inLockMap 2

# Mapa de farm principal
lockMap {lock_map}

# Stats target
{stats_block}

# Comportamento
sitAuto_hp 30
sitAuto_sp 20
itemsGatherAuto 2
itemsTakeAuto 2
itemsTakeAuto_start 1

# Compras automáticas (reabastecimento)
{buy_block}

{card_comment}
{vend_block}
# Plugins
loadPlugin MarketScanner
loadPlugin TradeHandler
loadPlugin PartyManager
"""


def create_bot(bot_name: str, job_id: int, build_key: str,
               base_level: int = 1, zeny: int = 5_000) -> BotProfile:
    profile = generate_profile(bot_name, job_id, build_key, base_level, zeny)
    profile.save()

    bot_dir = BOTS_DIR / bot_name
    bot_dir.mkdir(parents=True, exist_ok=True)
    (bot_dir / "macros").mkdir(exist_ok=True)

    (bot_dir / "config.txt").write_text(
        generate_openkore_config(profile, build_key), encoding="utf-8"
    )

    dynamic = bot_dir / "macros" / "dynamic.txt"
    if not dynamic.exists():
        dynamic.write_text("# comandos dinâmicos do orquestrador\n", encoding="utf-8")

    return profile


if __name__ == "__main__":
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    created = 0
    for (name, job_id, build_key, level, zeny) in FLEET:
        p = create_bot(name, job_id, build_key, level, zeny)
        job_label = f"{p.job_name}" + (f" [{p.build}]" if p.build else "")
        print(f"  {name:<26} {job_label:<30} Lv{level}")
        created += 1

    print(f"\n{created} bots criados em {PROFILES_DIR}")

"""
build_knowledge.py
Base de conhecimento por build: mapas de farm, consumíveis, itens para
comprar, vender e priorizar. Baseado em guias Pre-Renewal do RateMyServer,
iROWiki Classic, TalonRO Wiki e ROGGH.

Formato de cada entrada:
  farm_maps   → lista de mapas (interna rAthena) em ordem de prioridade
  hunt_mobs   → AegisNames de mobs prioritários
  buy_items   → AegisNames de itens que o bot DEVE comprar
  sell_items  → AegisNames de itens que o bot deve vender (drops/cards)
  equip_prio  → por slot EQI, lista de AegisNames preferidos (ordem de prioridade)
  card_prio   → cartas que o bot quer inserir em equipamentos (por slot)
  notes       → observações sobre a build
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONSUMÍVEIS UNIVERSAIS — todo bot carrega isso
# ─────────────────────────────────────────────────────────────────────────────
UNIVERSAL_CONSUMABLES = [
    "White_Potion",         # HP recovery
    "Blue_Potion",          # SP recovery
    "Awakening_Potion",     # ASPD +12, 3 min
    "Concentration_Potion", # HIT +20, 3 min
    "Fly_Wing",             # teleport
    "Butterfly_Wing",       # retornar à cidade
]

MELEE_DPS_CONSUMABLES = UNIVERSAL_CONSUMABLES + [
    "Berserk_Potion",       # ASPD +20 (apenas melee)
]

CASTER_CONSUMABLES = UNIVERSAL_CONSUMABLES + [
    "Yggdrasil_Berry",      # HP+SP full
]

WOE_CONSUMABLES = UNIVERSAL_CONSUMABLES + [
    "Yggdrasil_Berry",
    "Yggdrasil_Seed",       # HP+SP 50%
    "Speed_Potion",         # movimento
    "Berserk_Potion"
]

# ─────────────────────────────────────────────────────────────────────────────
# BASE DE CONHECIMENTO POR BUILD
# ─────────────────────────────────────────────────────────────────────────────
BUILD_KNOWLEDGE: dict[str, dict] = {

    # ── NOVICE / BASE ────────────────────────────────────────────────────────
    "Novice": {
        "farm_maps": ["new_1-1", "payon_cave01"],
        "hunt_mobs": ["Poring", "Fabre", "Lunatic"],
        "buy_items": UNIVERSAL_CONSUMABLES,
        "sell_items": ["Poring_Card", "Lunatic_Card", "Jellopy", "Fluff"],
        "equip_prio": {},
        "card_prio": [],
        "notes": "Fase transitória. Evoluir para 2ª classe o mais rápido possível.",
    },
    "Swordman": {
        "farm_maps": ["pay_dun01", "moc_ruins"],
        "hunt_mobs": ["Mummy", "Minorous", "Zombie"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["Mummy_Card", "Minorous_Card", "Horrendous_Mouth", "Rotten_Bandage"],
        "equip_prio": {"EQI_HAND_R": ["Katana_", "Katana"], "EQI_ARMOR": ["Chain_Mail_"]},
        "card_prio": ["Skel_Worker_Card", "Hydra_Card"],
        "notes": "Classe base. Priorizar chegar a Knight o mais rápido possível.",
    },
    "Mage": {
        "farm_maps": ["pay_dun01", "moc_ruins", "ant_hell01"],
        "hunt_mobs": ["Mummy", "Soldier_Skeleton", "Ant_Egg"],
        "buy_items": CASTER_CONSUMABLES,
        "sell_items": ["Mummy_Card", "Soldier_Skeleton_Card", "Cyfar", "Steel"],
        "equip_prio": {"EQI_HAND_R": ["Rod_", "Rod"]},
        "card_prio": ["Drops_Card", "Dokebi_Card"],
        "notes": "Acumular INT e DEX. Transição para Wizard.",
    },
    "Archer": {
        "farm_maps": ["pay_fild08", "gef_fild01", "mjolnir_05"],
        "hunt_mobs": ["Creamy", "Myst_Case", "Wormtail"],
        "buy_items": UNIVERSAL_CONSUMABLES + ["Arrow", "Silver_Arrow"],
        "sell_items": ["Creamy_Card", "Myst_Case_Card", "Cyfar"],
        "equip_prio": {"EQI_HAND_R": ["Composite_Bow_", "Kakkung_"]},
        "card_prio": ["Knight_Of_Abyss_Card"],
        "notes": "Classe base para Hunter/Sniper/Bard/Dancer.",
    },
    "Acolyte": {
        "farm_maps": ["pay_dun01", "gl_chyard"],
        "hunt_mobs": ["Zombie", "Skeleton", "Ghoul"],
        "buy_items": UNIVERSAL_CONSUMABLES + ["Blue_Gemstone", "Yellow_Gemstone"],
        "sell_items": ["Yoyo_Card", "Tarou_Card", "Holy_Water"],
        "equip_prio": {"EQI_HAND_R": ["Mace_", "Mace"]},
        "card_prio": ["Phen_Card"],
        "notes": "Produzir Holy Water para venda. Transição para Priest/Monk.",
    },
    "Merchant": {
        "farm_maps": ["orc_dun01", "pay_fild08"],
        "hunt_mobs": ["Orc_Warrior", "Orc_Lady", "Orc_Zombie"],
        "buy_items": UNIVERSAL_CONSUMABLES,
        "sell_items": ["Orcish_Axe", "Steel", "Orc_Warrior_Card", "Orc_Lady_Card"],
        "equip_prio": {"EQI_HAND_R": ["Battle_Axe_", "Two_Handed_Axe_"]},
        "card_prio": ["Zipper_Bear_Card"],
        "notes": "Classe comercial. Maximizar LUK para Lucky Blunder (critical).",
    },
    "Thief": {
        "farm_maps": ["gl_cul01", "gef_fild14", "orc_dun01"],
        "hunt_mobs": ["Thara_Frog", "Orc_Warrior", "Familiar"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["Thara_Frog_Card", "Orc_Warrior_Card", "Cyfar"],
        "equip_prio": {"EQI_HAND_R": ["Main_Gauche_", "Stiletto_"]},
        "card_prio": ["Side_Winder_Card", "Kobold_Card"],
        "notes": "Usar Steal para maximizar drops. Transição para Assassin/Rogue.",
    },

    # ── KNIGHT ───────────────────────────────────────────────────────────────
    "Knight_STR": {
        "farm_maps": ["orc_dun02", "gl_knt01", "gef_fild14"],
        "hunt_mobs": ["High_Orc", "Raydric", "Orc_Warrior"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Awakening_Potion", "Concentration_Potion"],
        "sell_items": ["Orcish_Axe", "Steel", "Daydric_Card", "Orc_Warrior_Card", "High_Orc_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Executioner_", "Claymore_", "Two_Hand_Sword_"],
            "EQI_ARMOR":  ["Plate_Armor_", "Chain_Mail_"],
            "EQI_GARMENT":["Muffler_"],
            "EQI_SHOES":  ["Boots_"],
            "EQI_ACC_L":  ["Glove_"],
            "EQI_ACC_R":  ["Glove_"],
        },
        "card_prio": ["Skel_Worker_Card", "Hydra_Card", "Daydric_Card", "Marc_Card", "Verit_Card"],
        "notes": "Bowling Bash com 2H Sword. Sage Endow Water para High Orcs. "
                 "STR 90, AGI 30, VIT 60, INT 1, DEX 50, LUK 1.",
    },
    "Knight_AGI": {
        "farm_maps": ["pay_dun04", "moc_ruins", "gl_knt01"],
        "hunt_mobs": ["Mummy", "Minorous", "Raydric"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["Mummy_Card", "Minorous_Card", "Daydric_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Muramasa", "Tsurugi_"],
            "EQI_HEAD_TOP":["Snake_Head"],
            "EQI_ARMOR":  ["Chain_Mail_"],
            "EQI_SHOES":  ["Boots_"],
        },
        "card_prio": ["Kobold_Card", "Skel_Worker_Card", "Verit_Card"],
        "notes": "Crit build. Muramasa (Crit+30) + Snake Head Hat (Double Attack). "
                 "STR 70, AGI 90, VIT 30, INT 1, DEX 30, LUK 30.",
    },
    "Knight_VIT": {
        "farm_maps": ["gl_knt01", "gl_cas01", "orc_dun02"],
        "hunt_mobs": ["Raydric", "Khalitzburg", "High_Orc"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["White_Potion"],
        "sell_items": ["Daydric_Card", "Khalitzburg_Card", "Orcish_Axe"],
        "equip_prio": {
            "EQI_HAND_R": ["Skewer", "Guisarme_"],
            "EQI_HAND_L": ["Shield_", "Buckler_"],
            "EQI_ARMOR":  ["Meteo_Plate_Armor"],
            "EQI_HEAD_TOP":["Helm_"],
        },
        "card_prio": ["Thara_Frog_Card", "Daydric_Card", "Marc_Card", "Verit_Card"],
        "notes": "Tank com lança. Pierce ignora DEF. 100 VIT total = imune a Stun. "
                 "STR 60, AGI 1, VIT 99, INT 20, DEX 50, LUK 1.",
    },

    # ── LORD KNIGHT ──────────────────────────────────────────────────────────
    "LordKnight_STR": {
        "farm_maps": ["orc_dun02", "gl_knt01", "gef_fild14", "tur_dun04"],
        "hunt_mobs": ["High_Orc", "Raydric", "Turtle_General"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Berserk_Potion"],
        "sell_items": ["Orcish_Axe", "Steel", "Daydric_Card", "Turtle_General_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Executioner_", "Claymore_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_GARMENT":["Wool_Scarf"],
            "EQI_SHOES":  ["Tidal_Shoes"],
            "EQI_HEAD_TOP":["Horn_Of_Lord_Kaho"],
        },
        "card_prio": ["Skel_Worker_Card", "Hydra_Card", "Daydric_Card", "Tao_Gunka_Card"],
        "notes": "Bowling Bash máximo. Tidal + Wool combo. "
                 "STR 95, AGI 30, VIT 80, INT 1, DEX 50, LUK 1.",
    },
    "LordKnight_AGI": {
        "farm_maps": ["gl_knt01", "gl_knt02", "orc_dun02"],
        "hunt_mobs": ["Raydric", "Khalitzburg", "High_Orc"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["Daydric_Card", "Khalitzburg_Card", "Executioner"],
        "equip_prio": {
            "EQI_HAND_R": ["Muramasa", "Tsurugi_"],
            "EQI_HEAD_TOP":["Snake_Head", "Horn_Of_Lord_Kaho"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_SHOES":  ["Tidal_Shoes"],
        },
        "card_prio": ["Kobold_Card", "Skel_Worker_Card", "Tao_Gunka_Card"],
        "notes": "Two-Hand Quicken + crit. STR 80, AGI 90, VIT 30, INT 1, DEX 30, LUK 30.",
    },
    "LordKnight_VIT": {
        "farm_maps": ["gl_knt02", "gl_cas01", "tur_dun04"],
        "hunt_mobs": ["Khalitzburg", "Raydric", "Turtle_General"],
        "buy_items": WOE_CONSUMABLES,
        "sell_items": ["Daydric_Card", "Khalitzburg_Card", "Turtle_General_Card"],
        "equip_prio": {
            "EQI_HAND_L": [ "Shield_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_GARMENT":["Wool_Scarf"],
            "EQI_SHOES":  ["Tidal_Shoes"],
        },
        "card_prio": ["Thara_Frog_Card", "Daydric_Card", "Tao_Gunka_Card", "Ghostring_Card"],
        "notes": "WoE tank. 100 VIT total obrigatório. 25k+ HP meta. "
                 "STR 80, AGI 1, VIT 99, INT 1, DEX 60, LUK 1.",
    },
    "LordKnight_Spiral": {
        "farm_maps": ["thor_v02", "tur_dun04", "gl_knt02"],
        "hunt_mobs": ["Turtle_General", "Khalitzburg", "Anolian"],
        "buy_items": WOE_CONSUMABLES,
        "sell_items": ["Turtle_General_Card", "Anolian_Card", "Steel"],
        "equip_prio": {
            "EQI_HAND_R": ["Skewer", "Gungnir"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_GARMENT":["Wool_Scarf"],
            "EQI_SHOES":  ["Tidal_Shoes"],
            "EQI_HEAD_TOP":["Horn_Of_Lord_Kaho"],
        },
        "card_prio": ["Thara_Frog_Card", "Daydric_Card", "Marc_Card", "Tao_Gunka_Card"],
        "notes": "Spiral Pierce: dano escala com PESO da lança, não STR. "
                 "Brocca ignora parte da DEF. Gungnir nunca erra. "
                 "STR deliberadamente baixo — cada ponto em VIT/DEX vale mais. "
                 "STR 30, AGI 40, VIT 90, INT 20, DEX 70, LUK 1.",
    },
    "LordKnight_Muramasa": {
        "farm_maps": ["pay_dun04", "gl_knt01", "orc_dun02"],
        "hunt_mobs": ["Mummy", "Wraith_Dead", "Raydric"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Berserk_Potion"],
        "sell_items": ["Mummy_Card", "Daydric_Card", "Lich_s_Bone_Wand"],
        "equip_prio": {
            "EQI_HAND_R": ["Muramasa"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_SHOES":  ["Tidal_Shoes"],
        },
        "card_prio": ["Kobold_Card", "Skel_Worker_Card", "Verit_Card"],
        "notes": "LUK = BaseLV+1 garante imunidade total à Maldição do Muramasa. "
                 "Two-Hand Quicken + Berserk Potion = 184 ASPD com apenas DEX 14. "
                 "STR 90, AGI 99, VIT 10, INT 1, DEX 14, LUK 66.",
    },

    # ── CRUSADER ─────────────────────────────────────────────────────────────
    "Crusader_VIT": {
        "farm_maps": ["gef_fild14", "gl_knt01", "pay_dun04"],
        "hunt_mobs": ["High_Orc", "Raydric", "Mummy"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["High_Orc_Card", "Daydric_Card", "Orcish_Axe"],
        "equip_prio": {
            "EQI_HAND_L": ["Stone_Buckler", "Shield_"],
            "EQI_ARMOR":  ["Full_Plate_Armor_"],
            "EQI_HEAD_TOP":["Helm_"],
        },
        "card_prio": ["Thara_Frog_Card", "Daydric_Card"],
        "notes": "Shield Chain. Dano escala com peso do escudo — refinar o escudo. "
                 "STR 80, AGI 1, VIT 80, INT 30, DEX 60, LUK 1.",
    },
    "Crusader_Spear": {
        "farm_maps": ["gl_chyard", "gl_prison", "pay_dun04"],
        "hunt_mobs": ["Wraith", "Evil_Druid", "Mummy"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["Evil_Druid_Card", "Wraith_Card", "Fabric"],
        "equip_prio": {
            "EQI_HAND_R": ["Lance_", "Glaive_"],
            "EQI_ARMOR":  ["Full_Plate_Armor_"],
        },
        "card_prio": ["Skel_Worker_Card", "Hydra_Card"],
        "notes": "Holy Cross com 2H Spear duplica os hits. Excelente vs Undead/Demon. "
                 "STR 60, AGI 40, VIT 60, INT 10, DEX 60, LUK 1.",
    },

    # ── PALADIN ──────────────────────────────────────────────────────────────
    "Paladin_VIT": {
        "farm_maps": ["gl_knt02", "abbey02", "gl_cas01"],
        "hunt_mobs": ["Khalitzburg", "Necromancer", "Raydric"],
        "buy_items": WOE_CONSUMABLES,
        "sell_items": ["Khalitzburg_Card", "Necromancer_Card", "Corrupted_Monk_Card"],
        "equip_prio": {
            "EQI_HAND_L": ["Shield_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_GARMENT":["Wool_Scarf"],
            "EQI_SHOES":  ["Tidal_Shoes"],
        },
        "card_prio": ["Thara_Frog_Card", "Ghostring_Card", "Tao_Gunka_Card"],
        "notes": "Sacrifice usa HP como dano fixo ignorando DEF. Full VIT para HP pool. "
                 "STR 25, AGI 1, VIT 99, INT 25, DEX 99, LUK 1.",
    },
    "Paladin_GC": {
        "farm_maps": ["gl_chyard", "abbey01", "gl_prison"],
        "hunt_mobs": ["Wraith", "Evil_Druid", "Lude", "Banshee"],
        "buy_items": CASTER_CONSUMABLES + ["Blue_Potion", "Blue_Gemstone"],
        "sell_items": ["Evil_Druid_Card", "Wraith_Card", "Fabric", "Necromancer_Card"],
        "equip_prio": {
            "EQI_HEAD_TOP": ["Horn_Of_Lord_Kaho", "Valkyrie_Helmet"],
            "EQI_ACC_L": ["Medal_Swordman", "Vesper_Core01"],
            "EQI_ARMOR":    ["Full_Plate_Armor_"],
        },
        "card_prio": ["Skel_Worker_Card", "Evil_Druid_Card", "Marc_Card"],
        "notes": "Grand Cross dano Holy. Imperial Feather + Ring: +1% GC dmg/base level. "
                 "Consome ~200 Blue Potions por sessão. "
                 "STR 53, AGI 9, VIT 63, INT 99, DEX 37, LUK 1.",
    },
    "Paladin_Devotion": {
        "farm_maps": ["gl_knt02", "gl_cas01", "prontera"],
        "hunt_mobs": ["Khalitzburg", "Raydric", "Abysmal_Knight"],
        "buy_items": WOE_CONSUMABLES + ["Blue_Gemstone"],
        "sell_items": ["Khalitzburg_Card", "Daydric_Card", "Steel"],
        "equip_prio": {
            "EQI_HAND_L": ["Valkyrja's_Shield"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_GARMENT":["Wool_Scarf"],
            "EQI_SHOES":  ["Tidal_Shoes"],
            "EQI_ACC_L":  ["Rosary_", "Orleans_Glove"],
        },
        "card_prio": ["Thara_Frog_Card", "Hodremlin_Card", "Ghostring_Card", "Tao_Gunka_Card"],
        "notes": "WoE support puro. Devotion desvia até 30% do dano do aliado para o Paladin. "
                 "DEX 99 para recast instantâneo. Sacrifica dano para proteger Breaker/Professor. "
                 "STR 30, AGI 10, VIT 99, INT 15, DEX 99, LUK 1.",
    },

    # ── WIZARD ───────────────────────────────────────────────────────────────
    "Wizard_INT": {
        "farm_maps": ["orc_dun02", "gl_knt02", "gefenia01"],
        "hunt_mobs": ["High_Orc", "Raydric_Archer", "Demon_Pungus"],
        "buy_items": CASTER_CONSUMABLES + ["Blue_Gemstone"],
        "sell_items": ["High_Orc_Card", "Raydric_Archer_Card", "Steel", "Orcish_Axe"],
        "equip_prio": {
            "EQI_HAND_R": ["Survival_Rod_", "Rod_"],
            "EQI_ACC_L":  ["Orleans_Glove"],
            "EQI_ACC_R":  ["Orleans_Glove"],
        },
        "card_prio": ["Drops_Card", "Dokebi_Card", "Horong_Card"],
        "notes": "Storm Gust principal. Survivor's Rod[2] + 2x Drops Card (INT+2 cada). "
                 "150 DEX total = cast instantâneo com Soul Link. "
                 "STR 1, AGI 1, VIT 20, INT 99, DEX 50, LUK 1.",
    },
    "Wizard_VIT": {
        "farm_maps": ["orc_dun02", "pay_dun03", "moc_fild22"],
        "hunt_mobs": ["High_Orc", "Mummy", "Zombie_Master"],
        "buy_items": CASTER_CONSUMABLES,
        "sell_items": ["High_Orc_Card", "Mummy_Card", "Orcish_Axe"],
        "equip_prio": {
            "EQI_HAND_R": ["Survival_Rod_"],
            "EQI_ARMOR":  ["Robe_Of_Casting_"],
        },
        "card_prio": ["Drops_Card", "Tao_Gunka_Card"],
        "notes": "Versão com mais VIT para sobrevivência em mapas densos. "
                 "STR 1, AGI 1, VIT 30, INT 99, DEX 60, LUK 1.",
    },

    # ── HIGH WIZARD ──────────────────────────────────────────────────────────
    "HighWizard_INT": {
        "farm_maps": ["thor_v01", "thor_v02", "gl_knt02", "mag_dun02"],
        "hunt_mobs": ["Kasa", "Salamander", "Abysmal_Knight"],
        "buy_items": CASTER_CONSUMABLES + ["Yggdrasil_Berry"],
        "sell_items": ["Kasa_Card", "Salamander_Card", "Knight_Of_Abyss_Card", "Lava_Flower"],
        "equip_prio": {
            "EQI_HAND_R": ["Lich_Bone_Wand", "Survival_Rod_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_ACC_L":  ["Orleans_Glove"],
            "EQI_ACC_R":  ["Orleans_Glove"],
        },
        "card_prio": ["Drops_Card", "Dokebi_Card", "Tao_Gunka_Card"],
        "notes": "Mystical Amplification +50% no próximo hit mágico. "
                 "Usar Pasana Armor em thor_v para imunidade a Fire. "
                 "STR 1, AGI 1, VIT 30, INT 99, DEX 80, LUK 1.",
    },
    "HighWizard_VIT": {
        "farm_maps": ["thor_v01", "thor_v02", "abbey02"],
        "hunt_mobs": ["Kasa", "Banshee", "Necromancer"],
        "buy_items": CASTER_CONSUMABLES,
        "sell_items": ["Kasa_Card", "Necromancer_Card", "Lava_Flower"],
        "equip_prio": {
            "EQI_HAND_R": ["Lich_Bone_Wand"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
        },
        "card_prio": ["Drops_Card", "Tao_Gunka_Card", "Ghostring_Card"],
        "notes": "Versão com mais VIT. Meteor Storm para WoE. "
                 "STR 1, AGI 1, VIT 40, INT 99, DEX 70, LUK 1.",
    },
    "HighWizard_Soul": {
        "farm_maps": ["thor_v02", "mag_dun02", "lhz_dun02"],
        "hunt_mobs": ["Kasa", "Salamander", "Venatu"],
        "buy_items": CASTER_CONSUMABLES + ["Yggdrasil_Berry"],
        "sell_items": ["Kasa_Card", "Salamander_Card", "Lava_Flower", "Cursed_Water"],
        "equip_prio": {
            "EQI_HAND_R": ["Lich_Bone_Wand", "Survival_Rod_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_ACC_L":  ["Orleans_Glove"],
            "EQI_ACC_R":  ["Orleans_Glove"],
        },
        "card_prio": ["Drops_Card", "Dokebi_Card", "Tao_Gunka_Card"],
        "notes": "Depende de Soul Link de Soul Linker parceiro para cast instantâneo. "
                 "Sem Soul Link o HW não consegue atuar. Storm Gust mais poderoso do jogo. "
                 "INT 99 sem investimento em DEX — todo ponto vai em INT. "
                 "STR 1, AGI 1, VIT 30, INT 99, DEX 30, LUK 1.",
    },
    "HighWizard_FirePillar": {
        "farm_maps": ["gl_cas01", "gl_cas02", "thor_v01"],
        "hunt_mobs": ["Abysmal_Knight", "Khalitzburg", "Kasa"],
        "buy_items": CASTER_CONSUMABLES + ["Blue_Gemstone", "Red_Gemstone"],
        "sell_items": ["Knight_Of_Abyss_Card", "Lava_Flower", "Coal"],
        "equip_prio": {
            "EQI_HAND_R": ["Lich_Bone_Wand"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_HEAD_TOP": ["Horn_Of_Lord_Kaho", "Wit_Pumpkin_Hat"],
        },
        "card_prio": ["Drops_Card", "Tao_Gunka_Card"],
        "notes": "Fire Pillar Lv10: 12 hits de (50+MATK/5) em 3×3 quando pisado. "
                 "Combina com Quagmire para imobilizar inimigos nos pilares. "
                 "DEX baixo intencional — playstyle de controle de área, não spam. "
                 "STR 1, AGI 1, VIT 50, INT 99, DEX 30, LUK 1.",
    },

    # ── PRIEST ───────────────────────────────────────────────────────────────
    "Priest_Support": {
        "farm_maps": ["gl_chyard", "gl_prison", "abbey01"],
        "hunt_mobs": ["Wraith", "Evil_Druid", "Ghoul"],
        "buy_items": CASTER_CONSUMABLES + ["Blue_Gemstone", "Yellow_Gemstone"],
        "sell_items": ["Holy_Water", "Evil_Druid_Card", "Wraith_Card", "Fabric"],
        "equip_prio": {
            "EQI_HAND_R": [ "Mace_"],
            "EQI_ACC_L":  ["Rosary_"],
            "EQI_ACC_R":  ["Rosary_"],
        },
        "card_prio": ["Sting_Card", "Phen_Card"],
        "notes": "Rosary[1] + Spiritual Ring combo: Heal +5%, MATK +5%. "
                 "Staff of Recovery: Heal +10%. Vender Holy Water. "
                 "STR 1, AGI 1, VIT 60, INT 80, DEX 50, LUK 1.",
    },
    "Priest_Battle": {
        "farm_maps": ["gl_chyard", "gl_prison", "abbey01"],
        "hunt_mobs": ["Wraith", "Evil_Druid", "Necromancer"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Blue_Gemstone"],
        "sell_items": ["Evil_Druid_Card", "Necromancer_Card", "Fabric", "Oridecon"],
        "equip_prio": {
            "EQI_HAND_R": ["Mace_", "Mace"],
            "EQI_ACC_L":  ["Rosary_"],
        },
        "card_prio": ["Sting_Card", "Hydra_Card"],
        "notes": "Magnus Exorcismus: Rosary[1] + Sting Card = +30% ME dano. "
                 "STR 40, AGI 1, VIT 60, INT 80, DEX 70, LUK 1.",
    },

    # ── HIGH PRIEST ──────────────────────────────────────────────────────────
    "HighPriest_Support": {
        "farm_maps": ["abbey02", "abbey03", "gl_chyard"],
        "hunt_mobs": ["Necromancer", "Banshee", "Evil_Druid"],
        "buy_items": CASTER_CONSUMABLES + ["Blue_Gemstone", "Yellow_Gemstone"],
        "sell_items": ["Holy_Water", "Necromancer_Card", "Corrupted_Monk_Card"],
        "equip_prio": {
            "EQI_HAND_R": [ "Divine_Cross"],
            "EQI_ACC_L":  ["Rosary_"],
            "EQI_ACC_R":  ["Rosary_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
        },
        "card_prio": ["Sting_Card", "Phen_Card", "Tao_Gunka_Card"],
        "notes": "Meditatio 10: +2% Heal/nível. Assumptio: DEF +50%. "
                 "STR 1, AGI 1, VIT 60, INT 90, DEX 60, LUK 1.",
    },
    "HighPriest_Battle": {
        "farm_maps": ["abbey02", "gl_chyard", "gl_prison"],
        "hunt_mobs": ["Necromancer", "Necromancer", "Wraith"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Blue_Gemstone"],
        "sell_items": ["Corrupted_Monk_Card", "Necromancer_Card", "Evil_Druid_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Mace_"],
            "EQI_ACC_L":  ["Rosary_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
        },
        "card_prio": ["Sting_Card", "Hydra_Card", "Tao_Gunka_Card"],
        "notes": "Magnus + Assumptio. STR 30, AGI 1, VIT 60, INT 90, DEX 70, LUK 1.",
    },
    "HighPriest_TU": {
        "farm_maps": ["gl_chyard", "gl_prison", "abbey01", "moc_pryd06"],
        "hunt_mobs": ["Wraith", "Evil_Druid", "Wraith_Dead", "Ghoul", "Zombie_Master"],
        "buy_items": CASTER_CONSUMABLES + ["Blue_Gemstone", "Yellow_Gemstone"],
        "sell_items": ["Evil_Druid_Card", "Wraith_Card", "Lich_s_Bone_Wand", "Fabric"],
        "equip_prio": {
            "EQI_HAND_R": ["Lich_Bone_Wand", "Rod_"],
            "EQI_ACC_L":  ["Rosary_"],
            "EQI_ACC_R":  ["Rosary_"],
            "EQI_HEAD_MID": ["Crown_Of_Deceit", "Wings_Of_Victory"],
        },
        "card_prio": ["Drops_Card", "Imp_Card", "Zerom_Card"],
        "notes": "Turn Undead: fórmula usa INT/10 + LUK/10 + BaseLV/10 + (1-HP%)×200. "
                 "Gloria (+30 LUK) antes de TU = +3% chance adicional. "
                 "LUK 40 base: parece desperdício mas contribui diretamente ao hit rate de TU. "
                 "Farm solo em Glast Heim. STR 1, AGI 1, VIT 60, INT 99, DEX 60, LUK 40.",
    },

    # ── HUNTER ───────────────────────────────────────────────────────────────
    "Hunter_DEX": {
        "farm_maps": ["gl_knt01", "gl_knt02", "orc_dun02", "tur_dun04"],
        "hunt_mobs": ["Raydric", "Khalitzburg", "High_Orc", "Turtle_General"],
        "buy_items": UNIVERSAL_CONSUMABLES + ["Silver_Arrow", "Holy_Arrow", "Fire_Arrow"],
        "sell_items": ["Daydric_Card", "Khalitzburg_Card", "Turtle_General_Card", "High_Orc_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Composite_Bow_", "Kakkung_"],
            "EQI_ARMOR":  ["Sniping_Suit"],
        },
        "card_prio": ["Knight_Of_Abyss_Card", "Skel_Worker_Card", "Hydra_Card", "Gloom_Under_Night_Card"],
        "notes": "Double Strafe principal. Composite Bow[4]: 3x Abysmal Knight + Skel Worker. "
                 "Mudar flechas por elemento do mob. STR 10, AGI 75, VIT 30, INT 1, DEX 99, LUK 1.",
    },
    "Hunter_AGI": {
        "farm_maps": ["moc_ruins", "yuno_fild07", "lhz_dun02"],
        "hunt_mobs": ["Minorous", "Golem", "Venatu"],
        "buy_items": UNIVERSAL_CONSUMABLES + ["Silver_Arrow"],
        "sell_items": ["Minorous_Card", "Dolomedes_Card", "Steel"],
        "equip_prio": {
            "EQI_HAND_R": ["Composite_Bow_"],
            "EQI_SHOES":  ["Boots_"],
        },
        "card_prio": ["Kobold_Card", "Phreeoni_Card"],
        "notes": "Auto-Blitz. Chance Blitz = (AGI + LUK) / 10%. Falcon ATK = INT × 5. "
                 "STR 1, AGI 90, VIT 20, INT 30, DEX 40, LUK 90.",
    },

    # ── SNIPER ───────────────────────────────────────────────────────────────
    "Sniper_DEX": {
        "farm_maps": ["tur_dun04", "gl_knt02", "abbey02", "thor_v03"],
        "hunt_mobs": ["Turtle_General", "Abysmal_Knight", "Necromancer", "Salamander"],
        "buy_items": UNIVERSAL_CONSUMABLES + ["Silver_Arrow", "Holy_Arrow", "Fire_Arrow", "Wind_Arrow"],
        "sell_items": ["Turtle_General_Card", "Knight_Of_Abyss_Card", "Salamander_Card", "Kasa_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Composite_Bow_", "Orc_Archer_Bow"],
            "EQI_ARMOR":  ["Sniping_Suit"],
            "EQI_SHOES":  ["Tidal_Shoes"],
            "EQI_GARMENT":["Wool_Scarf"],
        },
        "card_prio": ["Knight_Of_Abyss_Card", "Skel_Worker_Card", "Hydra_Card", "Gloom_Under_Night_Card"],
        "notes": "Sharp Shooting + True Sight (ATK+20, HIT+10). "
                 "Orc Archer Bow + 2x Hydra = excelente vs demi-humano. "
                 "STR 10, AGI 75, VIT 50, INT 10, DEX 99, LUK 1.",
    },
    "Sniper_Falcon": {
        "farm_maps": ["lhz_dun02", "lhz_dun03", "yuno_fild07"],
        "hunt_mobs": ["Venatu", "Bloody_Knight", "Metaling"],
        "buy_items": UNIVERSAL_CONSUMABLES + ["Silver_Arrow"],
        "sell_items": ["Dolomedes_Card", "Bloody_Knight_Card", "Blue_Feather"],
        "equip_prio": {
            "EQI_HAND_R": ["Composite_Bow_"],
            "EQI_ARMOR":  ["Sniping_Suit"],
        },
        "card_prio": ["Phreeoni_Card", "Kobold_Card"],
        "notes": "True Sight 10 + Wind Walk 10. STR 1, AGI 99, VIT 20, INT 30, DEX 40, LUK 80.",
    },
    "Sniper_Trap": {
        "farm_maps": ["gl_cas01", "gl_cas02", "lhz_dun02"],
        "hunt_mobs": ["Abysmal_Knight", "Khalitzburg", "Venatu"],
        "buy_items": UNIVERSAL_CONSUMABLES + ["Blue_Potion"],
        "sell_items": ["Knight_Of_Abyss_Card", "Khalitzburg_Card", "Dolomedes_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Composite_Bow_"],
            "EQI_ARMOR":  ["Sniping_Suit"],
            "EQI_ACC_L":  ["Orleans_Glove"],
        },
        "card_prio": ["Drops_Card", "Zerom_Card", "Verit_Card"],
        "notes": "Dano de armadilha = (DEX + INT) × fator — NÃO usa ATK. "
                 "Ankle Snare imobiliza. Claymore Trap empilhada = burst massivo. "
                 "INT 80 atinge checkpoint ×(1+80/35) — grande spike de dano. "
                 "STR/AGI = 1, tudo em INT e VIT. Joga como controle de área. "
                 "STR 1, AGI 1, VIT 65, INT 80, DEX 99, LUK 1.",
    },

    # ── ASSASSIN ─────────────────────────────────────────────────────────────
    "Assassin_AGI": {
        "farm_maps": ["gef_fild14", "gl_knt01", "orc_dun02"],
        "hunt_mobs": ["High_Orc", "Raydric", "Orc_Warrior"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["High_Orc_Card", "Daydric_Card", "Orc_Warrior_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Infiltrator", "Jamadhar_"],
        },
        "card_prio": ["Kobold_Card", "Skel_Worker_Card", "Phreeoni_Card"],
        "notes": "Katar duplica crítico automaticamente. Infiltrator (AGI+5, STR+1). "
                 "STR 60, AGI 90, VIT 20, INT 1, DEX 30, LUK 30.",
    },
    "Assassin_SB": {
        "farm_maps": ["gl_knt01", "orc_dun02", "pay_dun04"],
        "hunt_mobs": ["Raydric", "High_Orc", "Mummy"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Poison_Bottle"],
        "sell_items": ["Daydric_Card", "High_Orc_Card", "Mummy_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Jamadhar_", "Blade_"],
        },
        "card_prio": ["Skel_Worker_Card", "Hydra_Card"],
        "notes": "Sonic Blow = 800% ATK em 8 hits. EDP multiplica ~3.2x. "
                 "Skel Worker melhor que Hydra quando STR > 88. "
                 "STR 90, AGI 40, VIT 40, INT 1, DEX 60, LUK 1.",
    },

    # ── ASSASSIN CROSS ───────────────────────────────────────────────────────
    "SinX_AGI": {
        "farm_maps": ["thor_v01", "gl_knt02", "abbey02"],
        "hunt_mobs": ["Kasa", "Abysmal_Knight", "Necromancer"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Poison_Bottle"],
        "sell_items": ["Kasa_Card", "Knight_Of_Abyss_Card", "Lava_Flower"],
        "equip_prio": {
            "EQI_HAND_R": ["Jamadhar_", "Infiltrator"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_SHOES":  ["Tidal_Shoes"],
        },
        "card_prio": ["Kobold_Card", "Skel_Worker_Card", "Tao_Gunka_Card"],
        "notes": "Grimtooth WoE. AGI+EDP para cloaked burst. "
                 "STR 90, AGI 80, VIT 30, INT 1, DEX 50, LUK 1.",
    },
    "SinX_EDP": {
        "farm_maps": ["thor_v01", "thor_v02", "lhz_dun03"],
        "hunt_mobs": ["Kasa", "Salamander", "Bloody_Knight"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Poison_Bottle"],
        "sell_items": ["Kasa_Card", "Salamander_Card", "Bloody_Knight_Card", "Lava_Flower"],
        "equip_prio": {
            "EQI_HAND_R": ["Jamadhar_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
        },
        "card_prio": ["Skel_Worker_Card", "Hydra_Card", "Tao_Gunka_Card"],
        "notes": "EDP multiplica Sonic Blow. Sem crit com EDP — usar Skel+Hydra. "
                 "STR 99, AGI 70, VIT 30, INT 1, DEX 50, LUK 1.",
    },
    "SinX_Grimtooth": {
        "farm_maps": ["gl_cas01", "gl_cas02", "prontera"],
        "hunt_mobs": ["Abysmal_Knight", "Khalitzburg", "Raydric"],
        "buy_items": WOE_CONSUMABLES + ["Poison_Bottle", "Cursed_Water"],
        "sell_items": ["Knight_Of_Abyss_Card", "Khalitzburg_Card", "Daydric_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Katar_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_GARMENT":["Muffler_"],
        },
        "card_prio": ["Frilldora_Card", "Kobold_Card", "Skel_Worker_Card", "Tao_Gunka_Card"],
        "notes": "WoE disruptor: Grimtooth Lv5 = 200% ATK em 3×3 splash de 6 cells enquanto cloaked. "
                 "Inimigos não podem retaliar pois não veem o SinX. "
                 "VIT 15 intencional — depende de nunca ser alvo. "
                 "Frilldora Card essencial (Cloaking). EDP + Grimtooth = devastador. "
                 "STR 75, AGI 85, VIT 15, INT 10, DEX 75, LUK 45.",
    },

    # ── MONK ─────────────────────────────────────────────────────────────────
    "Monk_Asura": {
        "farm_maps": ["abbey02", "thor_v02", "lhz_dun02"],
        "hunt_mobs": ["Necromancer", "Kasa", "Venatu"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Blue_Potion"],
        "sell_items": ["Corrupted_Monk_Card", "Kasa_Card", "Blue_Feather"],
        "equip_prio": {
            "EQI_HAND_R": [ "Mace_"],
            "EQI_ARMOR":  ["Diabolus_Robe"],
            "EQI_SHOES":  ["Variant_Shoes"],
        },
        "card_prio": ["Skel_Worker_Card", "Hydra_Card", "Tao_Gunka_Card"],
        "notes": "Guillotine Fist. SP cap para Asura ≈ 6000. "
                 "Diabolus Robe: INT+2, MATK+3%, SP+150. Variant Shoes: HP+400, SP+120. "
                 "STR 100, AGI 20, VIT 40, INT 90, DEX 70, LUK 1.",
    },
    "Monk_AGI": {
        "farm_maps": ["gl_knt01", "orc_dun02", "pay_dun04"],
        "hunt_mobs": ["Raydric", "High_Orc", "Mummy"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["Daydric_Card", "High_Orc_Card", "Mummy_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Waghnakh_"],
        },
        "card_prio": ["Skel_Worker_Card", "Strouf_Card", "Hydra_Card"],
        "notes": "Raging Trifecta > Quadruple > Thrust > Tiger Knuckle combo. "
                 "Waghnak[3]: Skel Worker + Hydra + Strouf. "
                 "STR 80, AGI 80, VIT 30, INT 20, DEX 50, LUK 1.",
    },

    # ── CHAMPION ─────────────────────────────────────────────────────────────
    "Champion_Asura": {
        "farm_maps": ["abbey02", "abbey03", "thor_v02", "lhz_dun03"],
        "hunt_mobs": ["Necromancer", "Banshee", "Kasa", "Bloody_Knight"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Blue_Potion"],
        "sell_items": ["Corrupted_Monk_Card", "Necromancer_Card", "Kasa_Card", "Bloody_Knight_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Combo_Battle_Glove", "Horn_Of_Hilthrion", "Waghnakh_"],
            "EQI_ARMOR":  ["Diabolus_Robe"],
            "EQI_ACC_L":  ["Diabolus_Ring"],
            "EQI_ACC_R":  ["Diabolus_Ring"],
            "EQI_SHOES":  ["Variant_Shoes"],
        },
        "card_prio": ["Skel_Worker_Card", "Hydra_Card", "Tao_Gunka_Card"],
        "notes": "Snap + Guillotine Fist burst. Zen regenera esferas instantaneamente. "
                 "Diabolus set: Mace + Robe + Ring x2. "
                 "STR 110, AGI 20, VIT 40, INT 90, DEX 70, LUK 1.",
    },
    "Champion_Tiger": {
        "farm_maps": ["gl_knt02", "orc_dun02", "thor_v01"],
        "hunt_mobs": ["Raydric", "High_Orc", "Kasa"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["Daydric_Card", "High_Orc_Card", "Kasa_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Waghnakh_", "Knuckle_Duster_"],
        },
        "card_prio": ["Skel_Worker_Card", "Hydra_Card"],
        "notes": "Tiger Knuckle Fist + Body Relocation para mobilidade. "
                 "ASPD alto = Trifecta combos mais rápidos. "
                 "STR 90, AGI 80, VIT 40, INT 1, DEX 50, LUK 1.",
    },
    "Champion_Snap": {
        "farm_maps": ["abbey02", "abbey03", "lhz_dun03"],
        "hunt_mobs": ["Necromancer", "Banshee", "Bloody_Knight"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Blue_Potion"],
        "sell_items": ["Corrupted_Monk_Card", "Necromancer_Card", "Bloody_Knight_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Horn_Of_Hilthrion"],
            "EQI_ARMOR":  ["Diabolus_Robe"],
            "EQI_ACC_L":  ["Diabolus_Ring"],
            "EQI_SHOES":  ["Variant_Shoes"],
        },
        "card_prio": ["Skel_Worker_Card", "Hydra_Card", "Tao_Gunka_Card"],
        "notes": "INT alto (~90) aumenta SP máximo → Asura mais forte mesmo sem SP cheio. "
                 "Snap para mobilidade — fecha distância sem cast time de movimentação. "
                 "Output mais estável que Asura puro (menos dependente de SP total). "
                 "STR 90, AGI 10, VIT 70, INT 90, DEX 50, LUK 1.",
    },

    # ── BLACKSMITH ───────────────────────────────────────────────────────────
    "Blacksmith_STR": {
        "farm_maps": ["orc_dun02", "gef_fild14", "tur_dun04"],
        "hunt_mobs": ["High_Orc", "Orc_Warrior", "Turtle_General"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["Orcish_Axe", "Steel", "Oridecon", "Elunium", "Turtle_Shell", "Turtle_General_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Battle_Axe_", "Two_Handed_Axe_"],
        },
        "card_prio": ["Orc_Lady_Card", "Hydra_Card", "Vadon_Card"],
        "notes": "Mammonite = 600% ATK Lv10, custa 1000z/uso. "
                 "Battle Axe[4]: 2x Orc Lady + Hydra + Vadon = OHKO High Orcs. "
                 "Sage Endow Water no grupo. STR 99, AGI 40, VIT 40, INT 1, DEX 40, LUK 1.",
    },
    "Blacksmith_WS": {
        "farm_maps": ["orc_dun01", "pay_fild08", "mjolnir_05"],
        "hunt_mobs": ["Orc_Warrior", "Wormtail", "Steel_Chonchon"],
        "buy_items": UNIVERSAL_CONSUMABLES + ["Iron", "Coal", "Steel", "Oridecon"],
        "sell_items": ["Forged_weapons", "Steel", "Oridecon", "Elunium"],
        "equip_prio": {
            "EQI_HAND_R": ["Giant_Axe", "Hurricane_Fury"],
        },
        "card_prio": ["Kobold_Card", "Phreeoni_Card"],
        "notes": "Weapon Perfection + forja de armas raras (3 slots). "
                 "LUK 50 melhora chance de forja rara. Receita de lucro: forge + vend. "
                 "STR 50, AGI 1, VIT 30, INT 30, DEX 99, LUK 50.",
    },

    # ── WHITESMITH ───────────────────────────────────────────────────────────
    "Whitesmith_STR": {
        "farm_maps": ["thor_v01", "thor_v02", "gl_knt02", "abbey02"],
        "hunt_mobs": ["Kasa", "Abysmal_Knight", "Necromancer"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["Kasa_Card", "Knight_Of_Abyss_Card", "Lava_Flower", "Corrupted_Monk_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Giant_Axe", "Two_Handed_Axe_"],
        },
        "card_prio": ["Zipper_Bear_Card", "Andre_Card", "Porcellio_Card"],
        "notes": "Cart Termination. CT NÃO escala com % cards — usar ATK flat: "
                 "Zipper Bear, Andre, Porcelio. Giant Axe: +15% CT se STR/VIT ok. "
                 "CART NO PESO MÁXIMO = dano máximo. "
                 "STR 99, AGI 50, VIT 50, INT 1, DEX 50, LUK 1.",
    },
    "Whitesmith_Cart": {
        "farm_maps": ["orc_dun02", "gef_fild14", "thor_v01"],
        "hunt_mobs": ["High_Orc", "Orc_Warrior", "Kasa"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["Orcish_Axe", "Steel", "Kasa_Card", "Oridecon"],
        "equip_prio": {
            "EQI_HAND_R": ["Battle_Axe_", "Giant_Axe"],
        },
        "card_prio": ["Orc_Lady_Card", "Hydra_Card", "Zipper_Bear_Card"],
        "notes": "Cart Revolution AoE + Mammonite para bosses. "
                 "STR 90, AGI 40, VIT 50, INT 1, DEX 40, LUK 1.",
    },
    "Whitesmith_MaxPow": {
        "farm_maps": ["thor_v02", "tur_dun04", "lhz_dun02"],
        "hunt_mobs": ["Salamander", "Turtle_General", "Venatu"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Awakening_Potion", "Berserk_Potion"],
        "sell_items": ["Salamander_Card", "Turtle_General_Card", "Dolomedes_Card", "Lava_Flower"],
        "equip_prio": {
            "EQI_HAND_R": ["Giant_Axe", "Two_Handed_Axe_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_SHOES":  ["Tidal_Shoes"],
        },
        "card_prio": ["Zipper_Bear_Card", "Andre_Card", "Tao_Gunka_Card", "Bathory_Card"],
        "notes": "Maximize Power: elimina variância de dano (min ATK = max ATK). "
                 "VIT 99 para sobreviver Earthquake de MVPs (requer ~15500 HP). "
                 "Solo tank de Baphomet/Valkyrie com Over Thrust + Adrenaline Rush. "
                 "Bathory Card armadura: imunidade Dark para mapas Thor/Glast Heim. "
                 "STR 70, AGI 50, VIT 99, INT 1, DEX 55, LUK 1.",
    },

    # ── SAGE ─────────────────────────────────────────────────────────────────
    "Sage_INT": {
        "farm_maps": ["orc_dun02", "gef_fild14", "gl_knt01"],
        "hunt_mobs": ["High_Orc", "Orc_Warrior", "Raydric"],
        "buy_items": CASTER_CONSUMABLES + ["Blue_Gemstone"],
        "sell_items": ["High_Orc_Card", "Daydric_Card", "Orcish_Axe"],
        "equip_prio": {
            "EQI_HAND_R": ["Survival_Rod_"],
        },
        "card_prio": ["Drops_Card", "Dokebi_Card"],
        "notes": "Land Protector Lv3-4 (NÃO 5 — área grande demais). "
                 "130+ DEX para LP rápido. Vender serviço de Endow (Aspersio, Endow Element). "
                 "STR 1, AGI 1, VIT 40, INT 80, DEX 99, LUK 1.",
    },
    "Sage_DEX": {
        "farm_maps": ["gef_fild14", "orc_dun02", "pay_dun04"],
        "hunt_mobs": ["High_Orc", "Orc_Warrior", "Mummy"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Blue_Gemstone"],
        "sell_items": ["High_Orc_Card", "Mummy_Card", "Orcish_Axe"],
        "equip_prio": {
            "EQI_HAND_R": ["Survival_Rod_"],
        },
        "card_prio": ["Drops_Card", "Skel_Worker_Card"],
        "notes": "Hindsight auto-casta Cold Bolt no melee. High Orcs = fraco a Water. "
                 "STR 60, AGI 80, VIT 30, INT 85, DEX 45, LUK 1.",
    },

    # ── PROFESSOR ────────────────────────────────────────────────────────────
    "Professor_INT": {
        "farm_maps": ["abbey02", "lhz_dun02", "thor_v02"],
        "hunt_mobs": ["Banshee", "Necromancer", "Venatu"],
        "buy_items": CASTER_CONSUMABLES + ["Blue_Gemstone"],
        "sell_items": ["Necromancer_Card", "Dolomedes_Card", "Fabric"],
        "equip_prio": {
            "EQI_HAND_R": ["Lich_Bone_Wand", "Survival_Rod_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
        },
        "card_prio": ["Drops_Card", "Tao_Gunka_Card"],
        "notes": "Soul Burn drena 20000 SP do alvo (Lv10). "
                 "Fiber Lock (Spider Web) imobiliza 3x3. Wall of Fog bloqueia ranged. "
                 "STR 1, AGI 1, VIT 50, INT 90, DEX 99, LUK 1.",
    },
    "Professor_VIT": {
        "farm_maps": ["abbey02", "gl_chyard", "lhz_dun02"],
        "hunt_mobs": ["Banshee", "Evil_Druid", "Venatu"],
        "buy_items": CASTER_CONSUMABLES,
        "sell_items": ["Necromancer_Card", "Evil_Druid_Card", "Fabric"],
        "equip_prio": {
            "EQI_ARMOR":  ["Valkyrie_Armor"],
        },
        "card_prio": ["Tao_Gunka_Card", "Ghostring_Card"],
        "notes": "MVP holder com Fiber Lock. WoE disruptor. "
                 "STR 1, AGI 1, VIT 99, INT 80, DEX 99, LUK 1.",
    },

    # ── ROGUE ────────────────────────────────────────────────────────────────
    "Rogue_AGI": {
        "farm_maps": ["gl_cul01", "gl_cul02", "gef_fild14", "orc_dun02"],
        "hunt_mobs": ["Thara_Frog", "High_Orc", "Orc_Warrior"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["Thara_Frog_Card", "High_Orc_Card", "Daydric_Card", "Stolen drops"],
        "equip_prio": {
            "EQI_HAND_R": ["Main_Gauche_"],
        },
        "card_prio": ["Side_Winder_Card", "Kobold_Card"],
        "notes": "Snatcher auto-rouba em cada hit. Maximizar ASPD = mais tentativas de Steal. "
                 "Main Gauche[4] + 4x Sidewinder = Double Attack Lv5. "
                 "STR 70, AGI 90, VIT 20, INT 1, DEX 50, LUK 1.",
    },
    "Rogue_STR": {
        "farm_maps": ["gl_knt01", "orc_dun02", "pay_dun04"],
        "hunt_mobs": ["Raydric", "High_Orc", "Mummy"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["Daydric_Card", "High_Orc_Card", "Mummy_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Stiletto_", "Blade_"],
        },
        "card_prio": ["Skel_Worker_Card", "Hydra_Card"],
        "notes": "Backstab = 700% ATK, não pode errar (ignora flee). "
                 "Deve atacar pelas costas. STR 90, AGI 60, VIT 30, INT 1, DEX 60, LUK 1.",
    },

    # ── STALKER ──────────────────────────────────────────────────────────────
    "Stalker_AGI": {
        "farm_maps": ["gl_knt01", "gl_knt02", "gef_fild14"],
        "hunt_mobs": ["Raydric", "Khalitzburg", "High_Orc"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Speed_Potion"],
        "sell_items": ["Daydric_Card", "Khalitzburg_Card", "High_Orc_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Stiletto_", "Main_Gauche_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
        },
        "card_prio": ["Kobold_Card", "Side_Winder_Card"],
        "notes": "Chase Walk = mover enquanto Hidden. Plagiarism: copiar ME do HP para farm solo. "
                 "Full Strip no WoE: remover todos os 4 slots do alvo. "
                 "STR 70, AGI 90, VIT 30, INT 1, DEX 60, LUK 1.",
    },
    "Stalker_Chase": {
        "farm_maps": ["lhz_dun02", "gl_knt02", "abbey02"],
        "hunt_mobs": ["Venatu", "Abysmal_Knight", "Necromancer"],
        "buy_items": WOE_CONSUMABLES,
        "sell_items": ["Dolomedes_Card", "Knight_Of_Abyss_Card", "Corrupted_Monk_Card"],
        "equip_prio": {
            "EQI_ARMOR":  ["Valkyrie_Armor"],
        },
        "card_prio": ["Tao_Gunka_Card", "Ghostring_Card"],
        "notes": "Full Strip + Chase Walk = WoE role principal. "
                 "STR 70, AGI 80, VIT 40, INT 1, DEX 60, LUK 1.",
    },
    "Stalker_Snatcher": {
        "farm_maps": ["gef_fild14", "orc_dun02", "gl_knt01"],
        "hunt_mobs": ["High_Orc", "Orc_Warrior", "Raydric"],
        "buy_items": MELEE_DPS_CONSUMABLES + ["Speed_Potion"],
        "sell_items": ["High_Orc_Card", "Daydric_Card", "Orcish_Axe", "Steel", "Cyfar"],
        "equip_prio": {
            "EQI_HAND_R": ["Main_Gauche_", "Stiletto_"],
            "EQI_ARMOR":  ["Thief_Clothes_"],
            "EQI_GARMENT":["Muffler_"],
        },
        "card_prio": ["Side_Winder_Card", "Kobold_Card", "Blood_Butterfly_Card"],
        "notes": "Snatcher Lv10: Steal automático em todo ataque físico. "
                 "LUK 45 melhora taxa de sucesso do Steal diretamente. "
                 "AGI 90 = mais ataques/s = mais roubos por minuto. "
                 "Chase Walk ATK bonus após sair do stealth para garantir kill. "
                 "STR 60, AGI 90, VIT 30, INT 10, DEX 60, LUK 45.",
    },

    # ── ALCHEMIST ────────────────────────────────────────────────────────────
    "Alchemist_INT": {
        "farm_maps": ["pay_fild08", "mjolnir_05", "gef_fild09"],
        "hunt_mobs": ["Wormtail", "Creamy", "Myst_Case"],
        "buy_items": CASTER_CONSUMABLES + [
            "Seed_Of_Life", "Morning_Dew_Of_Yggdrasil", "Dew_Laden_Moss", "Cloudy_Crystal"
        ],
        "sell_items": [
            "Condensed_White_Potion", "Blue_Potion", "Embryo",
            "Homunculus_feed"
        ],
        "equip_prio": {
            "EQI_HAND_R": ["Mace_"],
        },
        "card_prio": ["Phen_Card"],
        "notes": "Homunculus: Lif (heal), Amistr (tank), Filir (ATK/ASPD), Vanilmirth (magia). "
                 "Ingredientes Embryo: Seed of Life + Morning Dew + Cloudy Crystal + Dew Laden Moss. "
                 "Lucro: mass produce Condensed White Potion + vend. "
                 "STR 30, AGI 1, VIT 40, INT 80, DEX 50, LUK 1.",
    },
    "Alchemist_STR": {
        "farm_maps": ["orc_dun02", "gef_fild14", "pay_dun04"],
        "hunt_mobs": ["High_Orc", "Orc_Warrior", "Mummy"],
        "buy_items": MELEE_DPS_CONSUMABLES,
        "sell_items": ["Orcish_Axe", "Steel", "High_Orc_Card", "Mummy_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Mace_"],
        },
        "card_prio": ["Skel_Worker_Card", "Hydra_Card"],
        "notes": "Acid Bomb (base Alch). Fórmula: 0.7 × VIT_alvo × INT_caster² / (VIT+INT). "
                 "STR 60, AGI 30, VIT 30, INT 70, DEX 40, LUK 1.",
    },

    # ── CREATOR ──────────────────────────────────────────────────────────────
    "Creator_INT": {
        "farm_maps": ["lhz_dun02", "lhz_dun03", "abbey02"],
        "hunt_mobs": ["Venatu", "Bloody_Knight", "Necromancer"],
        "buy_items": CASTER_CONSUMABLES + ["Acid_Bottle", "Bottle_Grenade"],
        "sell_items": [
            "Condensed_White_Potion", "Blue_Potion",
            "Dolomedes_Card", "Bloody_Knight_Card", "Corrupted_Monk_Card"
        ],
        "equip_prio": {
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_ACC_L":  ["Orleans_Glove"],
            "EQI_ACC_R":  ["Orleans_Glove"],
        },
        "card_prio": ["Tao_Gunka_Card", "Phen_Card"],
        "notes": "Acid Demonstration: INT 99 base + buffs ~125 total. "
                 "Lex Aeterna antes de AD = dobra dano (2×10 hits). "
                 "Alvo com VIT alto = dano enorme. Bio Labs = farm ideal. "
                 "Comprar 200+ Acid Bottle + 200+ Bottle Grenade por sessão. "
                 "STR 1, AGI 1, VIT 40, INT 99, DEX 50, LUK 1.",
    },
    "Creator_VIT": {
        "farm_maps": ["lhz_dun02", "abbey02", "gl_knt02"],
        "hunt_mobs": ["Venatu", "Necromancer", "Abysmal_Knight"],
        "buy_items": WOE_CONSUMABLES + ["Glistening_Coat"],
        "sell_items": ["Corrupted_Monk_Card", "Knight_Of_Abyss_Card"],
        "equip_prio": {
            "EQI_ARMOR":  ["Valkyrie_Armor"],
        },
        "card_prio": ["Tao_Gunka_Card", "Ghostring_Card"],
        "notes": "Chemical Protection previne Strip no WoE. "
                 "Homunculus como tanque secundário. "
                 "STR 1, AGI 1, VIT 99, INT 70, DEX 60, LUK 1.",
    },
    "Creator_FCP": {
        "farm_maps": ["prontera", "gl_cas01", "gl_cas02"],
        "hunt_mobs": ["Abysmal_Knight", "Khalitzburg", "Raydric"],
        "buy_items": WOE_CONSUMABLES + ["Glistening_Coat"],
        "sell_items": ["Knight_Of_Abyss_Card", "Daydric_Card", "Steel"],
        "equip_prio": {
            "EQI_SHOES": ["Refresh_Shoes", "Variant_Shoes"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_ACC_L":  ["Orleans_Glove"],
            "EQI_GARMENT":["Muffler_"],
        },
        "card_prio": ["Smokie_Card", "Roda_Frog_Card", "Tao_Gunka_Card"],
        "notes": "Full Chemical Protection slave WoE: apenas spamma FCP nos aliados. "
                 "DEX 99 para recast rápido (FCP tem cast time variável). "
                 "STR 1 intencional — nunca ataca. Smokie Card (Cloaking) para sobreviver. "
                 "Previne Acid Bomb destruir armadura/arma dos aliados. "
                 "STR 1, AGI 1, VIT 70, INT 20, DEX 99, LUK 1.",
    },
    "Creator_Vani": {
        "farm_maps": ["lhz_dun02", "lhz_dun03", "abbey02"],
        "hunt_mobs": ["Venatu", "Bloody_Knight", "Necromancer"],
        "buy_items": CASTER_CONSUMABLES + ["Condensed_White_Potion"],
        "sell_items": ["Dolomedes_Card", "Bloody_Knight_Card", "Corrupted_Monk_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Elemental_Sword", "Erde"],
            "EQI_ARMOR": ["Clothes_Of_The_Lord", "Saint_Robe_"],
            "EQI_GARMENT": ["Morrigane's_Manteau", "Wool_Scarf"],
        },
        "card_prio": ["Drops_Card", "Tao_Gunka_Card", "Bathory_Card"],
        "notes": "Vanilmirth Caprice = bolt aleatório com MATK do homunculus. "
                 "Feather Mace (Creator exclusivo) + Mace Mastery: MATK+20. "
                 "Alloy Armor + Prophet's Cape: sinergiza com Vanilmirth. "
                 "LUK 40 melhora rolls de crescimento do Vanilmirth (RNG de stats). "
                 "STR 70, AGI 1, VIT 60, INT 75, DEX 50, LUK 40.",
    },

    # ── BARD / CLOWN ─────────────────────────────────────────────────────────
    "Bard_DEX": {
        "farm_maps": ["gl_knt01", "orc_dun02", "pay_fild08"],
        "hunt_mobs": ["Raydric", "High_Orc", "Wormtail"],
        "buy_items": UNIVERSAL_CONSUMABLES + ["Arrow", "Silver_Arrow"],
        "sell_items": ["Daydric_Card", "High_Orc_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Composite_Bow_", "Kakkung_"],
        },
        "card_prio": ["Knight_Of_Abyss_Card", "Skel_Worker_Card"],
        "notes": "Apple of Idun + Impressive Riff para suporte de party. "
                 "Poem of Bragi: DEX reduz delay, INT reduz cast. Múltiplos de 10 contam. "
                 "Serviço Bragi muito valorizado em guilds WoE. "
                 "STR 1, AGI 30, VIT 40, INT 40, DEX 99, LUK 1.",
    },
    "Clown_DEX": {
        "farm_maps": ["thor_v01", "gl_knt02", "abbey02"],
        "hunt_mobs": ["Kasa", "Abysmal_Knight", "Necromancer"],
        "buy_items": UNIVERSAL_CONSUMABLES + ["Arrow", "Silver_Arrow"],
        "sell_items": ["Kasa_Card", "Knight_Of_Abyss_Card", "Corrupted_Monk_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Composite_Bow_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_HEAD_TOP":["Horn_Of_Lord_Kaho"],
        },
        "card_prio": ["Knight_Of_Abyss_Card", "Skel_Worker_Card"],
        "notes": "Poem of Bragi Lv10 transcendente. Tarot Card of Fate = debuffs aleatórios poderosos. "
                 "Kaahi: auto-cast Heal quando atacado. "
                 "STR 1, AGI 30, VIT 50, INT 50, DEX 99, LUK 1.",
    },

    # ── DANCER / GYPSY ───────────────────────────────────────────────────────
    "Dancer_AGI": {
        "farm_maps": ["orc_dun02", "gef_fild14", "pay_fild08"],
        "hunt_mobs": ["High_Orc", "Orc_Warrior", "Wormtail"],
        "buy_items": UNIVERSAL_CONSUMABLES + ["Arrow", "Silver_Arrow"],
        "sell_items": ["High_Orc_Card", "Orc_Warrior_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Composite_Bow_"],
            "EQI_ARMOR":  ["Tights_"],
        },
        "card_prio": ["Knight_Of_Abyss_Card", "Gloom_Under_Night_Card"],
        "notes": "Arrow Shower 3x3 AoE. Slow Grace debuffa ASPD inimigo -30%. "
                 "STR 10, AGI 90, VIT 30, INT 1, DEX 80, LUK 1.",
    },
    "Gypsy_AGI": {
        "farm_maps": ["thor_v01", "gl_knt02", "abbey02"],
        "hunt_mobs": ["Kasa", "Abysmal_Knight", "Necromancer"],
        "buy_items": UNIVERSAL_CONSUMABLES + ["Arrow", "Silver_Arrow"],
        "sell_items": ["Kasa_Card", "Knight_Of_Abyss_Card", "Corrupted_Monk_Card"],
        "equip_prio": {
            "EQI_HAND_R": ["Composite_Bow_"],
            "EQI_ARMOR":  ["Valkyrie_Armor"],
            "EQI_HEAD_TOP":["Horn_Of_Lord_Kaho"],
        },
        "card_prio": ["Knight_Of_Abyss_Card", "Gloom_Under_Night_Card"],
        "notes": "Marionette Control: transfere metade dos stats base da Gypsy para aliado. "
                 "Link Sniper = combo devastador. Charming Wink: stun em jogadores masculinos. "
                 "STR 10, AGI 90, VIT 40, INT 1, DEX 99, LUK 1.",
    },
}


def get_build_knowledge(job_name: str, build_variant: str) -> dict:
    """Retorna conhecimento de build. Tenta '{job_name}_{build_variant}', depois '{job_name}'."""
    key = f"{job_name}_{build_variant}" if build_variant else job_name
    return BUILD_KNOWLEDGE.get(key) or BUILD_KNOWLEDGE.get(job_name) or {}


def get_farm_maps(job_name: str, build_variant: str) -> list[str]:
    return get_build_knowledge(job_name, build_variant).get("farm_maps", ["prontera"])


def get_buy_items(job_name: str, build_variant: str) -> list[str]:
    return get_build_knowledge(job_name, build_variant).get("buy_items", UNIVERSAL_CONSUMABLES)


def get_sell_items(job_name: str, build_variant: str) -> list[str]:
    return get_build_knowledge(job_name, build_variant).get("sell_items", [])


def get_card_priorities(job_name: str, build_variant: str) -> list[str]:
    return get_build_knowledge(job_name, build_variant).get("card_prio", [])


def get_equip_priorities(job_name: str, build_variant: str) -> dict[str, list[str]]:
    return get_build_knowledge(job_name, build_variant).get("equip_prio", {})

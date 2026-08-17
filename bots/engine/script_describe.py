"""
script_describe.py
Traduz script de item do rAthena para descricao legivel em portugues.

Existe para a coluna "Efeitos" do catalogo de cartas: tudo que uma carta faz
e que NAO e bonus de status simples. Os bonus de status ja saem pelo
BONUS_MAP do item_parser; aqui fica o resto — dano por raca, resistencia a
status, autospell, skills concedidas, drops extras, drain, etc.

A particao e limpa: o que o BONUS_MAP captura nao aparece aqui, e o que
aparece aqui o BONUS_MAP nao captura. Nada se perde nem se duplica.
"""

import re
from item_parser import BONUS_MAP

# ─────────────────────────────────────────────────────────────────────────────
# Constantes do rAthena → portugues
# ─────────────────────────────────────────────────────────────────────────────
RACA = {
    "DemiHuman": "Demi-humanos", "Undead": "Mortos-vivos", "Brute": "Brutos",
    "Insect": "Insetos", "Plant": "Plantas", "Fish": "Peixes",
    "Demon": "Demônios", "Angel": "Anjos", "Dragon": "Dragões",
    "Formless": "Amorfos", "Player_Human": "jogadores",
    "Player_Doram": "Dorams", "All": "todas as raças",
}
RACA2 = {"Goblin": "Goblins", "Kobold": "Kobolds", "Golem": "Golens"}
ELEM = {
    "Neutral": "Neutro", "Water": "Água", "Earth": "Terra", "Fire": "Fogo",
    "Wind": "Vento", "Poison": "Veneno", "Holy": "Sagrado", "Dark": "Sombrio",
    "Ghost": "Fantasma", "Undead": "Morto-vivo", "All": "todos os elementos",
}
STATUS = {
    "Stun": "Atordoamento", "Freeze": "Congelamento", "Stone": "Petrificação",
    "Sleep": "Sono", "Curse": "Maldição", "Silence": "Silêncio",
    "Blind": "Cegueira", "Poison": "Veneno", "Confusion": "Confusão",
    "Bleeding": "Sangramento",
}
TAM = {"Small": "Pequenos", "Medium": "Médios", "Large": "Grandes",
       "All": "todos os tamanhos"}
CLASSE = {"Boss": "chefes (MVP)", "Normal": "monstros comuns", "All": "todos os monstros"}
GRUPO = {"Herb": "ervas", "Fruit": "frutas", "Meat": "carnes", "Candy": "doces",
         "Juice": "sucos", "Fish": "peixes", "Food": "comidas",
         "Recovery": "itens de recuperação"}

# Skills mais citadas — as demais saem com o nome tecnico mesmo
SKILL = {
    "AL_HEAL": "Cura", "AL_BLESSING": "Benção", "AL_INCAGI": "Agilidade",
    "AL_DECAGI": "Diminuir Agilidade", "AL_PNEUMA": "Pneuma",
    "AL_CRUCIS": "Sinal da Cruz", "AL_CURE": "Curar", "AL_TELEPORT": "Teleporte",
    "PR_KYRIE": "Kyrie Eleison", "PR_GLORIA": "Gloria", "PR_IMPOSITIO": "Impositio Manus",
    "PR_LEXDIVINA": "Lex Divina", "PR_LEXAETERNA": "Lex Aeterna",
    "HP_ASSUMPTIO": "Assumptio", "CR_AUTOGUARD": "Auto Guarda",
    "CR_GRANDCROSS": "Grande Cruz", "MG_COLDBOLT": "Raio de Gelo",
    "MG_FIREBOLT": "Raio de Fogo", "MG_FIREBALL": "Bola de Fogo",
    "MG_FROSTDIVER": "Mergulho Gélido", "MG_STONECURSE": "Maldição de Pedra",
    "MG_SIGHT": "Visão", "WZ_STORMGUST": "Tempestade de Gelo",
    "WZ_METEOR": "Chuva de Meteoros", "WZ_JUPITEL": "Trovão de Júpiter",
    "WZ_FROSTNOVA": "Nova Gélida", "WZ_QUAGMIRE": "Lamaçal",
    "SM_BASH": "Golpe Poderoso", "SM_MAGNUM": "Impacto Mágnum",
    "SM_ENDURE": "Persistência", "KN_BOWLINGBASH": "Golpe de Boliche",
    "LK_BERSERK": "Frenesi", "AS_SONICBLOW": "Impacto Sônico",
    "AS_CLOAKING": "Ocultar-se", "TF_HIDING": "Esconder-se",
    "TF_STEAL": "Roubar", "TF_POISON": "Envenenar", "TF_DOUBLE": "Ataque Duplo",
    "TF_DETOXIFY": "Desintoxicar", "TF_BACKSLIDING": "Salto para Trás",
    "TF_PICKSTONE": "Pegar Pedra", "TF_THROWSTONE": "Atirar Pedra",
    "RG_INTIMIDATE": "Intimidar", "RG_STRIPARMOR": "Rasgar Armadura",
    "RG_STRIPWEAPON": "Rasgar Arma", "SA_DISPELL": "Dissipar",
    "SA_LANDPROTECTOR": "Proteção Territorial", "SA_SPELLBREAKER": "Quebra-Magia",
    "SA_CASTCANCEL": "Cancelar Conjuração", "MO_CALLSPIRITS": "Invocar Esferas",
    "AC_CONCENTRATION": "Concentração", "BA_FROSTJOKER": "Piada Congelante",
    "DC_WINKCHARM": "Piscadela", "MC_DISCOUNT": "Desconto",
    "NPC_EARTHQUAKE": "Terremoto",
}


def _sk(nome: str) -> str:
    return SKILL.get(nome, nome)


def _pct(v) -> str:
    try:
        n = int(v)
    except (ValueError, TypeError):
        return _expr(v)
    return f"+{n}%" if n > 0 else f"{n}%"


# ─────────────────────────────────────────────────────────────────────────────
# Valores dinamicos. Boa parte das cartas nao usa numero fixo:
#   300+600*(readparam(bVit)>=77)   → dobra a chance com VIT 77+
#   getrefine()*-1                  → escala com o refino
#   readparam(bDex)/18              → deriva de outro atributo
# Sem tratar isso, o int() estoura e o efeito sai cru na tabela.
# ─────────────────────────────────────────────────────────────────────────────
_ATRIB = {"bStr": "STR", "bAgi": "AGI", "bVit": "VIT", "bInt": "INT",
          "bDex": "DEX", "bLuk": "LUK"}


def _cond_expr(c: str) -> str:
    m = re.search(r'readparam\((b\w+)\)\s*>=\s*(\d+)', c)
    if m:
        return f"{_ATRIB.get(m.group(1), m.group(1))} {m.group(2)}+"
    m = re.search(r'Job_(\w+)', c)
    if m:
        return m.group(1).replace("_", " ")
    return c.strip()


def _expr(v: str) -> str:
    """Descreve uma expressao nao-numerica de forma legivel."""
    v = str(v).strip()
    m = re.match(r'^(\d+)\s*\+\s*(\d+)\s*\*\s*\((.+)\)$', v)
    if m:
        base, extra, cond = int(m.group(1)), int(m.group(2)), m.group(3)
        return f"{base/100:g}% ({(base+extra)/100:g}% com {_cond_expr(cond)})"
    m = re.match(r'^readparam\((b\w+)\)\s*/\s*(\d+)$', v)
    if m:
        return f"{_ATRIB.get(m.group(1), m.group(1))}/{m.group(2)}"
    if 'getrefine()' in v:
        return "conforme o refino"
    if 'BaseLevel' in v:
        return "conforme o nível base"
    return v


def _taxa(v) -> str:
    """Chance em milesimos (300 = 3%), tolerando expressao."""
    try:
        return f"{int(v)/100:g}%"
    except (ValueError, TypeError):
        return _expr(v)


# ─────────────────────────────────────────────────────────────────────────────
# Tradutores por tipo de bonus. Cada um recebe os argumentos ja separados.
# ─────────────────────────────────────────────────────────────────────────────
def _t(args, i, tabela, padrao=None):
    """Traduz o argumento i usando a tabela, tirando o prefixo (RC_, Ele_...)."""
    if i >= len(args):
        return padrao or "?"
    v = re.sub(r'^(RC2_|RC_|Ele_|Eff_|Size_|Class_|IG_)', '', args[i])
    return tabela.get(v, v)


TRAD = {
    # ── dano por alvo ────────────────────────────────────────────────────
    "bAddRace":       lambda a: f"Dano {_pct(a[1])} contra {_t(a,0,RACA)}",
    "bAddRace2":      lambda a: f"Dano {_pct(a[1])} contra {_t(a,0,RACA2)}",
    "bMagicAddRace":  lambda a: f"Dano mágico {_pct(a[1])} contra {_t(a,0,RACA)}",
    "bAddEle":        lambda a: f"Dano {_pct(a[1])} contra elemento {_t(a,0,ELEM)}",
    "bAddSize":       lambda a: f"Dano {_pct(a[1])} contra monstros {_t(a,0,TAM)}",
    "bAddClass":      lambda a: f"Dano {_pct(a[1])} contra {_t(a,0,CLASSE)}",
    "bAddDamageClass":lambda a: f"Dano {_pct(a[1])} contra o monstro #{a[0]}",
    "bCriticalAddRace":lambda a: f"Crítico +{a[1]} contra {_t(a,0,RACA)}",
    "bSkillAtk":      lambda a: f"Dano de {_sk(a[0])} {_pct(a[1])}",
    "bLongAtkRate":   lambda a: f"Dano à distância {_pct(a[0])}",
    "bCriticalLong":  lambda a: f"Crítico com ataque à distância +{a[0]}",
    "bSplashRange":   lambda a: f"Ataque atinge área de {a[0]} célula(s)",
    "bDefRatioAtkClass": lambda a: f"Dano proporcional à DEF de {_t(a,0,CLASSE)}",
    "bIgnoreDefClass":lambda a: f"Ignora a DEF de {_t(a,0,CLASSE)}",
    "bIgnoreMdefClassRate": lambda a: f"Ignora {a[1]}% da MDEF de {_t(a,0,CLASSE)}",

    # ── reducao de dano recebido ─────────────────────────────────────────
    "bSubRace":       lambda a: f"Reduz {a[1]}% do dano de {_t(a,0,RACA)}",
    "bSubEle":        lambda a: f"Reduz {a[1]}% do dano de elemento {_t(a,0,ELEM)}",
    "bSubSize":       lambda a: f"Reduz {a[1]}% do dano de monstros {_t(a,0,TAM)}",
    "bSubClass":      lambda a: f"Reduz {a[1]}% do dano de {_t(a,0,CLASSE)}",
    "bMagicSubRace":  lambda a: f"Reduz {a[1]}% do dano mágico de {_t(a,0,RACA)}",
    "bAddDefMonster": lambda a: f"Reduz {a[1]}% do dano do monstro #{a[0]}",
    "bLongAtkDef":    lambda a: f"Reduz {a[0]}% do dano à distância",
    "bDefEle":        lambda a: f"Muda o elemento da armadura para {_t(a,0,ELEM)}",
    "bMagicDamageReturn": lambda a: f"{a[0]}% de refletir dano mágico",
    "bShortWeaponDamageReturn": lambda a: f"Reflete {a[0]}% do dano corpo a corpo",

    # ── status ───────────────────────────────────────────────────────────
    "bResEff":        lambda a: f"Resistência a {_t(a,0,STATUS)} +{_taxa(a[1])}",
    "bAddEff":        lambda a: f"{_taxa(a[1])} de causar {_t(a,0,STATUS)} ao atacar",
    "bAddEff2":       lambda a: f"{_taxa(a[1])} de causar {_t(a,0,STATUS)} em si mesmo",
    "bAddEffWhenHit": lambda a: f"{_taxa(a[1])} de causar {_t(a,0,STATUS)} ao ser atingido",
    "bComaClass":     lambda a: f"{_taxa(a[1])} de causar Coma em {_t(a,0,CLASSE)}",

    # ── recuperacao e drain ──────────────────────────────────────────────
    "bHPrecovRate":   lambda a: f"Regeneração de HP {_pct(a[0])}",
    "bSPrecovRate":   lambda a: f"Regeneração de SP {_pct(a[0])}",
    "bHPRegenRate":   lambda a: f"Recupera {a[0]} HP a cada {int(a[1])/1000:g}s",
    "bSPRegenRate":   lambda a: f"Recupera {a[0]} SP a cada {int(a[1])/1000:g}s",
    "bHPDrainRate":   lambda a: f"{_taxa(a[0])} de absorver {a[1]}% do dano como HP",
    "bSPDrainRate":   lambda a: f"{_taxa(a[0])} de absorver {a[1]}% do dano como SP",
    "bHPGainValue":   lambda a: f"Recupera {a[0]} HP ao matar",
    "bSPGainValue":   lambda a: f"Recupera {a[0]} SP ao matar",
    "bSPDrainValue":  lambda a: f"{'Recupera' if int(a[0])>0 else 'Perde'} {abs(int(a[0]))} SP por golpe",
    "bSPGainRace":    lambda a: f"Recupera SP ao matar {_t(a,0,RACA)}",
    "bHPLossRate":    lambda a: f"Perde {a[0]} HP a cada {int(a[1])/1000:g}s",
    "bSPVanishRate":  lambda a: f"{_taxa(a[0])} de drenar {a[1]}% do SP do alvo",
    "bHealPower":     lambda a: f"Poder de cura {_pct(a[0])}",
    "bAddItemHealRate": lambda a: f"Recuperação do item #{a[0]} {_pct(a[1])}",
    "bAddItemGroupHealRate": lambda a: f"Recuperação de {_t(a,0,GRUPO)} {_pct(a[1])}",

    # ── conjuracao ───────────────────────────────────────────────────────
    "bCastrate":      lambda a: (f"Tempo de conjuração de {_sk(a[0])} {_pct(a[1])}"
                                 if len(a) > 1 else f"Tempo de conjuração {_pct(a[0])}"),
    "bDelayRate":     lambda a: f"Delay pós-conjuração {_pct(a[0])}",
    "bUseSPrate":     lambda a: f"Consumo de SP {_pct(a[0])}",
    "bNoCastCancel":  lambda a: "Conjuração não é interrompida ao levar dano",
    "bNoGemStone":    lambda a: "Não consome gemas nas habilidades",

    # ── drops e zeny ─────────────────────────────────────────────────────
    "bAddMonsterDropItem": lambda a: (f"{int(a[-1])/100:g}% de dropar o item #{a[0]}"
                                      + (f" de {_t(a,1,RACA)}" if len(a) > 2 else "")),
    "bAddMonsterDropItemGroup": lambda a: f"Chance de dropar {_t(a,0,GRUPO)}",
    "bGetZenyNum":    lambda a: f"{a[1]}% de ganhar até {a[0]} zeny ao matar",
    "bExpAddRace":    lambda a: f"Experiência {_pct(a[1])} ao matar {_t(a,0,RACA)}",

    # ── flags e movimento ────────────────────────────────────────────────
    "bUnbreakableArmor":  lambda a: "Armadura indestrutível",
    "bUnbreakableWeapon": lambda a: "Arma indestrutível",
    "bBreakWeaponRate":   lambda a: f"{_taxa(a[0])} de quebrar a arma do alvo",
    "bBreakArmorRate":    lambda a: f"{_taxa(a[0])} de quebrar a armadura do alvo",
    "bNoKnockback":       lambda a: "Imune a repulsão",
    "bNoWalkDelay":       lambda a: "Sem atraso de movimento ao ser atingido",
    "bNoSizeFix":         lambda a: "Ignora penalidade de tamanho da arma",
    "bSpeedRate":         lambda a: f"Velocidade de movimento {_pct(a[0])}",
    "bIntravision":       lambda a: "Enxerga inimigos ocultos",
    "bClassChange":       lambda a: f"{_taxa(a[0])} de transformar o alvo em outro monstro",
    "bAddSkillBlow":      lambda a: f"{_sk(a[0])} empurra o alvo {a[1]} célula(s)",
    "bRestartFullRecover":lambda a: "Ressuscita com HP e SP cheios",
}


def _autospell(args, ao_ser_atingido=False) -> str:
    quando = "ao ser atingido" if ao_ser_atingido else "ao atacar"
    skill = _sk(args[0].strip('"'))
    lv    = args[1] if len(args) > 1 else "?"
    taxa  = args[2] if len(args) > 2 else "?"
    try:
        taxa = f"{int(taxa)/100:g}%"
    except (ValueError, TypeError):
        taxa = f"{taxa}"
    return f"{taxa} de conjurar {skill} nv.{lv} {quando}"


def _split_args(s: str) -> list[str]:
    """Separa argumentos por virgula respeitando aspas e parenteses."""
    out, atual, prof, aspas = [], "", 0, False
    for ch in s:
        if ch == '"':
            aspas = not aspas
        elif not aspas and ch in "([{":
            prof += 1
        elif not aspas and ch in ")]}":
            prof -= 1
        elif ch == "," and prof == 0 and not aspas:
            out.append(atual.strip()); atual = ""; continue
        atual += ch
    if atual.strip():
        out.append(atual.strip())
    return [a.strip().strip('"') for a in out]


def _condicao(cond: str) -> str:
    """Traduz a condicao de um if para um prefixo curto."""
    c = cond.strip()
    jobs = re.findall(r'Job_(\w+)', c)
    if jobs:
        nomes = " ou ".join(j.replace("_", " ") for j in jobs)
        return f"Se {nomes}"
    m = re.search(r'getrefine\(\)\s*([<>=]+)\s*(\d+)', c)
    if m:
        return f"Se refino {m.group(1)} {m.group(2)}"
    m = re.search(r'readparam\((\w+)\)\s*([<>=]+)\s*(\d+)', c)
    if m:
        return f"Se {m.group(1).lstrip('b')} {m.group(2)} {m.group(3)}"
    if 'isequipped' in c:
        return "Se equipado com o conjunto" if not c.startswith('!') else "Se não equipado com o conjunto"
    if 'BaseLevel' in c:
        return "Conforme o nível base"
    return "Condicional"


def describe(script: str) -> list[str]:
    """
    Converte um script de item na lista de efeitos legiveis, ja excluindo
    o que o BONUS_MAP captura (esses aparecem na coluna de bonus).
    """
    if not script:
        return []
    s = re.sub(r'//[^\n]*', '', script)
    efeitos: list[str] = []

    # autobonus: bloco que ativa temporariamente
    for m in re.finditer(r'autobonus2?\s+"\{([^}]*)\}"\s*,\s*(\d+)\s*,\s*(\d+)', s):
        interno = ", ".join(describe(m.group(1)) or [])
        stats = [f"{BONUS_MAP[b]}{v}" for b, v in
                 re.findall(r'bonus\s+(b\w+)\s*,\s*(-?\d+)', m.group(1)) if b in BONUS_MAP]
        alvo = ", ".join(x for x in [", ".join(stats), interno] if x) or "efeito temporário"
        efeitos.append(f"{int(m.group(2))/100:g}% ao lutar: {alvo} por {int(m.group(3))/1000:g}s")
    s = re.sub(r'autobonus2?\s+"\{[^}]*\}"[^;]*;', '', s)

    # blocos condicionais
    prefixos: list[tuple[str, str]] = []
    for m in re.finditer(r'if\s*\(([^)]*)\)\s*\{([^}]*)\}', s):
        prefixos.append((_condicao(m.group(1)), m.group(2)))
    s = re.sub(r'if\s*\(([^)]*)\)\s*\{[^}]*\}', '', s)
    for m in re.finditer(r'if\s*\(([^)]*)\)\s*([^;{]+;)', s):
        prefixos.append((_condicao(m.group(1)), m.group(2)))
    s = re.sub(r'if\s*\(([^)]*)\)\s*[^;{]+;', '', s)

    def processa(trecho: str, prefixo: str = "") -> list[str]:
        saida = []
        for linha in trecho.split(';'):
            linha = linha.strip()
            if not linha:
                continue
            # bonus sem argumento: `bonus bNoSizeFix;`, `bonus bIntravision;`
            m = re.match(r'^bonus\s+(b\w+)$', linha)
            if m and m.group(1) in TRAD:
                saida.append(f"{prefixo}{TRAD[m.group(1)]([])}")
                continue

            m = re.match(r'^bonus([2-5]?)\s+(b\w+)\s*,\s*(.*)$', linha, re.S)
            if m:
                tipo, args = m.group(2), _split_args(m.group(3))
                if tipo.startswith("bAutoSpell"):
                    txt = _autospell(args, "WhenHit" in tipo)
                elif tipo in TRAD:
                    try:
                        txt = TRAD[tipo](args)
                    except (IndexError, ValueError):
                        txt = f"{tipo} ({', '.join(args)})"
                elif tipo in BONUS_MAP:
                    # Valor numerico ja aparece na coluna de bonus. Mas varias
                    # cartas derivam o stat de outro atributo ou do refino
                    # (bonus bVit,readparam(bDex)/18) — isso o BONUS_MAP nao
                    # captura, entao vira efeito para nao sumir da tabela.
                    if re.fullmatch(r'-?\d+', args[0] if args else ''):
                        continue
                    desc = _expr(args[0])
                    # "conforme o refino" ja e uma frase; "DEX/18" e um valor
                    ligacao = "" if desc.startswith("conforme") else "igual a "
                    saida.append(f"{prefixo}{BONUS_MAP[tipo]} {ligacao}{desc}")
                    continue
                else:
                    txt = f"{tipo} ({', '.join(args)})"
                saida.append(f"{prefixo}{txt}")
                continue
            m = re.match(r'^skill\s+"?(\w+)"?\s*,\s*(\d+)', linha)
            if m:
                saida.append(f"{prefixo}Concede {_sk(m.group(1))} nv.{m.group(2)}")
                continue
            m = re.match(r'^(sc_start\w*)\s+(\w+)', linha)
            if m:
                saida.append(f"{prefixo}Aplica {STATUS.get(m.group(2).replace('SC_','').title(), m.group(2))}")
        return saida

    efeitos += processa(s)
    for cond, corpo in prefixos:
        efeitos += processa(corpo, f"{cond}: ")

    # remove duplicatas mantendo a ordem
    return list(dict.fromkeys(efeitos))


if __name__ == "__main__":
    import sys, io, yaml
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    from pathlib import Path

    cards = {}
    for p in [Path(r"C:\rAthena\rathena\db\pre-re\item_db_etc.yml"),
              Path(r"C:\rAthena\rathena\db\import\item_db.yml")]:
        for e in (yaml.safe_load(open(p, encoding="utf-8")).get("Body") or []):
            if e.get("Type") == "Card":
                cards[e["Id"]] = e

    for cid in (4035, 4133, 4058, 4047, 4302, 4121, 4142, 4174, 4144, 4128, 4305):
        c = cards.get(cid)
        if not c:
            continue
        print(f"[{cid}] {c['Name']}")
        for ef in describe(c.get("Script") or ""):
            print(f"     • {ef}")
        print()

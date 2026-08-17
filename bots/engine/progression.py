"""
progression.py
Jornada de classe dos bots.

Regra do servidor: nenhum bot nasce transcendente. Para chegar a LordKnight
ele precisa percorrer o mesmo caminho de um jogador — Novice, Swordman,
Knight, base 99 / job 50, renascer em Valhalla e so entao virar LordKnight.
Este modulo decide, a partir do estado atual do perfil, qual e o proximo
objetivo do bot.

O nivel base ZERA para 1 no renascimento. Um bot lv 99 Knight vira um
High Novice lv 1 — a segunda subida ate 99 e mais lenta (curva trans) mas
rende stats maiores. Por isso `peak_base_level` existe: sem ele nao da para
distinguir "Knight lv 40 subindo pela primeira vez" de "Knight lv 40 que ja
foi 99 e esta a caminho do renascimento".
"""

from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Cadeia de classes Pre-Renewal
# ─────────────────────────────────────────────────────────────────────────────
PRIMEIRA_CLASSE = {
    "Swordman", "Mage", "Archer", "Acolyte", "Merchant", "Thief",
}

# 2a classe → 1a classe de origem
ORIGEM_SEGUNDA = {
    "Knight": "Swordman",   "Crusader": "Swordman",
    "Wizard": "Mage",       "Sage": "Mage",
    "Hunter": "Archer",     "Bard": "Archer",      "Dancer": "Archer",
    "Priest": "Acolyte",    "Monk": "Acolyte",
    "Blacksmith": "Merchant", "Alchemist": "Merchant",
    "Assassin": "Thief",    "Rogue": "Thief",
}

# transcendente → 2a classe de origem
ORIGEM_TRANS = {
    "LordKnight": "Knight",   "Paladin": "Crusader",
    "HighWizard": "Wizard",   "Professor": "Sage",
    "Sniper": "Hunter",       "Clown": "Bard",       "Gypsy": "Dancer",
    "HighPriest": "Priest",   "Champion": "Monk",
    "Whitesmith": "Blacksmith", "Creator": "Alchemist",
    "SinX": "Assassin",       "Stalker": "Rogue",
}
SEGUNDA_PARA_TRANS = {v: k for k, v in ORIGEM_TRANS.items()}

# Requisitos de cada transicao
JOB_LV_MUDANCA_1A = 10   # Novice → 1a classe
JOB_LV_MUDANCA_2A = 40   # 1a → 2a classe
BASE_LV_RENASCER  = 99   # 2a classe precisa de base 99 ...
JOB_LV_RENASCER   = 50   # ... e job 50 para renascer
ZENY_RENASCER     = 1_285_000  # atalho pago da Valkyrie (Pre-RE)

# Onde cada etapa acontece
LOCAIS = {
    "job_1a":     {"Swordman": "izlude",  "Mage": "geffen_in", "Archer": "payon_in02",
                   "Acolyte": "prt_church", "Merchant": "alberta_in", "Thief": "moc_prydb1"},
    "renascer":   "valkyrie",     # Valhalla, via Metheus Sylphe em yuno_in02
    "portal_val": "yuno_in02",
}


def tier(job_name: str) -> str:
    """Retorna 'novice', 'primeira', 'segunda' ou 'trans'."""
    if job_name in ORIGEM_TRANS:
        return "trans"
    if job_name in ORIGEM_SEGUNDA:
        return "segunda"
    if job_name in PRIMEIRA_CLASSE:
        return "primeira"
    return "novice"


def caminho_ate(job_alvo: str) -> list[str]:
    """
    Sequencia completa de classes ate o alvo, comecando em Novice.
    caminho_ate("LordKnight") -> [Novice, Swordman, Knight, LordKnight]
    """
    if job_alvo in ORIGEM_TRANS:
        segunda = ORIGEM_TRANS[job_alvo]
        return ["Novice", ORIGEM_SEGUNDA[segunda], segunda, job_alvo]
    if job_alvo in ORIGEM_SEGUNDA:
        return ["Novice", ORIGEM_SEGUNDA[job_alvo], job_alvo]
    if job_alvo in PRIMEIRA_CLASSE:
        return ["Novice", job_alvo]
    return ["Novice"]


def proximo_objetivo(job_name: str, base_level: int, job_level: int,
                     zeny: int = 0, job_alvo: Optional[str] = None,
                     renasceu: bool = False) -> dict:
    """
    Decide o que o bot deve fazer agora.

    Retorna {acao, alvo, motivo, local, pronto} — `pronto` indica se os
    requisitos ja foram atingidos (o bot deve viajar e executar) ou se ainda
    falta subir de nivel.
    """
    t = tier(job_name)
    alvo = job_alvo or job_name

    # ── Novice: virar 1a classe ──────────────────────────────────────────
    if t == "novice":
        destino = caminho_ate(alvo)[1] if len(caminho_ate(alvo)) > 1 else "Swordman"
        pronto = job_level >= JOB_LV_MUDANCA_1A
        return {
            "acao": "mudar_classe", "alvo": destino,
            "local": LOCAIS["job_1a"].get(destino, "prontera"),
            "pronto": pronto,
            "motivo": (f"job {job_level}/{JOB_LV_MUDANCA_1A} para virar {destino}"
                       if not pronto else f"pronto para virar {destino}"),
        }

    # ── 1a classe: virar 2a classe ───────────────────────────────────────
    if t == "primeira":
        caminho = caminho_ate(alvo)
        destino = caminho[2] if len(caminho) > 2 else alvo
        pronto = job_level >= JOB_LV_MUDANCA_2A
        return {
            "acao": "mudar_classe", "alvo": destino, "local": "prontera",
            "pronto": pronto,
            "motivo": (f"job {job_level}/{JOB_LV_MUDANCA_2A} para virar {destino}"
                       if not pronto else f"pronto para virar {destino}"),
        }

    # ── 2a classe ────────────────────────────────────────────────────────
    if t == "segunda":
        # O alvo e transcendente? Entao 99/50 e renascer.
        if alvo in ORIGEM_TRANS or SEGUNDA_PARA_TRANS.get(job_name) == alvo:
            if base_level < BASE_LV_RENASCER or job_level < JOB_LV_RENASCER:
                return {
                    "acao": "upar", "alvo": f"base {BASE_LV_RENASCER}/job {JOB_LV_RENASCER}",
                    "local": None, "pronto": False,
                    "motivo": f"base {base_level}/{BASE_LV_RENASCER}, "
                              f"job {job_level}/{JOB_LV_RENASCER} para renascer",
                }
            if zeny < ZENY_RENASCER:
                return {
                    "acao": "juntar_zeny", "alvo": ZENY_RENASCER, "local": None,
                    "pronto": False,
                    "motivo": f"{zeny:,}z de {ZENY_RENASCER:,}z para o renascimento",
                }
            return {
                "acao": "renascer", "alvo": SEGUNDA_PARA_TRANS.get(job_name, alvo),
                "local": LOCAIS["portal_val"], "pronto": True,
                "motivo": "99/50 e zeny suficientes — renascer em Valhalla",
            }
        # Alvo e a propria 2a classe: so upar
        return {"acao": "upar", "alvo": "base 99", "local": None, "pronto": False,
                "motivo": f"base {base_level}/99 na classe final"}

    # ── Transcendente: jornada concluida ─────────────────────────────────
    return {
        "acao": "upar", "alvo": "base 99", "local": None,
        "pronto": base_level >= 99,
        "motivo": ("jornada concluida, no nivel maximo" if base_level >= 99
                   else f"base {base_level}/99 como transcendente"),
    }


def resumo_jornada(job_name: str, base_level: int, job_alvo: Optional[str] = None,
                   renasceu: bool = False) -> str:
    """Linha legivel do progresso: Novice > Swordman > [Knight] > LordKnight"""
    alvo = job_alvo or job_name
    caminho = caminho_ate(alvo)
    partes = []
    achou_atual = False
    for c in caminho:
        if c == job_name and not achou_atual:
            partes.append(f"[{c} lv{base_level}]")
            achou_atual = True
        else:
            partes.append(c)
    return " > ".join(partes)


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    casos = [
        ("Novice",     8,  8,        0, "LordKnight"),
        ("Swordman",  35, 32,    50_000, "LordKnight"),
        ("Knight",    72, 44,   300_000, "LordKnight"),
        ("Knight",    99, 50,   400_000, "LordKnight"),
        ("Knight",    99, 50, 2_000_000, "LordKnight"),
        ("LordKnight",85, 60, 1_000_000, "LordKnight"),
    ]
    print(f"{'classe':12s} {'base':>4} {'job':>4} {'zeny':>10}  {'acao':14s} motivo")
    print("-" * 96)
    for jn, bl, jl, z, alvo in casos:
        o = proximo_objetivo(jn, bl, jl, z, alvo)
        print(f"{jn:12s} {bl:4d} {jl:4d} {z:10,d}  {o['acao']:14s} {o['motivo']}")
    print()
    print(resumo_jornada("Knight", 72, "LordKnight"))

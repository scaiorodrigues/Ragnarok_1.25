# Ragnarok 1.25 — Servidor Hardcore Pre-Renewal

> Servidor de Ragnarok Online **Pre-Renewal com morte permanente**, construído
> sobre o [rAthena](https://github.com/rathena/rathena). Acompanha um motor de
bots que simulam jogadores, para que um servidor pequeno tenha economia,
mercado e movimento.

> Fork do rAthena, distribuído sob **GPLv3** — a mesma licença do original.
> A documentação do upstream continua em [`README_UPSTREAM.md`](README_UPSTREAM.md).

---

## A ideia

Morrer apaga o personagem. Não há ressurreição por skill, não há Kafra
guardando seu progresso de volta. A única forma de trazer alguém de volta é
uma Folha de Yggdrasil, e ela dropa de sete MVPs a 0,01%.

Isso muda como se joga: preparar-se importa mais que reagir, e cada decisão
carrega peso.

---

## O que muda em relação ao rAthena

### Morte permanente

Ao morrer, o personagem é marcado e **não pode mais ser selecionado**. Três
colunas em `char` sustentam isso (`sql-files/hardcore_columns.sql`):

| Coluna | Função |
|---|---|
| `hardcore_dead` | Personagem morto permanentemente |
| `guardian_angel_used` | Carta Osiris já consumida |
| `osiris_resurrect_time` | Fim do Limbo de Osiris |

A **Carta Osiris** é o seguro: em vez da morte definitiva, o personagem entra
em Limbo por 24 h e volta sozinho. A carta é consumida no processo.

### Ressurreição: só a Folha de Yggdrasil

Todas as rotas normais foram fechadas — `ALL_RESURRECTION` fora das árvores de
Priest, Alchemist e Creator; `PR_REDEMPTIO` removida; Abracadabra não sorteia
mais ressurreição; Holy Egg virou item de cura.

Ao usar a Folha, o jogador vê a lista de personagens mortos **da própria
conta** e escolhe um para voltar. O item só é consumido quando a ressurreição
acontece — cancelar ou não ter mortos não gasta a folha.

Ela não é vendida por NPC e saiu dos 9 mobs comuns que a dropavam. Agora vem
de **7 MVPs a 0,01%**: Osiris, Angeling, Deviling, Valkyrie Randgris, Memory of
Thanatos, Lord of the Dead e Dark Lord.

### Encantamento de equipamento

Todo equipamento — de drop, quest, loja ou craft — nasce com **um
encantamento aleatório**. As outras quatro posições ficam fechadas.

**Só o ferreiro abre as demais.** Refinando com `WS_WEAPONREFINE`, uma posição
nova a cada 2 níveis: `+2`, `+4`, `+6`, `+8`. É a única skill de refino do
jogo, então a linha Blacksmith → Whitesmith ganha um papel econômico real —
sem um deles, ninguém passa de um encantamento.

O pool não é global: cada família de equipamento tem o seu, então uma espada
nunca sorteia encantamento de cajado.

| Tema | Aplica a |
|---|---|
| Lâmina | espadas de uma e duas mãos |
| Precisão | adagas e katares |
| Pontaria | arcos |
| Arcano | cajados e livros |
| Impacto | maças e manoplas |
| Peso | lanças e machados |
| Harmonia | instrumentos e chicotes |
| Couraça · Guarda · Manto · Passo · Talismã · Elmo | armaduras por slot |

### Refino não destrói

Falhar no refino **nunca quebra o equipamento** — consome o material e devolve
um nível. Vale para os NPCs refinadores e para a skill do Blacksmith. O mesmo
no Socket Enchant: a falha leva só os materiais.

### Maestria por raça

A cada 10.000 abates de uma raça, +1% de dano contra ela e +1% de redução do
dano dela. Cinco títulos por tier, de Caçador a Nêmesis. Consulta com o Mestre
das Crônicas, em Prontera.

### Outros

Refino seguro até +7 com Pedra de Proteção, cura gradual, chave de Thanatos,
buffs de mercenário, 17 variantes de carta com bônus fixos (o nome mostra o
bônus antes de encaixar) e 16 combos — 8 de carta e 8 conjuntos temáticos por
classe montados só com equipamento de NPC.

---

## Bots

O motor vive em [`bots/`](bots/). Ele decide o que cada bot caça, compra, vende
e equipa, a partir de **63 variações de build** Pre-Renewal documentadas em
guias da comunidade — incluindo 24 exóticas como LordKnight Spiral, HighPriest
Turn Undead, Sniper Trap e Creator Vanilmirth.

Três pontos de desenho:

**Cartas com bônus condicional.** 63% das cartas Pre-RE dão efeito contra uma
raça ou elemento específico. O motor pontua esses bônus contra a distribuição
real dos alvos que a build caça — uma Hydra Card vale muito para quem farma
Demi-humanos e zero para quem farma Mortos-vivos.

**Jornada de classe.** Nenhum bot nasce transcendente. Para chegar a
LordKnight ele passa por Novice, Swordman, Knight, alcança base 99 / job 50,
junta 1.285.000 z e renasce em Valhalla — o mesmo caminho de um jogador.

**A lista de bots é local.** Cada servidor gera a sua com
`engine/profile_generator.py`. Os 77 perfis versionados são exemplo, e as
credenciais nos `config.txt` são placeholder: defina as suas antes de subir.

Para testar sem carregar a frota inteira, veja
[`bots/README_TESTE.md`](bots/README_TESTE.md) — um recorte de 10 bots que
cobre os três tiers de classe e todos os arquétipos.

---

## Instalação

**1. Banco**

```bash
mysql -u root -p < sql-files/main.sql
mysql -u root -p < sql-files/logs.sql
mysql -u root -p < sql-files/hardcore_columns.sql
```

O `main.sql` tem o bloco `CREATE USER` comentado — descomente e defina a senha,
ou crie o usuário à mão.

**2. Credenciais**

`conf/import/` está fora do versionamento: cada servidor tem as suas. Copie de
`conf/import-tmpl/` e preencha o `inter_conf.txt`.

**3. Rede local**

Para jogar em LAN, defina em `conf/import/`:

```
// char_conf.txt
login_ip: <IP de LAN desta maquina>
char_ip:  <IP de LAN desta maquina>

// map_conf.txt
char_ip: <IP de LAN desta maquina>
map_ip:  <IP de LAN desta maquina>
```

Deixe `bind_ip` sem definir, para o servidor escutar em todas as interfaces —
assim atende tanto os bots em `127.0.0.1` quanto os clientes da rede.

Rodando muitos bots, relaxe o anti-DDoS em `conf/import/packet_conf.txt`. O
padrão trata 5 conexões em 3 s como ataque, e todos os bots vêm do mesmo IP:

```
ddos_count: 200
```

**4. Compilar**

Há alterações em `src/` (`skill.cpp`, `script.cpp`, `mob.cpp`, `itemdb.cpp`,
`clif.cpp`, `pc.cpp`, `char.cpp`), então **compilar é obrigatório** — trocar
apenas os arquivos de configuração não basta.

No Windows, abra `rAthena.sln` no Visual Studio 2022 e compile em `x64`. No
Linux:

```bash
./configure && make server
```

---

## Requisitos

MySQL/MariaDB, e um cliente Ragnarok compatível com `PACKETVER 20211103`
(definido em `src/config/packets.hpp`).

---

## Licença

GPLv3, herdada do rAthena. Veja [`LICENSE`](LICENSE).

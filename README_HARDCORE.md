# Ragnarok Hardcore — Pre-Renewal

Servidor Pre-Renewal com **morte permanente**, construído sobre o
[rAthena](https://github.com/rathena/rathena). Acompanha uma frota de bots que
simulam jogadores, para que um servidor pequeno tenha economia e movimento.

> Fork do rAthena, distribuído sob **GPLv3** — a mesma licença do projeto
> original. Ao redistribuir modificações, o código-fonte precisa continuar
> disponível.

---

## O que muda em relação ao rAthena padrão

### Morte permanente

Quando um personagem morre, ele é marcado como morto e **não pode mais ser
selecionado** na tela de personagens. Três colunas novas em `char`
(`sql-files/hardcore_columns.sql`):

| Coluna | Função |
|---|---|
| `hardcore_dead` | Personagem morto permanentemente |
| `guardian_angel_used` | Carta Osiris já foi consumida |
| `osiris_resurrect_time` | Timestamp do fim do Limbo de Osiris |

**Carta Osiris** funciona como seguro: em vez da morte definitiva, o
personagem entra em Limbo por 24h e volta sozinho. A carta é consumida.

### Ressurreição: só a Folha de Yggdrasil

Todas as rotas normais de ressurreição estão fechadas:

- `ALL_RESURRECTION` fora das árvores de Priest, Alchemist e Creator
- `PR_REDEMPTIO` removida de Priest e High Priest
- Abracadabra não sorteia mais ressurreição
- Holy Egg virou item de cura

A **Folha de Yggdrasil** é o único caminho. Ao usá-la, o jogador vê a lista de
personagens mortos da própria conta e escolhe um para voltar. O item só é
consumido quando a ressurreição acontece de fato — cancelar ou não ter mortos
não gasta a folha.

Ela deixou de ser vendida por NPC e saiu dos 9 mobs comuns que a dropavam.
Agora vem de **7 MVPs a 0,01%**, o tier mais raro do servidor:

> Osiris · Angeling · Deviling · Valkyrie Randgris · Memory of Thanatos ·
> Lord of the Dead · Dark Lord

### Outras mecânicas

Refino seguro, cura gradual, chave de Thanatos, buffs de mercenário e 17
variantes de carta com bônus fixos (o nome da carta mostra o bônus antes de
encaixar).

---

## Instalação

**1. Banco**

```bash
mysql -u root -p < sql-files/main.sql
mysql -u root -p < sql-files/logs.sql
mysql -u root -p < sql-files/hardcore_columns.sql
```

O `main.sql` tem o bloco `CREATE USER` comentado — descomente e defina a senha,
ou crie o usuário manualmente.

**2. Credenciais**

`conf/import/` está fora do versionamento: cada servidor tem as suas. Copie de
`conf/import-tmpl/` e preencha `inter_conf.txt` com os dados do banco.

**3. Rede**

Para jogar em LAN, defina em `conf/import/`:

```
// char_conf.txt
login_ip: <IP de LAN desta maquina>
char_ip:  <IP de LAN desta maquina>

// map_conf.txt
char_ip: <IP de LAN desta maquina>
map_ip:  <IP de LAN desta maquina>
```

Deixe `bind_ip` sem definir para o servidor escutar em todas as interfaces —
assim atende tanto os bots em `127.0.0.1` quanto os clientes da rede.

Se for rodar muitos bots, relaxe o anti-DDoS em `conf/import/packet_conf.txt`.
O padrão trata 5 conexões em 3s como ataque, e todos os bots vêm do mesmo IP:

```
ddos_count: 200
```

**4. Compilar**

Há alterações em `src/` (`resurrection.cpp`, `pc.cpp`, `char.cpp`,
`char_clif.cpp`, `mmo.hpp`), então compilar é obrigatório — não basta trocar
os arquivos de configuração.

---

## Bots

O motor vive em `../bots/` (repositório separado). Ele decide o que cada bot
caça, compra, vende e equipa, a partir de **63 variações de build**
Pre-Renewal documentadas em guias da comunidade — incluindo builds exóticas
como LordKnight Spiral, HighPriest Turn Undead e Sniper Trap.

Dois pontos de desenho:

**Cartas com bônus condicional.** 63% das cartas Pre-RE dão efeito contra uma
raça ou elemento específico. O motor pontua esses bônus contra a distribuição
real dos alvos que a build caça — uma Hydra Card vale muito para quem farma
Demihuman e zero para quem farma Undead.

**Jornada de classe.** Nenhum bot nasce transcendente. Para chegar a
LordKnight ele passa por Novice, Swordman, Knight, alcança base 99 / job 50,
junta 1.285.000z e renasce em Valhalla — o mesmo caminho de um jogador.

**A lista de bots é local.** Cada servidor gera a sua com
`engine/profile_generator.py`. Os perfis versionados são exemplos.

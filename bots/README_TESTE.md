# Ambiente de teste — 10 bots

Recorte da frota completa (77 bots) para validar o servidor sem carregar
tudo de uma vez. Os 10 foram escolhidos para cobrir os três tiers de classe,
todos os arquétipos de combate e duas builds exóticas.

| Bot | Nv | Papel no teste |
|---|---|---|
| HC_Novice01 | 10 | Progressão inicial, menor nível da frota |
| HC_Merchant01 | 40 | **Mercado**: vending, loja, trade entre bots |
| HC_Knight_STR01 | 70 | 2ª classe corpo a corpo |
| HC_Priest_Supp01 | 72 | 2ª classe suporte: party e buffs |
| HC_Wizard_INT01 | 68 | 2ª classe conjurador |
| HC_Hunter_DEX01 | 74 | 2ª classe à distância |
| HC_LK_STR01 | 85 | Transcendente corpo a corpo |
| HC_HW_INT01 | 84 | Transcendente conjurador |
| HC_Sniper_Trap01 | 84 | Exótica: dano por DEX+INT, ignora ATK |
| HC_Creator_FCP01 | 84 | Exótica: slave puro, STR 1 / DEX 99 |

## Antes de subir

**1. Servidores no ar.** `login`, `char` e `map`. O `web-server` **não** é mais
necessário — `use_web_auth_token` foi desligado.

**2. Contas.** Criadas automaticamente: o usuário de cada bot termina em `_M`
e o `login_athena.conf` está com `new_account: yes`. Senha comum: `TROQUE_ESTA_SENHA`.

**3. Personagens — passo manual.** O OpenKore cria a conta, mas **não cria o
personagem**. Na primeira execução cada bot vai logar e parar na seleção de
personagem. Duas saídas:

- Criar os 10 pelo cliente do jogo (login com `HC_Novice01_M` / `TROQUE_ESTA_SENHA`,
  criar o char com o nome exato da tabela acima), ou
- Inserir direto na tabela `char` por SQL.

O nome do personagem precisa bater **exatamente** com a linha `char` do
`config.txt` de cada bot.

## Subir e parar

```
start_test10.bat     sobe os 10, em janelas separadas, 4s entre cada
stop_bots.bat        encerra tudo (mata todos os perl.exe)
```

O intervalo de 4s não é por causa do anti-DDoS (`ddos_count` já está em 200) —
é para não saturar CPU e disco subindo 10 interpretadores Perl de uma vez.

## Voltar para a frota completa

Nada foi removido: os 77 perfis continuam em `profiles/` e as 77 pastas de bot
intactas. Para rodar tudo, basta um launcher com a lista completa. Os outros 67
ainda não têm credenciais no `config.txt` — só os 10 de teste receberam.

## Escopo

`config/known_bots.txt` lista apenas estes 10. É o que `PartyManager` e
`TradeHandler` usam para decidir de quem aceitar party e trade — durante o
teste os bots só interagem entre si.

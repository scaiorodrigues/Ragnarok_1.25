###########################################################################
# TradeHandler.pm
# Lê comandos do orquestrador em dynamic.txt e executa trades:
#   - go_vend: abre vending shop no ponto de comércio (só merchants)
#   - open_chat: abre sala de chat WTS no ponto de comércio
#   - buy_vend: vai até vend shop e compra item
#   - buy_from_chat: vai até sala de chat e inicia trade direto
###########################################################################

package TradeHandler;

use strict;
use warnings;
use Plugins;
use Globals qw($char $net %venderLists %chatRooms $field $accountID);
use Log qw(message error debug);
use Network::Send ();
use Utils qw(timeOut);
use JSON::PP;

my $BOTS_DIR = 'C:/rAthena/bots';
my $DYNAMIC_FILE;        # definido no on_start
my $last_mtime = 0;
my $CHECK_INTERVAL = 3;  # segundos
my $last_check     = 0;
my %timers;

Plugins::register('TradeHandler', 'Executa comandos de trade do orquestrador', \&on_unload);

my $hooks = Plugins::addHooks(
    ['start3',             \&on_start],
    ['AI_pre',             \&on_ai_pre],
    ['AI_pre',             \&_tick_timers],
    ['packet_trade_add',   \&on_trade_add],
    ['packet_trade_ok',    \&on_trade_ok],
    ['packet_chat_join',   \&on_chat_join],
);

sub on_unload { Plugins::delHooks($hooks) }

# ---------------------------------------------------------------------------
# Inicialização — descobrir nome do bot via char name
# ---------------------------------------------------------------------------
sub on_start {
    return unless $char;
    my $bot_name = $char->{name} // 'unknown';
    $DYNAMIC_FILE = "$BOTS_DIR/$bot_name/macros/dynamic.txt";
    message "[TradeHandler] Iniciado para $bot_name. Lendo: $DYNAMIC_FILE\n", 'info';
}

# ---------------------------------------------------------------------------
# Hook: AI_pre — verificar comandos periodicamente
# ---------------------------------------------------------------------------
sub on_ai_pre {
    # Tentar iniciar se ainda não foi
    unless ($DYNAMIC_FILE) {
        on_start();
        return;
    }

    my $now = time();
    return if ($now - $last_check) < $CHECK_INTERVAL;
    $last_check = $now;

    return unless -f $DYNAMIC_FILE;

    my $mtime = (stat $DYNAMIC_FILE)[9];
    return if $mtime == $last_mtime;
    $last_mtime = $mtime;

    _process_command_file();
}

# ---------------------------------------------------------------------------
# Processar arquivo de comandos
# ---------------------------------------------------------------------------
sub _process_command_file {
    open(my $fh, '<:encoding(UTF-8)', $DYNAMIC_FILE) or do {
        error "[TradeHandler] Não conseguiu abrir $DYNAMIC_FILE: $!\n";
        return;
    };
    my @lines = <$fh>;
    close $fh;

    for my $line (@lines) {
        chomp $line;
        $line =~ s/^\s+|\s+$//g;
        next if !$line || $line =~ /^#/;

        if ($line =~ /^go_vend\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)/) {
            my ($map, $x, $y, $item_id, $price) = ($1, $2, $3, $4, $5);
            _cmd_go_vend($map, $x, $y, $item_id, $price);

        } elsif ($line =~ /^open_chat\s+(.+?)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)/) {
            my ($title, $map, $x, $y, $item_id, $price, $duration) = ($1, $2, $3, $4, $5, $6, $7);
            _cmd_open_chat($title, $map, $x, $y, $item_id, $price, $duration);

        } elsif ($line =~ /^buy_vend\s+(\S+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d+)/) {
            my ($vendor_id, $item_id, $qty, $map, $x, $y) = ($1, $2, $3, $4, $5, $6);
            _cmd_buy_vend($vendor_id, $item_id, $qty, $map, $x, $y);

        } elsif ($line =~ /^buy_from_chat\s+(\S+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d+)/) {
            my ($owner_id, $item_id, $price, $map, $x, $y) = ($1, $2, $3, $4, $5, $6);
            _cmd_buy_from_chat($owner_id, $item_id, $price, $map, $x, $y);

        } elsif ($line =~ /^party_create\s+(.+)/) {
            # Delegar para PartyManager via arquivo
        } elsif ($line =~ /^party_accept\s+(\S+)/) {
            # Delegar para PartyManager
        }
    }

    # Limpar arquivo após processar
    _clear_file();
}

# ---------------------------------------------------------------------------
# Comandos de venda
# ---------------------------------------------------------------------------

sub _cmd_go_vend {
    my ($map, $x, $y, $item_id, $price) = @_;
    message "[TradeHandler] go_vend → $map ($x,$y) item=$item_id preço=$price\n", 'info';

    _navigate_to($map, $x, $y, sub {
        # Colocar item na vending shop
        if ($char && $char->{skills}{MC_VENDING}) {
            # Abre janela de vending
            $net->sendSkillUse(MC_VENDING(), 1, $char->{ID});
            # O jogador configura os itens via interface — aqui apenas log
            message "[TradeHandler] Vending shop aberta. Item $item_id a $price z.\n", 'info';
        } else {
            error "[TradeHandler] Bot não tem habilidade MC_VENDING\n";
        }
    });
}

sub _cmd_open_chat {
    my ($title, $map, $x, $y, $item_id, $price, $duration) = @_;
    message "[TradeHandler] open_chat → '$title' em $map ($x,$y)\n", 'info';

    _navigate_to($map, $x, $y, sub {
        # Criar sala de chat pública WTS
        # Pacote: CA_CHAT_ROOM_CREATE ou equivalente
        $net->sendChatRoomCreate($title, 0, 0, '') if $net->can('sendChatRoomCreate');
        message "[TradeHandler] Chat '$title' criado. Aguardando comprador...\n", 'info';

        # Fechar chat após $duration segundos
        if ($duration && $duration > 0) {
            $timers{chat_close} = {
                time   => time(),
                delay  => $duration,
                action => sub {
                    $net->sendChatRoomLeave() if $net->can('sendChatRoomLeave');
                    message "[TradeHandler] Chat encerrado após $duration s.\n", 'info';
                },
            };
        }
    });
}

# ---------------------------------------------------------------------------
# Comandos de compra
# ---------------------------------------------------------------------------

sub _cmd_buy_vend {
    my ($vendor_id, $item_id, $qty, $map, $x, $y) = @_;
    message "[TradeHandler] buy_vend → vendor=$vendor_id item=$item_id x$qty\n", 'info';

    _navigate_to($map, $x, $y, sub {
        my $vendor = $venderLists{$vendor_id};
        unless ($vendor) {
            error "[TradeHandler] Vendor $vendor_id não encontrado no range\n";
            return;
        }

        # Encontrar index do item na loja
        for my $itm (@{$vendor->{items} // []}) {
            if (($itm->{nameID} // 0) == $item_id) {
                $net->sendBuyBulkVender($vendor_id, [[$itm->{index}, $qty]])
                    if $net->can('sendBuyBulkVender');
                message "[TradeHandler] Comprando item $item_id x$qty da loja $vendor_id\n", 'info';
                last;
            }
        }
    });
}

sub _cmd_buy_from_chat {
    my ($owner_id, $item_id, $price, $map, $x, $y) = @_;
    message "[TradeHandler] buy_from_chat → owner=$owner_id item=$item_id preço=$price\n", 'info';

    _navigate_to($map, $x, $y, sub {
        # Entrar na sala de chat do vendedor
        my $room = _find_chat_by_owner($owner_id);
        unless ($room) {
            error "[TradeHandler] Chat de $owner_id não encontrado\n";
            return;
        }

        $net->sendChatRoomJoin($room->{ID}, '') if $net->can('sendChatRoomJoin');
        message "[TradeHandler] Entrou no chat de $owner_id. Aguardando trade...\n", 'info';

        # Guardar intenção de compra para on_trade_add
        $timers{pending_buy} = {
            owner_id => $owner_id,
            item_id  => $item_id,
            price    => $price,
        };
    });
}

# ---------------------------------------------------------------------------
# Hooks de pacotes de trade
# ---------------------------------------------------------------------------

sub on_trade_add {
    my (undef, $args) = @_;
    # Verificar se a troca corresponde ao item que queremos
    my $pending = $timers{pending_buy};
    return unless $pending;

    message "[TradeHandler] Recebeu item em trade. Verificando...\n", 'debug';
    # Aceitar o trade — a verificação de preço já foi feita pelo orquestrador
    $net->sendTradeAdd($pending->{item_id}, 1, $pending->{price})
        if $net->can('sendTradeAdd');
}

sub on_trade_ok {
    my (undef, $args) = @_;
    message "[TradeHandler] Trade confirmado!\n", 'info';
    delete $timers{pending_buy};
    $net->sendTradeCommit() if $net->can('sendTradeCommit');
}

sub on_chat_join {
    my (undef, $args) = @_;
    # Quando alguém entra na nossa sala de chat, podemos iniciar trade
    # O vendedor (nós) envia o item para o comprador
    my $pending = $timers{pending_sale};
    return unless $pending;

    message "[TradeHandler] Comprador entrou no chat. Iniciando trade...\n", 'info';
    my $buyer_id = $args->{ID} // '';
    if ($buyer_id) {
        $net->sendTradeRequest($buyer_id) if $net->can('sendTradeRequest');
    }
}

# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

sub _navigate_to {
    my ($map, $x, $y, $callback) = @_;

    return unless $char && $field;

    my $current_map = $field->name();
    if ($current_map ne $map) {
        # Usar teleport/walk para o mapa correto
        # Simplificado: escrever waypoint no log e esperar AI de movimento
        message "[TradeHandler] Navegando para $map ($x,$y)...\n", 'info';
        # Na prática, o AI_route do OpenKore cuida disso via lockMap
        # Escrevemos o destino no arquivo de rota
        _write_route($map, $x, $y, $callback);
    } else {
        # Já no mapa certo — apenas andar até as coordenadas
        $net->sendMove($x, $y) if $net->can('sendMove');
        # Executar callback após delay curto
        $timers{nav_callback} = {
            time   => time(),
            delay  => 3,
            action => $callback,
        };
    }
}

sub _write_route {
    my ($map, $x, $y, $callback) = @_;
    return unless $DYNAMIC_FILE;

    my $bot_name = ($char ? $char->{name} : 'unknown');
    my $route_file = "$BOTS_DIR/$bot_name/route_target.txt";

    open(my $fh, '>:encoding(UTF-8)', $route_file) or return;
    print $fh "map=$map x=$x y=$y\n";
    close $fh;

    # Callback armazenado para executar quando chegarmos
    $timers{route_callback} = {
        map    => $map,
        x      => $x,
        y      => $y,
        action => $callback,
    };
}

sub _find_chat_by_owner {
    my ($owner_id) = @_;
    for my $id (keys %chatRooms) {
        my $room = $chatRooms{$id};
        # Match by binary ownerID or by ownerName (for bot-to-bot trades)
        return $room if ($room->{ownerID}   // '') eq $owner_id;
        return $room if ($room->{ownerName} // '') eq $owner_id;
    }
    return undef;
}

sub _clear_file {
    return unless $DYNAMIC_FILE;
    open(my $fh, '>:encoding(UTF-8)', $DYNAMIC_FILE) or return;
    print $fh "# aguardando comandos\n";
    close $fh;
    $last_mtime = (stat $DYNAMIC_FILE)[9] // 0;
}

sub _tick_timers {
    my $now = time();
    for my $key (keys %timers) {
        my $t = $timers{$key};
        next unless ref($t) eq 'HASH' && $t->{time} && $t->{delay} && $t->{action};
        if ($now - $t->{time} >= $t->{delay}) {
            $t->{action}->();
            delete $timers{$key};
        }
    }
}

1;

###########################################################################
# MarketScanner.pm
# Escaneia vending shops e chat rooms no range do ponto de comercio.
# Salva em market/vends.json e market/chats.json para o orquestrador.
###########################################################################

package MarketScanner;

use strict;
use warnings;
use Plugins;
use Settings;
use Globals qw($char %venderLists %chatRooms $field);
use Log qw(message debug);
use Commands;
use JSON::PP;
use File::Path qw(make_path);
use Encode qw(decode encode);

my $BOTS_DIR    = 'C:/rAthena/bots';
my $MARKET_DIR  = "$BOTS_DIR/market";
my $SCAN_RADIUS = 25;    # celulas de raio para escanear
my $SCAN_INTERVAL = 10;  # segundos entre scans
my $last_scan   = 0;

# Pontos de comercio fixos (mapa → [x, y])
my %TRADE_POINTS = (
    'prontera' => [156, 183],
    'payon'    => [177, 108],
    'geffen'   => [120,  72],
    'morocc'   => [157, 103],
    'alberta'  => [119,  60],
);

Plugins::register('MarketScanner', 'Escaneia mercado e salva JSON', \&on_unload);

my $hooks = Plugins::addHooks(
    ['AI_pre',                    \&on_ai_pre],
    ['packet_vender_items_list',  \&on_vend_list],
    ['packet_chat_info',          \&on_chat_info],
);

make_path($MARKET_DIR) unless -d $MARKET_DIR;

sub on_unload { Plugins::delHooks($hooks) }

# ---------------------------------------------------------------------------
# Hook: AI_pre — rodar scanner periodicamente
# ---------------------------------------------------------------------------
sub on_ai_pre {
    my $now = time();
    return if ($now - $last_scan) < $SCAN_INTERVAL;
    $last_scan = $now;

    return unless $char && $field;
    my $map = $field->name();
    return unless exists $TRADE_POINTS{$map};

    my ($tp_x, $tp_y) = @{$TRADE_POINTS{$map}};
    my $dist = _distance($char->{pos_to}{x}, $char->{pos_to}{y}, $tp_x, $tp_y);

    if ($dist <= $SCAN_RADIUS) {
        _scan_vends();
        _scan_chats();
        debug "[MarketScanner] Scan concluido em $map ($dist celulas do ponto)\n", 'market';
    }
}

# ---------------------------------------------------------------------------
# Hook: packet_vender_items_list — dados de uma vend shop
# ---------------------------------------------------------------------------
sub on_vend_list {
    my (undef, $args) = @_;
    my $vendor_id = $args->{ID};
    return unless $vendor_id;

    my $vendor = $venderLists{$vendor_id};
    return unless $vendor && ref($vendor->{items}) eq 'ARRAY';

    my @items;
    for my $itm (@{$vendor->{items}}) {
        push @items, {
            item_id    => $itm->{nameID}  // 0,
            item_name  => $itm->{name}    // '',
            price      => $itm->{price}   // 0,
            amount     => $itm->{amount}  // 1,
            index      => $itm->{index}   // 0,
        };
    }

    _update_vends_file($vendor_id, $vendor, \@items);
}

# ---------------------------------------------------------------------------
# Hook: packet_chat_info — sala de chat visivel
# ---------------------------------------------------------------------------
sub on_chat_info {
    my (undef, $args) = @_;
    my $title = $args->{title} // '';

    # Filtrar apenas salas WTS
    return unless $title =~ /WTS\s+\[?(.+?)\]?\s+(\d+)z?/i;
    my ($item_name, $price) = ($1, int($2));

    _update_chats_file($args, $item_name, $price);
}

# ---------------------------------------------------------------------------
# Funções internas
# ---------------------------------------------------------------------------

sub _scan_vends {
    return unless %venderLists;
    for my $id (keys %venderLists) {
        # Solicitar lista de itens (se ainda não carregada)
        my $vendor = $venderLists{$id};
        next unless $vendor;
        next if $vendor->{items} && scalar @{$vendor->{items}};
        # Envia pacote de request
        if ($char && $vendor->{pos}) {
            my $dist = _distance(
                $char->{pos_to}{x}, $char->{pos_to}{y},
                $vendor->{pos}{x},  $vendor->{pos}{y}
            );
            Commands::run("vender $id") if $dist <= $SCAN_RADIUS;
        }
    }
}

sub _scan_chats {
    return unless %chatRooms;
    for my $id (keys %chatRooms) {
        my $room = $chatRooms{$id};
        next unless $room && $room->{title};
        # já processado em on_chat_info
    }
}

sub _update_vends_file {
    my ($vendor_id, $vendor, $items) = @_;
    return unless @$items;

    my $path    = "$MARKET_DIR/vends.json";
    my $current = _read_json($path) // [];

    # Remover entrada antiga do mesmo vendor
    @$current = grep { ($_->{vendor_id} // '') ne "$vendor_id" } @$current;

    push @$current, {
        vendor_id   => "$vendor_id",
        vendor_name => $vendor->{name}  // '',
        map         => ($field ? $field->name() : 'unknown'),
        x           => $vendor->{pos}{x} // 0,
        y           => $vendor->{pos}{y} // 0,
        items       => $items,
        updated_at  => time(),
    };

    _write_json($path, $current);
}

sub _update_chats_file {
    my ($args, $item_name, $price) = @_;

    my $path    = "$MARKET_DIR/chats.json";
    my $current = _read_json($path) // [];

    my $owner_id = $args->{ownerID} // '';
    @$current = grep { ($_->{owner_id} // '') ne "$owner_id" } @$current;

    push @$current, {
        owner_id   => "$owner_id",
        owner_name => $args->{ownerName} // '',
        map        => ($field ? $field->name() : 'unknown'),
        x          => $args->{x}  // 0,
        y          => $args->{y}  // 0,
        title      => $args->{title} // '',
        item_name  => $item_name,
        price      => $price,
        updated_at => time(),
    };

    _write_json($path, $current);
}

sub _read_json {
    my ($path) = @_;
    return undef unless -f $path;
    open(my $fh, '<:encoding(UTF-8)', $path) or return undef;
    local $/;
    my $content = <$fh>;
    close $fh;
    eval { decode_json($content) };
}

sub _write_json {
    my ($path, $data) = @_;
    open(my $fh, '>:encoding(UTF-8)', $path) or do {
        message "[MarketScanner] Erro ao escrever $path: $!\n", 'error';
        return;
    };
    print $fh JSON::PP->new->utf8->pretty->encode($data);
    close $fh;
}

sub _distance {
    my ($x1, $y1, $x2, $y2) = @_;
    return abs($x1 - $x2) + abs($y1 - $y2);  # Manhattan distance
}

1;

###########################################################################
# PartyManager.pm
# Gerencia parties entre bots no mesmo mapa.
# Lê comandos do orquestrador em dynamic.txt:
#   - party_create <member1> [member2...]: lider cria e convida membros
#   - party_accept <leader_name>: membro aceita convite pendente
#   - party_leave: sair da party atual
###########################################################################

package PartyManager;

use strict;
use warnings;
use Plugins;
use Globals qw($char $net %players %party $field);
use Log qw(message error debug);
use JSON::PP;

my $BOTS_DIR       = 'C:/rAthena/bots';
my $DYNAMIC_FILE;
my $KNOWN_BOTS_FILE = "$BOTS_DIR/config/known_bots.txt";
my $last_mtime      = 0;
my $CHECK_INTERVAL  = 5;
my $last_check      = 0;

my %known_bots;      # nome → 1 (whitelist)
my $pending_leader;  # nome do lider que nos convidou
my $party_retry     = 0;
my $MAX_RETRY       = 3;

Plugins::register('PartyManager', 'Gerencia parties entre bots', \&on_unload);

my $hooks = Plugins::addHooks(
    ['start3',                     \&on_start],
    ['AI_pre',                     \&on_ai_pre],
    ['packet_party_invite',        \&on_party_invite],
    ['packet_party_invite_result', \&on_invite_result],
    ['packet_party_leave',         \&on_party_leave_packet],
);

sub on_unload { Plugins::delHooks($hooks) }

# ---------------------------------------------------------------------------
sub on_start {
    return unless $char;
    my $bot_name = $char->{name} // 'unknown';
    $DYNAMIC_FILE = "$BOTS_DIR/$bot_name/macros/dynamic.txt";
    _load_known_bots();
    message "[PartyManager] Iniciado para $bot_name. Bots conhecidos: "
          . scalar(keys %known_bots) . "\n", 'info';
}

sub _load_known_bots {
    %known_bots = ();
    return unless -f $KNOWN_BOTS_FILE;
    open(my $fh, '<:encoding(UTF-8)', $KNOWN_BOTS_FILE) or return;
    while (<$fh>) {
        chomp;
        s/^\s+|\s+$//g;
        next if !$_ || /^#/;
        $known_bots{$_} = 1;
    }
    close $fh;
}

# ---------------------------------------------------------------------------
sub on_ai_pre {
    unless ($DYNAMIC_FILE) {
        on_start();
        return;
    }

    my $now = time();
    return if ($now - $last_check) < $CHECK_INTERVAL;
    $last_check = $now;

    # Recarregar known_bots periodicamente
    _load_known_bots() if $now % 60 < 5;

    return unless -f $DYNAMIC_FILE;

    my $mtime = (stat $DYNAMIC_FILE)[9];
    return if $mtime == $last_mtime;
    $last_mtime = $mtime;

    _process_commands();
}

# ---------------------------------------------------------------------------
sub _process_commands {
    open(my $fh, '<:encoding(UTF-8)', $DYNAMIC_FILE) or return;
    my @lines = <$fh>;
    close $fh;

    my @remaining;
    my $processed = 0;

    for my $line (@lines) {
        chomp $line;
        $line =~ s/^\s+|\s+$//g;

        if ($line =~ /^party_create\s+(.+)/) {
            my @members = split /\s+/, $1;
            _cmd_party_create(\@members);
            $processed = 1;

        } elsif ($line =~ /^party_accept\s+(\S+)/) {
            my $leader = $1;
            _cmd_party_accept($leader);
            $processed = 1;

        } elsif ($line =~ /^party_leave/) {
            _cmd_party_leave();
            $processed = 1;

        } else {
            # Linha não é comando de party — preservar para TradeHandler
            push @remaining, $line;
        }
    }

    if ($processed) {
        # Reescrever arquivo apenas com as linhas não processadas
        open(my $out, '>:encoding(UTF-8)', $DYNAMIC_FILE) or return;
        print $out "# aguardando comandos\n";
        for my $r (@remaining) {
            print $out "$r\n" if $r && $r !~ /^#/;
        }
        close $out;
        $last_mtime = (stat $DYNAMIC_FILE)[9] // 0;
    }
}

# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------

sub _cmd_party_create {
    my ($members_ref) = @_;
    return unless $char && $net;

    my @members = @$members_ref;
    return unless @members;

    # Verificar se já tem party
    if (%party) {
        message "[PartyManager] Já em party — skipping create\n", 'debug';
        return;
    }

    my $party_name = "HC_" . ($char->{name} // 'Bot');

    # Criar party
    if ($net->can('sendPartyCreate')) {
        $net->sendPartyCreate($party_name);
        message "[PartyManager] Party '$party_name' criada.\n", 'info';
    }

    # Convidar membros que estão no range de visão
    for my $member_name (@members) {
        _invite_player($member_name);
    }
}

sub _invite_player {
    my ($member_name) = @_;
    return unless $char && $net;

    # Buscar player pelo nome em %players
    for my $id (keys %players) {
        my $p = $players{$id};
        next unless $p && ($p->{name} // '') eq $member_name;

        if ($net->can('sendPartyJoinRequest')) {
            $net->sendPartyJoinRequest($p->{ID});
            message "[PartyManager] Convite enviado para $member_name\n", 'info';
            return;
        }
    }
    debug "[PartyManager] Player '$member_name' não encontrado no range\n", 'party';
}

sub _cmd_party_accept {
    my ($leader_name) = @_;
    return unless $char && $net;

    # Guardar o nome do lider — aceitar quando chegar o convite
    $pending_leader = $leader_name;
    message "[PartyManager] Aguardando convite de '$leader_name'...\n", 'info';

    # Se o convite já veio antes do comando (corrida), aceitar imediatamente
    if (exists $known_bots{$leader_name}) {
        _accept_pending_invite($leader_name);
    }
}

sub _cmd_party_leave {
    return unless $char && $net;
    return unless %party;

    if ($net->can('sendPartyLeave')) {
        $net->sendPartyLeave();
        message "[PartyManager] Saiu da party.\n", 'info';
    }
}

# ---------------------------------------------------------------------------
# Hooks de pacotes
# ---------------------------------------------------------------------------

sub on_party_invite {
    my (undef, $args) = @_;
    my $inviter = $args->{name} // '';

    return unless $inviter;

    # Auto-aceitar apenas de bots conhecidos
    if (exists $known_bots{$inviter}) {
        message "[PartyManager] Convite de $inviter (bot conhecido) — aceitando.\n", 'info';
        _accept_invite($args->{ID} // '');

    } elsif ($pending_leader && $inviter eq $pending_leader) {
        message "[PartyManager] Convite de $inviter (esperado pelo orquestrador) — aceitando.\n", 'info';
        _accept_invite($args->{ID} // '');
        $pending_leader = undef;

    } else {
        message "[PartyManager] Convite de $inviter (desconhecido) — ignorado.\n", 'info';
        # Rejeitar convite de desconhecidos
        $net->sendPartyInviteReply($args->{ID}, 0) if $net->can('sendPartyInviteReply');
    }
}

sub on_invite_result {
    my (undef, $args) = @_;
    my $result = $args->{result} // -1;
    my $name   = $args->{name}   // '';

    if ($result == 0) {
        message "[PartyManager] $name aceitou o convite.\n", 'info';
    } elsif ($result == 1) {
        message "[PartyManager] $name recusou o convite.\n", 'info';
    } elsif ($result == 2) {
        # Party cheia (máx 12 no server — nosso orquestrador limita a 6)
        error "[PartyManager] Party cheia ao convidar $name\n";
    }
}

sub on_party_leave_packet {
    my (undef, $args) = @_;
    my $name = $args->{name} // '';
    message "[PartyManager] $name saiu da party.\n", 'info';
}

# ---------------------------------------------------------------------------
sub _accept_invite {
    my ($inviter_id) = @_;
    return unless $net && $net->can('sendPartyInviteReply');
    $net->sendPartyInviteReply($inviter_id, 1);
}

sub _accept_pending_invite {
    my ($leader_name) = @_;
    for my $id (keys %players) {
        my $p = $players{$id};
        next unless $p && ($p->{name} // '') eq $leader_name;
        _accept_invite($p->{ID});
        $pending_leader = undef;
        return;
    }
}

1;

#!/usr/bin/env perl
use strict;
use warnings;


sub main {
    # get function params =)  <3 perl
    my ($env_prefix, $uwsgi_ini, $output_temp_file) = @_;
    die 'APP_ENV_PREFIX environmental variable must be defined.  Ex, APP_ENV_PREFIX=GM_' unless $env_prefix;
    $uwsgi_ini = 'uwsgi.ini' unless $uwsgi_ini;
    $output_temp_file = '/tmp/app-env.bash' unless $output_temp_file;

    open (my $fh, '<:encoding(UTF-8)', $uwsgi_ini)
        or die "Couldn't open '$uwsgi_ini'.. does it exist?  Set path with UWSGI_INI=some-uwsgi.ini";

    my %environmental_vars = ();

    while(<$fh>) {

        chomp; # remove trailing \n or \r\n on windows
        if (/^env\=(($env_prefix.+?)\=(.+))$/) {
            $environmental_vars{$2} = $3;
        }
    }

    open (my $out_fh, '>:encoding(UTF-8)', $output_temp_file)
        or die "Couldn't write output to file $output_temp_file'";
    print $out_fh "export $_=$environmental_vars{$_}\n" foreach (keys %environmental_vars);

    0;
}

sub print_help {
    print STDOUT
        "\n" . "=" x 80 .
        "\n{{project_name}} APP SHELL CONFIG\n\n" .
        "Reads the environmental variable settings from a UWSGI config file and writes \n" .
        "to a temp file, which can be sourced immediately after export all variables into \n" .
        "the parent shell.\n\n" .
        "environmental variables: \n" .
        " * APP_ENV_PREFIX (required!) - set the app's environmental var prefix (ex, COR_)\n" .
        " * UWSGI_INI (default=uwsgi.ini) - relative path to the uwsgi.ini config file\n" .
        " * OUTPUT_TEMP_FILE (default=/tmp/app-env.bash) - where a sourcable-bash script will be written\n\n" .
        "Example Usage:\n" .
        " \$ APP_ENV_PREFIX=COR_ OUTPUT_TEMP_FILE=/tmp/cor-vars.bash ./set-env-from-uwsgi.pl\n" .
        " \$ source /tmp/core-vars.bash\n\n" .
        "=" x 80 . "\n";
    exit 0;
}

# turn program args into searchable hash
my %args = map { $_ => 1 } @ARGV;

&print_help if exists($args{'--help'});

# pretend this is a try-catch.. because perl doesn't have those.
eval {
    &main(
        $ENV{'APP_ENV_PREFIX'},
        $ENV{'UWSGI_INI'},
        $ENV{'OUTPUT_TEMP_FILE'}
    );
};
if ($@) {
    print STDERR "\n\nERROR!!\n";
    print STDERR $@;
    &print_help;
}

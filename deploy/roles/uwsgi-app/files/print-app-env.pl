#!/usr/bin/env perl

# * This file is a helper for our application users.
# * It is to print out the current appilcation environmental variables
#       when the users `sudo su <someapssh puser> -`
# * It makes the naive assumption that ALL password variables will be suffixed _PASS

use constant NORMAL => "\033[0m";
use constant RED => "\033[0;31m";
use constant GREEN => "\033[0;32m";
use constant LIGHT_GREEN => "\033[1;32m";
use constant CYAN => "\033[0;36m";

sub main {

    my $app_prefix = $ARGV[0];

    print &tableHeader;

    printf "| %-76s |\n", "Application Settings";

    print &tableStart;

    foreach $key (sort(keys %ENV)) {
        my $actual_prefix = substr $key, 0, length($app_prefix);
        next if $actual_prefix ne $app_prefix;
        my $setting_value = $ENV{$key};
        if ($key =~ m/^.+?_PASS$/gi) {
             $setting_value = sprintf "%-53s", '**HIDDEN**';
             $setting_value = RED.$setting_value.NORMAL;
        }
        else {

            # AWS hostnames are really really long.. 
            # trim them so they don't break our table =)
            my $max_value_length = 53;
            $setting_value = (substr $setting_value, 0, $max_value_length - 3)."..."
                if length($setting_value) > $max_value_length;

            $setting_value = sprintf "%-53s", $setting_value;
            $setting_value = GREEN.$setting_value.NORMAL;
        }
        $key = sprintf "%-20s", $key;
        $key = CYAN.$key.NORMAL;

        printf "| %s | %s |\n", $key, $setting_value;
    }

    print &tableStart;
}

sub tableStart {
    return "+" . '=' x 22 . "+" . "=" x 55 . "+\n";
}
sub tableHeader {
   return "+" . '=' x 78 . "+\n";
}

__PACKAGE__->main unless caller;

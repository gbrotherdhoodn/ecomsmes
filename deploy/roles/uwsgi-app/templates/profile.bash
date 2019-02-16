# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

# the default umask is set in /etc/profile; for setting the umask
# for ssh logins, install and configure the libpam-umask package.
#umask 022

#Aliasing Load
alias load-banks="python {{ workdir }}/manage.py loaddata banks"
alias load-country="python {{ workdir }}/manage.py loaddata address_country"
alias load-all-addres="python {{ workdir }}/manage.py load_address --json-file=/srv/{{ app_user }}/www/fixtures/all_address.json && python {{ workdir }}/manage.py load_address --json-file=/srv/{{ app_user }}/www/fixtures/maluku_papua_address.json"
alias migrate="python {{ workdir }}/manage.py migrate"
alias collectstatic="python {{ workdir }}/manage.py collectstatic --noinput"
alias rebuid-index="python {{ workdir }}/manage.py rebuild_index --noinput"
alias compress="python {{ workdir }}/manage.py compress --force"
alias createsuperuser="python {{ workdir }}/manage.py createsuperuser"

# if running bash
if [ -n "$BASH_VERSION" ]; then
    # include .bashrc if it exists
    if [ -f "$HOME/.bashrc" ]; then
        . "$HOME/.bashrc"
    fi
fi

# set PATH so it includes user's private bin directories
PATH="$HOME/bin:$HOME/.local/bin:$PATH"

# Add our application to the python path
export PYTHONPATH=/srv/{{ app_user }}/www

# Automatically active the python virtualenv
source $HOME/venv/bin/activate

echo ""
echo "{{ app_user }} API Application User"
echo ""

# read and set the same environmental variables that the UWSGI vassel is running with.
# NOTE:
#   This assumes only 1 app on this box.. if you've got more you'll need to
#   set OUTPUT_TEMP_FILE to something unique to this app!
export APP_ENV_PREFIX={{APP_ENV_PREFIX}}

APP_ENV_PREFIX=$APP_ENV_PREFIX set-app-env

source /tmp/app-env.bash

print-app-env $APP_ENV_PREFIX

# Try to make sure that future ops does the right thing when deploying.
NORMAL="\033[0m";
RED="\033[0;31m";
echo ""
echo "To restart app:  "
echo "$ touch ~/uwsgi.ini"
echo ""
printf "${RED}**DO NOT RESTART EMPEROR SERVICE**${NORMAL}\n"
echo ""

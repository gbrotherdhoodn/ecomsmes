#!/bin/bash

# Run celery
source /srv/{{ app_user }}/venv/bin/activate && source /tmp/app-env.bash && cd {{ celery_workdir }} && /srv/{{ app_user }}/venv/bin/python3 /srv/{{ app_user }}/venv/bin/celery --app={{ celery_appname }} worker --beat --loglevel={{ celery_loglevel }} --logfile=/srv/{{ app_user }}/www/logs/{{ celery_logfile }}

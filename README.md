JIMS HONEY
===========

A [django-oscar](http://oscarcommerce.com/) app for handling JIMS HONEY devices (specifically 
in a marketplace deployment). 

This app must be installed with oscar in order to be used.

Make sure docker already installed in your machine

```bash
$ pip install -r requirements.txt
$ docker-compose up -d
$ ./manage.py migrate\
$ ./manage.py createsuperuser
$ ./manage.py rebuild_index --noinput
$ ./manage.py loaddata [json file name]
$ ./manage.py runserver
```

Vagrant Use
-------------

This Vagrantfile use Virtualbox

- Vagrant up

```bash
vagrant up
```

- Open Browser
```bash
localhost:8080
```

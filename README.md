# django-webapp-initscript

Script to setup a django project to be served by gunicorn+supervisord+nginx by creating the config files.

The python script will create the following folders in the project directory:

```
conf/
logs/
run/
```

It will then create the configuration scripts from the templates and place them into the _conf/_ directory.

It will create a configuration file for running gunicorn that is run from a virtual environment and calls the django project (wsgi).

It will create a configuration file for supervisord to run the gunicorn app and monitor it.

It will create a configuration file for nginx using a virtual named host. All requests (that is not static) is passed on to the gunicorn unix socket.

All that is left to do, is to fine tune the config files, and create links:

```
conf/<appname>-supervisord.conf -> /etc/supervisor/conf.d/
conf/<appname>-nginx.conf -> /etc/nginx/conf.d/
```

Usually, nginx config file is fined tuned to point the media and static files to the correct paths.

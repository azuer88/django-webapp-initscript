#!/usr/bin/env python

import sys
import os
import argparse
from string import Template 


def check_dir(dirname):
    if os.path.exists(dirname):
       if os.path.isdir(dirname):
          return 1
       else:
          return 2
    else:
       return 0


def make_dir(dirname):
    retval = check_dir(dirname)
    if retval == 0:
       print("Creating directory '%s'" % dirname)
       os.makedirs(dirname)
    elif retval == 1:
       print("Directory '%s' exists, doing nothing" % dirname)
    else:
       print("'%s' exists but is NOT a directory, exiting" % dirname)
       sys.exit(-1)


def init_dirs(appname):
    curdir = os.getcwd()
    appdir = os.path.join(curdir, appname)
    
    make_dir(appdir)
    make_dir(os.path.join(appdir, 'run'))
    logdir = os.path.join(appdir, 'logs')
    make_dir(logdir)
    make_dir(os.path.join(appdir, 'conf'))


def init_logs(appname):
    curdir = os.getcwd()
    logdir = os.path.join(curdir, appname, 'logs')

    # initialize supervisord app log file
    logfile = os.path.join(logdir, 'gunicorn.log')
    print("Createing log file %s" % logfile)
    open(logfile, 'a').close()

    # initialize nginx access log file
    logfile = os.path.join(logdir, 'nginx-access.log')
    print("Createing log file %s" % logfile)
    open(logfile, 'a').close()



def get_test_mapping():
    return {
        "BASEDIR": "/webapps/",
        "APPNAME": "my_new_app",
    }

def load_template(template):
    template_path = os.path.dirname(os.path.realpath(__file__))
    template_name = os.path.join(template_path, template + ".conf.template")
    if not os.path.exists(template_name):
         print("template '%s' NOT found, exiting" % template_name)
         sys.exit(-1)
    print("opening template %s" % template_name)
    f = open(template_name, "rt")
    try:
        return Template(f.read())
    finally:
        f.close()

def write_config(config_name, content, maps):
    base = maps['BASEDIR']
    app = maps['APPNAME']
    target_dir = os.path.join(base, app, 'conf')
    target_file = os.path.join(target_dir, "%s-%s.conf" % (app, config_name))
    print("writing config file - %s" % target_file)
    f = open(target_file, "wt")
    try:
        f.write(content)
    finally:
        f.close()


def make_config(config_name, maps):
    tmpl = load_template(config_name)
    content = tmpl.substitute(maps)
    write_config(config_name, content, maps)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Script to create webapps")
    
    parser.add_argument('-b', '--basedir', default=os.path.join(os.getcwd(),''),
                metavar='basedir', type=str, dest='BASEDIR',
                help='base directory of all webapps default=%s' % os.getcwd(),
                )
    parser.add_argument('APPNAME', type=str, metavar='appname',
                help='name of the application to initialize',
                )
    parser.add_argument('SERVERNAME', type=str, metavar='servername',
                help='server hostname to respond to in nginx',
                )

    return vars(parser.parse_args())


def validate_data(data):
    base = os.path.join(os.path.normpath(data['BASEDIR']), '')
    if not (os.path.exists(base) and os.path.isdir(base)):
    	print("directory '%s' does not exist" % base)
        sys.exit(-2)
    data['BASEDIR'] = base

    app = os.path.normpath(data['APPNAME']).split('/')[-1]
    print("Appname = '%s'" % app)
    data['APPNAME'] = app

    djangodir = find_manage_py(app)
    data['DJANGODIR'] = djangodir
    
 
    return data       


def print_reminders(data):
    appname = data['APPNAME']
    basedir = os.path.join(os.path.normpath(data['BASEDIR']), '')
    appdir = os.path.join(basedir, appname, '')
    settingsdir = os.path.join(appdir, appname, '')
    servername = data['SERVERNAME']
    print """\n\nREMINDERS: (as root, do the following)
(1)  Create links for config files from {BASEDIR}conf 
     (a) {APPNAME}-supervisord.conf into /etc/supervisor/conf.d/
     (b) {APPNAME}-nginx.conf into /etc/nginx/conf.d/

(2)  Add '{SERVERNAME}' to ALLOWED_HOSTS in settings.py
     edit {SETTINGSDIR}settings.py

(3)  Restart or reload superversord
     service supervisord reload 

(4)  Restart or reload nginx 
     service nginx reload

""".format(APPNAME=appname, 
        BASEDIR=basedir, 
        SETTINGSDIR=settingsdir,
        SERVERNAME=servername)


def find_manage_py(appname):
    curdir = os.getcwd()

    for root, dirs, files in os.walk(curdir):
        for name in files:
            if name == "manage.py":
               dirname = os.path.basename(os.path.normpath(root))
               if dirname == appname:
                  print "manage.py is at %s" % root
                  return root

    return None


def main():

    data = parse_arguments()
    data = validate_data(data)

    print data

    init_dirs(data['APPNAME'])
    init_logs(data['APPNAME'])

    # tmpl = load_template("supervisord")
    # data = get_test_mapping()

    # content = tmpl.substitute(data)

    # write_config("supervisord", content, data)

    make_config("supervisord", data)
    make_config("nginx", data)
    make_config("gunicorn", data)

    print_reminders(data)


if __name__ == "__main__":
   import sys
   sys.exit(main())

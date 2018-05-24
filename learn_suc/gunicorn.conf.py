"""
This is the configuration file for inner Gunicorn server.
"""

bind = "127.0.0.1:8001"  # Don't use port 8000 becaue nginx occupied it already.
workers = 3

django_project_dir = '/Users/dahengwang/Documents/workspace-pycharm/learn_suc-gui-local/learn_suc/'

errorlog = django_project_dir + 'logs/gunicorn-error.log'
accesslog = django_project_dir + 'logs/gunicorn-access.log'
loglevel = 'debug'

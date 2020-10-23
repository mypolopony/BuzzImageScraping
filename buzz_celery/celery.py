from __future__ import absolute_import
from celery import Celery

app = Celery('buzz_celery',
             broker='amqp://buzz:buzz@localhost/buzz_vhost',
             backend='rpc://',
             include=['buzz_celery.tasks'])
#coding:utf-8
from django.db import models
from django.contrib.auth.models import User
import re

# Create your models here.
class Terminal(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length = 30, default = '')
    ip = models.IPAddressField()
    port = models.IntegerField() 

class Device(models.Model):
    terminal = models.ForeignKey(Terminal)
    port_id = models.IntegerField() 
    sn = models.CharField(max_length =16, default = '')
    mac = models.CharField(max_length =14, default = '') 
    state = models.BooleanField(default = False)
            

class Pool(models.Model):
    user = models.ForeignKey(User)
    platform = models.CharField(max_length = 30, default = '')
    hw = models.CharField(max_length = 4, default = '')
    image = models.CharField(max_length = 40, default = '')
    bootloader = models.CharField(max_length = 40, default = '')
    sysloader = models.CharField(max_length = 40, default = '')
    state = models.BooleanField(default = False) 
    cpld = models.CharField(max_length = 10, default='')
    job = models.CharField(max_length = 40, default='')
    
class License(models.Model):
    user = models.ForeignKey(User)
    choices = [('plat', 'platform-base license'),
                       ('plat-trial', 'platform-trial license'),
                       ('av', 'anti-virus feature license'),
                       ('ips', 'ips feature license'),
                       ('urld', 'url db feature license'),
                       ('appd', 'app db feature license'),
                       ('qos', 'qos feature license'),
                       ('qos-trial', 'qos-trial license'),
                       ('thre', 'threat feature license'),
                       ('thre-trial', 'threat-trial license'),
                       ('inte', 'intelligence feature license'),
                       ('inte-trial', 'intelligence-trial license'),
                       ('feat', 'feature-trial license'),
                       ('sess', 'session license'),
                       ('perf', 'performance enhancement license'),
                       ('nbc', 'nbc feature license'),
                       ('scvp', 'secure connect license'),
                       ('vsys', 'virtual system license')
                       ]
    name = models.CharField(max_length = 35, choices = choices)
    deadline = models.CharField(max_length = 35, default = '')
    username = models.CharField(max_length = 35, default = '')
    
class Task(models.Model):
    username = models.CharField(max_length = 40, default = '')
    name = models.CharField(max_length = 40, default = '')
    platform = models.CharField(max_length = 30, default = '')
    hw = models.CharField(max_length = 4, default = '')
    image = models.CharField(max_length = 40, default = '')
    bootloader = models.CharField(max_length = 40, default = '')
    sysloader = models.CharField(max_length = 40, default = '') 
    cpld = models.CharField(max_length = 10, default = '') 
    state = models.IntegerField(default=0)
    result = models.IntegerField(default=0)
    begin = models.CharField(max_length = 30, default = '')
    over = models.CharField(max_length = 30, default = '')
    history = models.BooleanField(default = False)

class Subtask(models.Model):
    task = models.ForeignKey(Task)
    terminal = models.CharField(max_length = 30, default = '')
    ip = models.IPAddressField(default='0.0.0.0')
    port_id = models.IntegerField(default=0) 
    sn = models.CharField(max_length =16, default = '')
    mac = models.CharField(max_length =12, default = '') 
    state = models.IntegerField(default=0)
    result = result = models.IntegerField(default=0)
    log = models.TextField()
    console_log = models.TextField()
    prompt = models.CharField(max_length=50, default = '')

    
class Script(models.Model):
    username = models.CharField(max_length = 30, default = '')
    files = models.FileField(upload_to= 'product_test/script/')
    def __unicode__(self):
        return re.search('script/(\S+).py', self.files.name) .group(1)

class Platform(models.Model):
    script = models.ForeignKey(Script)
    serial = models.CharField(max_length = 2, default='')
    name = models.CharField(max_length = 30, default = '')
    memory = models.CharField(max_length = 30, default = '')
    def __unicode__(self):
        return self.name 
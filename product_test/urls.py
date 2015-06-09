#coding:utf-8
from django.conf.urls import patterns, url
from product_test import views

urlpatterns = patterns('',
    url(r'^$', views.config, name='config'),
    url(r'^pool/(?P<arg>\S+)/$', views.pool, name='pool'),
    url(r'^license/(?P<arg>\S+)/$', views.license, name='license'),
    url(r'^terminal/add/$', views.add_terminal, name='add_terminal'),
    url(r'^terminal/(?P<index>\d+)/(?P<arg>\w+)/$', views.operation_terminal, name='operation_terminal'),
    url(r'^task/$', views.task, name='task'),
    url(r'^task/recent/$', views.recent_task, name='recent_task'),
    url(r'^task/perform/$', views.perform_task, name='perform_task'),
    url(r'^task/(?P<index>\d+)/(?P<arg>\w+)/$', views.operation_task, name='operation_task'),
    url(r'^task/(?P<index>\d+)/$', views.subtask, name='subtask'),
    url(r'^task/(?P<index1>\d+)/(?P<index2>\d+)/(?P<arg>\w+)/$', views.operation_subtask, name='operation_subtask'),
    url(r'^manage/$', views.manage, name='manage'),
    url(r'^manage/platform/(?P<arg>\S+)/$', views.platform, name='platform'),
    url(r'^manage/script/(?P<arg>\S+)/$', views.script, name='script'),
)

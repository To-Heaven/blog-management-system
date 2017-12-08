"""bms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include

from blog import views
from bms import settings

urlpatterns = [
    url(r'^(?P<username>.*)/(?P<para>category|tag|date)/(?P<para_content>(.*))$', views.homesite, name='archive'),

    url(r'^(?P<username>.*)/articles/(?P<article_id>(\d+))/$', views.homesite, name='article'),

    url(r'^(?P<username>.*)/(?P<option>up|down)/(?P<article_id>(\d+))/$', views.updown, name='updown'),

    url(r'^(?P<username>.*)/comment/(?P<article_id>(\d+))/$', views.pull_comment, name='pull_comment'),

    url(r'^(?P<username>.*)/$', views.homesite, name='blog_url'),
]

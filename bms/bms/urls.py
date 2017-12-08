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
from django.contrib import admin
from django.views.static import serve

from blog import views
from bms import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^(?P<article_id>(\d+))/load_comments/$', views.load_comments, name='load_comments'),
    url(r'^register/$', views.register),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^home/$', views.home),
    url(r'^home/(?P<para>hot|time)/$', views.home, name='order'),
    url(r'^category/(?P<type_category>(\d+))/$', views.homesite, name='category'),

    url(r'^pc-geetest/register', views.pcgetcaptcha, name='pcgetcaptcha'),
    url(r'^pc-geetest/validate$', views.pcvalidate, name='pcvalidate'),
    url(r'^pc-geetest/ajax_validate', views.pcajax_validate, name='pcajax_validate'),

    # media配置
    url(r'^media/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}),

    url(r'^blog/', include("blog.urls")),
    url(r'^manage/', include("manager.urls")),


]

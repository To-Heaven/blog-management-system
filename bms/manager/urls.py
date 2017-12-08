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

from manager import views
from bms import settings

urlpatterns = [
    url(r'^home/$', views.manage_main),
    url(r'^delArticle/(?P<article_id>\d+)/$', views.delArticle, name='delArticle'),
    url(r'^addArticle/$', views.addArticle, name='addArticle'),
    url(r'^editArticle/(?P<article_id>\d+)/$', views.editArticle, name='editAritcle'),
    url(r'^uploadFile/$', views.uploadFile, name='uploadFile'),
    url(r'^listCategory/$', views.listCategory, name='listCategory'),
    url(r'^addCategory/$', views.addCategory, name='addCategory'),
    url(r'^editCategory/(?P<category_id>\d+)/$', views.editCategory, name='editCategory'),
    url(r'^delCategory/(?P<category_id>\d+)/$', views.delCategory, name='delCategory'),
]

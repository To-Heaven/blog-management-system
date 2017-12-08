from django.forms import Form
from django.forms import widgets
from django.forms import fields
from bs4 import BeautifulSoup

from blog import models


class BaseArticleForm(Form):
    title = fields.CharField(max_length=32, required=True,
                             error_messages={'required': '标题不能为空'},
                             widget=widgets.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': '文章标题',
                                                             'aria-describedby': 'title'}))

    summary = fields.CharField(max_length=512, required=True,
                               error_messages={'required': '摘要不能为空'},
                               widget=widgets.Textarea(attrs={'class': 'form-control',
                                                              'placeholder': '文章概要',
                                                              'rows': 3, 'cols': 10,
                                                              'aria-describedby': 'summary'}))

    content = fields.CharField(max_length=40960, required=True,
                               error_messages={'required': '文章内容不能为空'},
                               widget=widgets.Textarea(attrs={'class': 'form-control',
                                                              'placeholder': '文章内容',
                                                              'aria-describedby': 'content'}))


class CategoryForm(Form):
    title = fields.CharField(required=True, max_length=32,
                             error_messages={'required': '名称不能为空'},
                             widget=widgets.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': '分类名，不能为空且长度少于32字符',
                                                             'aria-describedby': 'title'}))
    description = fields.CharField(required=True, max_length=128,
                                   error_messages={'required': '描述不能为空'},
                                   widget=widgets.Textarea(attrs={'rows': 3, 'cols': 10,
                                                                  'class': 'form-control',
                                                                  'placeholder': '描述，不能为空且长度少于128字符',
                                                                  'aria-describedby': 'description'}))




# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-22 02:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20171121_2346'),
    ]

    operations = [
        migrations.AddField(
            model_name='type',
            name='total_count',
            field=models.IntegerField(default=0, verbose_name='今日该类型文章数量'),
        ),
        migrations.AddField(
            model_name='typecategory',
            name='today_article_count',
            field=models.IntegerField(default=0, verbose_name='今日该类文章数量'),
        ),
    ]

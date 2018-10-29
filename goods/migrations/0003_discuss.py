# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0002_auto_20181022_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discuss',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='评论编号', primary_key=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('content', models.CharField(max_length=60, verbose_name='评论内容')),
                ('user', models.CharField(max_length=20, verbose_name='用户')),
                ('pid', models.ForeignKey(to='goods.Discuss', verbose_name='评论的谁', null=True)),
                ('sku', models.ForeignKey(verbose_name='评论的商品', to='goods.GoodsSKU')),
            ],
            options={
                'verbose_name': '评论',
                'db_table': 'df_discuss',
                'verbose_name_plural': '评论',
            },
        ),
    ]

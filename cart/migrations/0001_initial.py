# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('uid', models.IntegerField(verbose_name='用户id')),
                ('gid', models.IntegerField(verbose_name='物品id')),
                ('num', models.IntegerField(verbose_name='购物车数量')),
            ],
            options={
                'db_table': 'df_cart',
                'verbose_name_plural': '购物车',
                'verbose_name': '购物车',
            },
        ),
    ]

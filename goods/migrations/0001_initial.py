# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('name', models.CharField(verbose_name='商品SUP名称', max_length=20)),
                ('detail', tinymce.models.HTMLField(verbose_name='商品详情', blank=True)),
            ],
            options={
                'verbose_name': '商品SUP',
                'verbose_name_plural': '商品SUP',
                'db_table': 'df_goods',
            },
        ),
        migrations.CreateModel(
            name='GoodsImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('image', models.ImageField(verbose_name='图片存储路径', upload_to='goods')),
            ],
            options={
                'verbose_name': '商品图片',
                'verbose_name_plural': '商品图片',
                'db_table': 'df_goods_image',
            },
        ),
        migrations.CreateModel(
            name='GoodsSKU',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('name', models.CharField(verbose_name='商品名称', max_length=20)),
                ('desc', models.CharField(verbose_name='商品简介', max_length=256)),
                ('price', models.DecimalField(verbose_name='商品名称', max_digits=10, decimal_places=2)),
                ('unite', models.CharField(verbose_name='商品单位', max_length=20)),
                ('image', models.ImageField(verbose_name='商品图片', upload_to='goods')),
                ('stock', models.IntegerField(verbose_name='商品库存', default=1)),
                ('sales', models.IntegerField(verbose_name='商品销量', default=0)),
                ('status', models.SmallIntegerField(default=1, choices=[(0, '下线'), (1, '上线')])),
                ('goods', models.ForeignKey(verbose_name='商品SPU', to='goods.Goods')),
            ],
            options={
                'verbose_name': '商品',
                'verbose_name_plural': '商品',
                'db_table': 'df_good_sku',
            },
        ),
        migrations.CreateModel(
            name='GoodsType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('name', models.CharField(verbose_name='种类名称', max_length=20)),
                ('logo', models.CharField(verbose_name='标识', max_length=20)),
                ('image', models.ImageField(verbose_name='商品类型图片', upload_to='type')),
            ],
            options={
                'verbose_name': '商品种类',
                'verbose_name_plural': '商品种类',
                'db_table': 'df_goods_type',
            },
        ),
        migrations.AddField(
            model_name='goodssku',
            name='type',
            field=models.ForeignKey(verbose_name='商品种类', to='goods.GoodsType'),
        ),
        migrations.AddField(
            model_name='goodsimage',
            name='sku',
            field=models.ForeignKey(verbose_name='商品', to='goods.GoodsSKU'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndexGoodBanner',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('image', models.ImageField(verbose_name='图片', upload_to='banner')),
                ('index', models.SmallIntegerField(verbose_name='展示顺序', default=0)),
            ],
            options={
                'db_table': 'df_index_banner',
                'verbose_name': '首页轮播商品',
                'verbose_name_plural': '首页轮播商品',
            },
        ),
        migrations.CreateModel(
            name='IndexPromotionBanner',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('name', models.CharField(max_length=20, verbose_name='活动名称')),
                ('url', models.CharField(max_length=256, verbose_name='活动链接')),
                ('image', models.ImageField(verbose_name='活动图片', upload_to='banner')),
                ('index', models.SmallIntegerField(verbose_name='展示顺序', default=0)),
            ],
            options={
                'db_table': 'df_index_promotion',
                'verbose_name': '主页促销活动',
                'verbose_name_plural': '主页促销活动',
            },
        ),
        migrations.CreateModel(
            name='IndexTypeGoodsBanner',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('display_type', models.SmallIntegerField(choices=[(0, '标题'), (1, '图片')], verbose_name='展示方式', default=1)),
                ('index', models.SmallIntegerField(verbose_name='展示顺序', default=0)),
            ],
            options={
                'db_table': 'df_index_type_goods',
                'verbose_name': '主页分类展示商品',
                'verbose_name_plural': '主页分类展示商品',
            },
        ),
        migrations.AlterModelOptions(
            name='goods',
            options={'verbose_name': '商品SPU', 'verbose_name_plural': '商品SPU'},
        ),
        migrations.AlterField(
            model_name='goods',
            name='name',
            field=models.CharField(max_length=20, verbose_name='商品SPU名称'),
        ),
        migrations.AlterField(
            model_name='goodssku',
            name='price',
            field=models.DecimalField(decimal_places=2, verbose_name='商品价格', max_digits=10),
        ),
        migrations.AddField(
            model_name='indextypegoodsbanner',
            name='sku',
            field=models.ForeignKey(verbose_name='商品sku', to='goods.GoodsSKU'),
        ),
        migrations.AddField(
            model_name='indextypegoodsbanner',
            name='type',
            field=models.ForeignKey(verbose_name='商品类型', to='goods.GoodsType'),
        ),
        migrations.AddField(
            model_name='indexgoodbanner',
            name='sku',
            field=models.ForeignKey(verbose_name='商品', to='goods.GoodsSKU'),
        ),
    ]

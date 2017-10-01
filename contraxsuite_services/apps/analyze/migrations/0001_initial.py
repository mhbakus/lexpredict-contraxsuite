# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-31 09:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentCluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cluster_id', models.IntegerField(default=0)),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('self_name', models.CharField(db_index=True, max_length=100)),
                ('description', models.CharField(db_index=True, max_length=200)),
                ('cluster_by', models.CharField(db_index=True, max_length=20)),
                ('using', models.CharField(db_index=True, max_length=20)),
                ('created_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ('cluster_by', 'using', 'cluster_id'),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DocumentSimilarity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similarity', models.DecimalField(decimal_places=2, max_digits=5)),
                ('created_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ('document_a__pk', '-similarity', 'document_b__pk'),
                'verbose_name_plural': 'Document Similarities',
            },
        ),
        migrations.CreateModel(
            name='PartySimilarity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similarity', models.DecimalField(decimal_places=2, max_digits=5)),
                ('created_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ('party_a__pk', '-similarity', 'party_b__pk'),
                'verbose_name_plural': 'Party Similarities',
            },
        ),
        migrations.CreateModel(
            name='TextUnitClassification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_name', models.CharField(db_index=True, max_length=1024)),
                ('class_value', models.CharField(db_index=True, max_length=1024)),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ('text_unit', 'class_name', 'timestamp'),
            },
        ),
        migrations.CreateModel(
            name='TextUnitClassifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=1024)),
                ('version', models.CharField(db_index=True, max_length=1024)),
                ('class_name', models.CharField(db_index=True, max_length=1024)),
                ('model_object', models.BinaryField()),
                ('is_active', models.BooleanField(db_index=True, default=True)),
            ],
            options={
                'ordering': ('name', 'class_name'),
            },
        ),
        migrations.CreateModel(
            name='TextUnitClassifierSuggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classifier_run', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('classifier_confidence', models.FloatField(default=0.0)),
                ('class_name', models.CharField(db_index=True, max_length=1024)),
                ('class_value', models.CharField(db_index=True, max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='TextUnitCluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cluster_id', models.IntegerField(default=0)),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('self_name', models.CharField(db_index=True, max_length=100)),
                ('description', models.CharField(db_index=True, max_length=200)),
                ('cluster_by', models.CharField(db_index=True, max_length=20)),
                ('using', models.CharField(db_index=True, max_length=20)),
                ('created_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ('cluster_by', 'using', 'cluster_id'),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TextUnitSimilarity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similarity', models.DecimalField(decimal_places=2, max_digits=5)),
                ('created_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ('text_unit_a__pk', '-similarity', 'text_unit_b__pk'),
                'verbose_name_plural': 'Text Unit Similarities',
            },
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-10-18 14:47
from __future__ import unicode_literals

import commercialoperator.components.compliances.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commercialoperator', '0002_auto_20181018_2212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compliancedocument',
            name='_file',
            field=models.FileField(upload_to=commercialoperator.components.compliances.models.update_proposal_complaince_filename),
        ),
    ]

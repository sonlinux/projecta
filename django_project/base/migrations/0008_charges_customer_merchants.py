# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_project_project_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Charges',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('charge_stripe_id', models.CharField(max_length=50)),
                ('merchant_stripe_id', models.CharField(max_length=50)),
                ('customer_stripe_id', models.CharField(max_length=50)),
                ('charge_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, blank=True, help_text='Amount charged on account in dollars', null=True)),
                ('project_id', models.CharField(max_length=50)),
                ('user_id', models.CharField(max_length=50)),
                ('date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('merchant_id', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Merchants',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('firstname', models.CharField(max_length=50)),
                ('merchantid', models.CharField(max_length=50)),
            ],
        ),
    ]

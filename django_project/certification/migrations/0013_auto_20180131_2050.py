    # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certification', '0012_auto_20170922_0649'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attendee',
            options={'ordering': ['firstname']},
        ),
        migrations.RenameField(
            model_name='attendee',
            old_name='first_name',
            new_name='firstname',
        ),
        migrations.AlterUniqueTogether(
            name='attendee',
            unique_together=set([('firstname', 'surname', 'email', 'certifying_organisation')]),
        ),
    ]

# Generated by Django 2.2.8 on 2020-01-18 05:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finalizeddata',
            name='group',
            field=models.ForeignKey(default=117, on_delete=django.db.models.deletion.DO_NOTHING, to='authentication.CustomGroup'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='taskdata',
            name='group',
            field=models.ForeignKey(default=117, on_delete=django.db.models.deletion.DO_NOTHING, to='authentication.CustomGroup'),
            preserve_default=False,
        ),
    ]
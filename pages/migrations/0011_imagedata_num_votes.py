# Generated by Django 2.2.8 on 2020-04-08 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0010_votingdata_num_votes'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagedata',
            name='num_votes',
            field=models.IntegerField(default=0),
        ),
    ]

# Generated by Django 2.2.8 on 2019-12-25 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_auto_20191225_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customgroup',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
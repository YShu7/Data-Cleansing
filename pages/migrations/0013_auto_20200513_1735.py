# Generated by Django 2.2.8 on 2020-05-13 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0012_auto_20200419_0940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagedata',
            name='image_url',
            field=models.URLField(),
        ),
    ]
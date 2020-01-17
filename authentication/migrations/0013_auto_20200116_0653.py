# Generated by Django 2.2.8 on 2020-01-16 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_customuser_is_approved'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customgroup',
            name='main_group',
        ),
        migrations.AlterField(
            model_name='customgroup',
            name='name',
            field=models.CharField(max_length=32, unique=True),
        ),
        migrations.DeleteModel(
            name='Specialization',
        ),
    ]

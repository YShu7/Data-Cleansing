# Generated by Django 2.2.8 on 2020-01-21 04:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalizedData',
            fields=[
                ('data_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='pages.Data')),
                ('answer_text', models.TextField()),
            ],
            bases=('pages.data',),
        ),
    ]

# Generated by Django 2.2.5 on 2019-10-12 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VotingData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=200)),
                ('answer_text_1', models.TextField()),
                ('answer_text_2', models.TextField()),
                ('answer_text_3', models.TextField()),
                ('type_text', models.CharField(max_length=100)),
            ],
        ),
    ]
# Generated by Django 2.2.5 on 2019-12-16 11:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_votingdata'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='votingdata',
            name='answer_text_1',
        ),
        migrations.RemoveField(
            model_name='votingdata',
            name='answer_text_2',
        ),
        migrations.RemoveField(
            model_name='votingdata',
            name='answer_text_3',
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('num_votes', models.IntegerField()),
                ('data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.VotingData')),
            ],
        ),
    ]
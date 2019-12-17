# Generated by Django 2.2.5 on 2019-12-17 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_auto_20191216_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='num_votes',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='ValidatingData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=200)),
                ('answer_text', models.TextField()),
                ('num_approved', models.IntegerField(default=0)),
                ('num_disapproved', models.IntegerField(default=0)),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.Type')),
            ],
        ),
    ]
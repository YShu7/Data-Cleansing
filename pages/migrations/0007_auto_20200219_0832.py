# Generated by Django 2.2.8 on 2020-02-19 08:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0006_auto_20200212_0956'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageData',
            fields=[
                ('data_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='pages.Data')),
                ('image_url', models.URLField()),
            ],
            bases=('pages.data',),
        ),
        migrations.AlterField(
            model_name='finalizeddata',
            name='ans_keywords',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='finalizeddata',
            name='qns_keywords',
            field=models.TextField(default=''),
        ),
        migrations.CreateModel(
            name='ImageLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField()),
                ('num_votes', models.IntegerField(default=0)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.ImageData')),
            ],
        ),
    ]

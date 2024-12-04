# Generated by Django 5.1.3 on 2024-12-04 03:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('departmentID', models.AutoField(primary_key=True, serialize=False)),
                ('departmentName', models.CharField(max_length=100)),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('employeeID', models.AutoField(primary_key=True, serialize=False)),
                ('firstName', models.CharField(max_length=50)),
                ('lastName', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('hireDate', models.DateField()),
                ('position', models.CharField(blank=True, max_length=50, null=True)),
                ('salary', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees', to='statera.department')),
                ('reportsTo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subordinates', to='statera.employee')),
            ],
        ),
        migrations.AddField(
            model_name='department',
            name='managerID',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_departments', to='statera.employee'),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('projectName', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('startDate', models.DateField()),
                ('endDate', models.DateField()),
                ('status', models.CharField(max_length=50)),
                ('budget', models.DecimalField(decimal_places=2, max_digits=15)),
                ('projectManager', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='statera.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taskName', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('status', models.CharField(max_length=50)),
                ('priority', models.CharField(max_length=20)),
                ('estimatedHours', models.DecimalField(decimal_places=2, max_digits=5)),
                ('startDate', models.DateField()),
                ('dueDate', models.DateField(blank=True, null=True)),
                ('ETA', models.DateField(blank=True, null=True)),
                ('assignedTo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='statera.employee')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statera.project')),
            ],
        ),
        migrations.CreateModel(
            name='TimeEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('hoursWorked', models.IntegerField()),
                ('description', models.TextField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statera.employee')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statera.task')),
            ],
        ),
    ]
# Generated by Django 5.0.10 on 2025-03-11 12:42

import base.files.storages
import core.validators
import django.contrib.postgres.fields
import django.db.models.deletion
import django.db.models.expressions
import django.utils.timezone
import user.access_rights
import user.models.user
import user.models.user_role
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=user.access_rights.get_all_permission, max_length=255, verbose_name='Name')),
                ('permissions', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=128), blank=True, default=list, help_text='List of permissions available for this role.', size=None, validators=[core.validators.validate_unique_choice_array])),
                ('rules', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=user.models.user_role.get_rule_choices, max_length=128), blank=True, default=list, help_text='List of access rules applied for this role.', size=None, validators=[core.validators.validate_unique_choice_array])),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=255, verbose_name='Username')),
                ('first_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='First name')),
                ('last_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Last name')),
                ('email', models.EmailField(max_length=255, verbose_name='Email')),
                ('avatar', models.ImageField(blank=True, max_length=256, null=True, storage=base.files.storages.PrivateMediaFileSystemStorage(), upload_to=user.models.user.upload_to_user_avatar)),
                ('language', models.CharField(choices=[('en-us', 'English'), ('fr', 'French')], default='fr', max_length=10)),
                ('user_type', models.CharField(choices=[('PORTAL', 'Portal'), ('INTERNAL', 'Internal'), ('ADMIN', 'Admin')], default='PORTAL', max_length=24)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            managers=[
                ('objects', user.models.user.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserRoleRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='role_relations', to='user.userrole')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='role_relations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='roles',
            field=models.ManyToManyField(related_name='users', through='user.UserRoleRelation', to='user.userrole'),
        ),
        migrations.AddConstraint(
            model_name='userrolerelation',
            constraint=models.UniqueConstraint(django.db.models.expressions.RawSQL('SPLIT_PART("role_id", \'_\', 1)', output_field=models.CharField(), params=[]), models.F('user'), name='unique_role_category', violation_error_message='A user can only have one role per category.'),
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.UniqueConstraint(fields=('username',), name='unique_username', violation_error_message='A user with that username already exists.'),
        ),
    ]

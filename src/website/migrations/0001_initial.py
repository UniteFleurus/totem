# Generated by Django 5.0.8 on 2024-10-31 08:46

import core.fields
import django.core.validators
import django.db.models.deletion
import uuid
import website.website_widget
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
                ('widget_type', models.CharField(choices=website.website_widget.get_widget_type_choices, max_length=64, verbose_name='Type')),
                ('position', models.CharField(choices=[('FOOTER_1', 'Footer 1'), ('FOOTER_2', 'Footer 2'), ('FOOTER_3', 'Footer 3'), ('FOOTER_4', 'Footer 4'), ('HOMEPAGE_1', 'Homepage 1'), ('HOMEPAGE_2', 'Homepage 2'), ('HOMEPAGE_3', 'Homepage 3'), ('HOMEPAGE_4', 'Homepage 4')], max_length=64, verbose_name='Position')),
                ('param_content', core.fields.HtmlField(blank=True, null=True, verbose_name='HTML Content')),
                ('param_limit_item', models.IntegerField(blank=True, help_text='Used to limit the number of item to display in the widget.', null=True, validators=[django.core.validators.MaxValueValidator(10)], verbose_name='Max Item to Display')),
            ],
            options={
                'verbose_name': 'Widget',
                'verbose_name_plural': 'Widgets',
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(help_text='URL part identifying the page.', max_length=256, verbose_name='Slug')),
                ('is_published', models.BooleanField(default=False, help_text='Is published on the website.', verbose_name='Is Published')),
                ('date_published', models.DateTimeField(blank=True, help_text='Date of the last publication of the document.', null=True, verbose_name='Publication Date')),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
                ('content', core.fields.HtmlField(help_text='HTML content', verbose_name='Content')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name='Update Date')),
                ('user', models.ForeignKey(blank=True, help_text='Author of the web page.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Author')),
            ],
            options={
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, verbose_name='Title')),
                ('parent_path', models.CharField(editable=False, help_text='Use to fetch all menu tree at once.', max_length=256, verbose_name='Parent Path')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('sequence', models.IntegerField(default=20, help_text='Ordering menu items', verbose_name='Sequence')),
                ('link', models.CharField(blank=True, max_length=256, null=True, verbose_name='Target Link')),
                ('new_window', models.BooleanField(blank=True, default=False, verbose_name='Open in a new window')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='website.menu')),
                ('page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='website.page', verbose_name='Target Page')),
            ],
            options={
                'verbose_name': 'Menu Item',
                'verbose_name_plural': 'Menu Items',
            },
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, verbose_name='Name')),
                ('headline', models.CharField(max_length=256, verbose_name='Headline')),
                ('meta_authors', models.CharField(blank=True, max_length=256, null=True, verbose_name='Meta Author')),
                ('meta_description', models.TextField(blank=True, null=True, verbose_name='Meta Description')),
                ('footer', core.fields.HtmlField(blank=True, null=True, verbose_name='Footer Content')),
                ('menu', models.ForeignKey(blank=True, help_text='Parent item as the main menu of the website.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='website.menu', verbose_name='Main Menu')),
            ],
            options={
                'verbose_name': 'Website',
                'verbose_name_plural': 'Websites',
            },
        ),
        migrations.AddConstraint(
            model_name='widget',
            constraint=models.UniqueConstraint(fields=('position',), name='widget_unique_position'),
        ),
        migrations.AddConstraint(
            model_name='page',
            constraint=models.UniqueConstraint(fields=('slug',), name='page_unique_slug'),
        ),
        migrations.AddConstraint(
            model_name='menu',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('parent__isnull', False), models.Q(('link__isnull', False), ('page__isnull', False), _connector='OR')), ('parent__isnull', True), _connector='OR'), name='menu_page_or_link', violation_error_message='Menu must be linked to an URL or a page.'),
        ),
    ]

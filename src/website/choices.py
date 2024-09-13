from django.db import models


class WidgetPosition(models.TextChoices):
    FOOTER_1 = 'FOOTER_1', 'Footer 1'
    FOOTER_2 = 'FOOTER_2', 'Footer 2'
    FOOTER_3 = 'FOOTER_3', 'Footer 3'
    FOOTER_4 = 'FOOTER_4', 'Footer 4'

    HOMEPAGE_1 = 'HOMEPAGE_1', 'Homepage 1'
    HOMEPAGE_2 = 'HOMEPAGE_2', 'Homepage 2'
    HOMEPAGE_3 = 'HOMEPAGE_3', 'Homepage 3'
    HOMEPAGE_4 = 'HOMEPAGE_4', 'Homepage 4'

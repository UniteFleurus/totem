from django.db.models.expressions import RawSQL
from django.db import models
from django.contrib.postgres.fields import ArrayField

from user import choices


class UserRole(models.Model):
    id = models.CharField(
        "ID", max_length=128, null=False, blank=False, primary_key=True)
    name = models.CharField(
        "Name", max_length=255, null=False, blank=False)
    scopes = ArrayField(
        models.CharField(max_length=128, blank=False),
        blank=True,
        default=list,
        help_text="List of scopes available for this role."
    )


class UserRoleRelation(models.Model):
    user = models.ForeignKey(
        'user.User', related_name='role_relations', null=False, on_delete=models.CASCADE)
    role = models.ForeignKey(
        'user.UserRole', related_name='role_relations', null=False, on_delete=models.CASCADE)

    class Meta:
        indexes = []
        constraints = [
            models.UniqueConstraint(
                RawSQL("SPLIT_PART('role', '_', 1)", params=[],
                       output_field=models.CharField()),
                name="unique_role_category",
                violation_error_message="A user can only have one role per category.",
            ),
        ]

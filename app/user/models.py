import uuid
from tortoise import fields, models


class Role(models.Model):
    id = fields.CharField(50, pk=True)
    name = fields.CharField(128, null=False)
    description = fields.TextField(null=True)


class User(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    username = fields.CharField(50, unique=True)
    email = fields.CharField(50, null=False)
    hashed_password = fields.CharField(128)
    is_active = fields.BooleanField(default=True)
    first_name = fields.CharField(50, null=True)
    last_name = fields.CharField(50, null=True)
    role: fields.ForeignKeyRelation[Role] = fields.ForeignKeyField(
        "models.Role", related_name="users"
    )

    def has_permission(self, perms):
        return None

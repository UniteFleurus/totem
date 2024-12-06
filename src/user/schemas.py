
from ninja import ModelSchema
from pydantic import UUID4

from user.models import User


class UserDisplayNameSchema(ModelSchema):
    id: UUID4

    class Meta:
        model = User
        fields = ['id', 'username']

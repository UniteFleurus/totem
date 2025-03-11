from tortoise import fields, models
from datetime import date


class Member(models.Model):
    id = fields.IntField(pk=True)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    birth_date = fields.DateField()
    section = fields.CharField(max_length=50)
    active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @property
    def age(self):
        today = date.today()
        return (
            today.year - self.birth_date.year -
            ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    class Meta:
        table = "members"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

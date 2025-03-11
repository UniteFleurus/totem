from typing import TypeVar, Generic, Optional, Union
from pydantic import BaseModel, UUID4
from tortoise.models import Model, QuerySet


ModelType = TypeVar("ModelType", bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
FilterschemaType = TypeVar("FilterschemaType", bound=BaseModel)


class CRUDMixin(Generic[ModelType, CreateSchemaType, UpdateSchemaType, FilterschemaType]):

    def __init__(self, model: Model):
        self.model = model

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        obj_dict = obj_in.dict(exclude_unset=True)
        return await self.model.create(**obj_dict)

    async def update(self, _id: Union[int, str, UUID4], obj_in: UpdateSchemaType, slug_field: str = 'pk') -> ModelType:
        obj_dict = obj_in.dict(exclude_unset=True)
        await self.model.filter(**{slug_field: _id}).update(**obj_dict)
        return await self.get(id)

    async def delete(self, _id: Union[int, str, UUID4], slug_field: str = 'pk') -> None:
        await self.model.filter(**{slug_field: _id}).delete()

    async def list(self, filters: Optional[FilterschemaType] = None) -> QuerySet:
        qs = self.model.all()
        if filters:
            qs = filters.filter(qs).all()
        return qs

    async def get(self, _id: Union[int, str, UUID4], slug_field: str = 'pk') -> ModelType:
        return await self.model.get(**{slug_field: _id})

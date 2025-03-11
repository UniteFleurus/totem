from pydantic import BaseModel, Field, UUID4
from typing import Any, Generic, List, Optional, TypeVar, Sequence, Union
from tortoise.queryset import QuerySet


class PaginationNumberParams(BaseModel):
    page_size: int = Field(default=20, gt=1, lte=100, title="Number of results to return per page.")
    page: int = Field(default=1, gte=1, title="A page number within the paginated result set.")

    async def paginate(self, queryset: Union[QuerySet, List[Any]]):
        return {
            "count": await self._items_count(queryset),
            "results": await self._slice_queryset(queryset),
        }

    async def _slice_queryset(self, queryset: Union[QuerySet, List[Any]]):
        offset = (self.page - 1) * self.page_size
        if isinstance(queryset, QuerySet):
            return [item async for item in queryset.limit(offset + self.page_size).offset(offset).all()]
        return queryset[offset : offset + self.page_size]

    async def _items_count(self, queryset: Union[QuerySet, List[Any]]) -> int:
        try:
            return await queryset.all().count()
        except AttributeError as exc:
            return len(queryset)


ItemType = TypeVar('ItemType', bound=BaseModel)


class PaginationNumberPage(BaseModel, Generic[ItemType]):
    count: int = Field(gte=0, title="Total number of item.")
    results: Sequence[ItemType] = Field(title="List of item.")

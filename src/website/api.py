from typing import Any, List, Tuple, Type

from ninja import Query
from ninja_extra import (
    http_get, http_post, http_patch, http_delete,
    api_controller, pagination
)
from ninja_extra.searching import searching
from ninja_extra.ordering import ordering

from core.api import BaseModelController
from totem.api import api_v1
from oauth.security import OAuthTokenBearer, TokenHasScope
from website.filters import PageFilterSchema
from website.schemas import PageListSchema, PageDetailSchema, PageCreateSchemaIn, PageUpdateSchemaIn
from website.services import PageModelService


@api_controller('/website/pages/', auth=OAuthTokenBearer())
class PagesController(BaseModelController):

    def __init__(self, page_service: PageModelService):
        self.page_service = page_service

    @http_get("", response=pagination.PaginatedResponseSchema[PageListSchema], permissions=[TokenHasScope('totem.websitepage.read')], operation_id="ListPage")
    @pagination.paginate(pagination.PageNumberPaginationExtra)
    @searching(search_fields=['title'])
    @ordering(ordering_fields=['slug', 'title', 'date_published'], default_fields=['date_published', 'id'])
    # TODO @queryfield(response_schema=....) and give the ORM field (or annotation) field list aka the validation_alias of response schema model field
    async def list_pages(self, filters: PageFilterSchema = Query(...), **kwargs):
        """ Get all website pages, or search them. """
        return await self.page_service.search_read_async(filters=filters, user=self.context.request.user)

    @http_get('/{slug}/', response=PageDetailSchema, permissions=[TokenHasScope('totem.websitepage.read')], operation_id="DetailPage")
    async def detail_page(self, slug: str):
        return await self.page_service.read_async(lookup_value=slug, lookup_name='slug')

    @http_post(response={201: PageDetailSchema}, permissions=[TokenHasScope('totem.websitepage.create')], operation_id="CreatePage")
    async def create_page(self, page: PageCreateSchemaIn):
        return 201, await self.page_service.create_async(page, user=self.context.request.user)

    @http_patch('/{slug}/', response=PageDetailSchema, permissions=[TokenHasScope('totem.websitepage.update')], operation_id="UpdatePage")
    async def update_page(self, slug: str, page: PageUpdateSchemaIn):
        return await self.page_service.update_async(page, lookup_value=slug, lookup_name='slug', user=self.context.request.user)

    @http_delete('/{slug}/', response={204: None}, permissions=[TokenHasScope('totem.websitepage.delete')], operation_id="DeletePage")
    async def delete_page(self, slug: str):
        return 204, await self.page_service.delete_async(lookup_value=slug, lookup_name='slug', user=self.context.request.user)

api_v1.register_controllers(
    PagesController
)


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
from website.filters import MenuFilterSchema, PageFilterSchema
from website.schemas import MenuCreateSchemaIn, MenuListSchema, MenuDetailSchema, MenuUpdateSchemaIn, PageListSchema, PageDetailSchema, PageCreateSchemaIn, PageUpdateSchemaIn
from website.services import MenuModelService, PageModelService


@api_controller('/website/pages/', auth=OAuthTokenBearer())
class PagesController(BaseModelController):

    def __init__(self, page_service: PageModelService):
        self.page_service = page_service

    @http_get("", response=pagination.PaginatedResponseSchema[PageListSchema], permissions=[TokenHasScope('totem.websitepage.read')], operation_id="ListPage")
    @pagination.paginate(pagination.PageNumberPaginationExtra)
    @searching(search_fields=['title'])
    @ordering(ordering_fields=['slug', 'title', 'date_published'], default_fields=['date_published', 'id'])
    async def list_pages(self, filters: PageFilterSchema = Query(...)):
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


@api_controller('/website/menus/', auth=OAuthTokenBearer())
class WebsiteMenusController(BaseModelController):

    def __init__(self, menu_service: MenuModelService):
        self.menu_service = menu_service

    @http_get(
        "",
        response=pagination.PaginatedResponseSchema[MenuListSchema],
        permissions=[TokenHasScope('totem.websitemenu.read')],
        operation_id="ListWebsiteMenu"
    )
    @pagination.paginate(pagination.PageNumberPaginationExtra)
    @searching(search_fields=['name'])
    @ordering(
        ordering_fields=['id', 'name', 'create_date', 'sequence'],
        default_fields=['sequence', 'name']
    )
    async def list_menus(self, filters: MenuFilterSchema = Query(...)):
        """ Get all website menu, or search them. """
        return await self.menu_service.search_read_async(filters=filters, user=self.context.request.user)

    @http_post(
        response={201: MenuDetailSchema},
        permissions=[TokenHasScope('totem.websitemenu.create')],
        operation_id="CreateWebsiteMenu"
    )
    async def create_menu(self, menu: MenuCreateSchemaIn):
        return 201, await self.menu_service.create_async(menu, user=self.context.request.user)

    @http_patch(
        '/{menu_id}/',
        response=MenuDetailSchema,
        permissions=[TokenHasScope('totem.websitemenu.update')],
        operation_id="UpdateWebsiteMenu"
    )
    async def update_menu(self, menu_id: str, menu: MenuUpdateSchemaIn):
        return await self.menu_service.update_async(menu, lookup_value=menu_id, lookup_name='id', user=self.context.request.user)

    @http_delete(
        '/{menu_id}/',
        response={204: None},
        permissions=[TokenHasScope('totem.websitemenu.delete')],
        operation_id="DeleteWebsiteMenu"
    )
    async def delete_menu(self, menu_id: str):
        return 204, await self.menu_service.delete_async(lookup_value=menu_id, lookup_name='id', user=self.context.request.user)


api_v1.register_controllers(
    WebsiteMenusController
)

from pydantic import UUID4

from ninja import Query
from ninja_extra import (
    http_get, http_post, http_patch, http_delete,
    api_controller, pagination
)
from ninja_extra.searching import searching
from ninja_extra.ordering import ordering
from ninja_extra.permissions import IsAuthenticated

from core.api import BaseModelController
from totem.api import api_v1
from oauth.security import OAuthTokenBearer, TokenHasScope
from user.filters import UserFilterSchema
from user.schemas import UserListSchema, UserDetailSchema, UserCreateSchemaIn, UserUpdateSchemaIn, UserProfileSchemaOut
from user.services import UserModelService


@api_controller('/users/', auth=OAuthTokenBearer())
class UsersController(BaseModelController):

    def __init__(self, user_service: UserModelService):
        self.user_service = user_service

    @http_get('/me/', response=UserProfileSchemaOut, permissions=[IsAuthenticated], operation_id="ReadMyProfile")
    async def my_profile(self):
        return await self.user_service.read_my_profile(self.context.request.user)

    @http_get("", response=pagination.PaginatedResponseSchema[UserListSchema], permissions=[TokenHasScope('totem.user.read')], operation_id="ListUser")
    @pagination.paginate(pagination.PageNumberPaginationExtra)
    @searching(search_fields=['username', 'email'])
    @ordering(ordering_fields=['username', 'email', 'is_active', 'date_joined'], default_fields=['username', 'id'])
    async def list_users(self, filters: UserFilterSchema = Query(...)):
        """ Get all users, or search them. """
        return await self.user_service.search_read_async(filters=filters, user=self.context.request.user)

    @http_get('/{identifier}/', response=UserDetailSchema, permissions=[TokenHasScope('totem.user.read')], operation_id="DetailUser")
    async def detail_user(self, identifier: UUID4):
        return await self.user_service.read_async(lookup_value=identifier)

    @http_post(response={201: UserDetailSchema}, permissions=[TokenHasScope('totem.user.create')], operation_id="CreateUser")
    async def create_user(self, user: UserCreateSchemaIn):
        return 201, await self.user_service.create_async(user, user=self.context.request.user)

    @http_patch('/{identifier}/', response=UserDetailSchema, permissions=[TokenHasScope('totem.user.update')], operation_id="UpdateUser")
    async def update_user(self, identifier: UUID4, user: UserUpdateSchemaIn):
        return await self.user_service.update_async(user, lookup_value=identifier, user=self.context.request.user)

    @http_delete('/{identifier}/', response={204: None}, permissions=[TokenHasScope('totem.user.delete')], operation_id="DeleteUser")
    async def delete_user(self, identifier: UUID4):
        return 204, await self.user_service.delete_async(lookup_value=identifier, user=self.context.request.user)

api_v1.register_controllers(
    UsersController
)


# @api_controller('/website/menus/', auth=OAuthTokenBearer())
# class WebsiteMenusController(BaseModelController):

#     def __init__(self, menu_service: MenuModelService):
#         self.menu_service = menu_service

#     @http_get(
#         "",
#         response=pagination.PaginatedResponseSchema[MenuListSchema],
#         permissions=[TokenHasScope('totem.websitemenu.read')],
#         operation_id="ListWebsiteMenu"
#     )
#     @pagination.paginate(pagination.UserNumberPaginationExtra)
#     @searching(search_fields=['name'])
#     @ordering(
#         ordering_fields=['id', 'name', 'create_date', 'sequence'],
#         default_fields=['sequence', 'name']
#     )
#     async def list_menus(self, filters: MenuFilterSchema = Query(...)):
#         """ Get all website menu, or search them. """
#         return await self.menu_service.search_read_async(filters=filters, user=self.context.request.user)

#     @http_post(
#         response={201: MenuDetailSchema},
#         permissions=[TokenHasScope('totem.websitemenu.create')],
#         operation_id="CreateWebsiteMenu"
#     )
#     async def create_menu(self, menu: MenuCreateSchemaIn):
#         return 201, await self.menu_service.create_async(menu, user=self.context.request.user)

#     @http_patch(
#         '/{menu_id}/',
#         response=MenuDetailSchema,
#         permissions=[TokenHasScope('totem.websitemenu.update')],
#         operation_id="UpdateWebsiteMenu"
#     )
#     async def update_menu(self, menu_id: str, menu: MenuUpdateSchemaIn):
#         return await self.menu_service.update_async(menu, lookup_value=menu_id, lookup_name='id', user=self.context.request.user)

#     @http_delete(
#         '/{menu_id}/',
#         response={204: None},
#         permissions=[TokenHasScope('totem.websitemenu.delete')],
#         operation_id="DeleteWebsiteMenu"
#     )
#     async def delete_menu(self, menu_id: str):
#         return 204, await self.menu_service.delete_async(lookup_value=menu_id, lookup_name='id', user=self.context.request.user)


# api_v1.register_controllers(
#     WebsiteMenusController
# )

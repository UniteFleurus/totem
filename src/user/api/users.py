# examples/views/department_views.py
from typing import List

from ninja import NinjaAPI, Router
from ninja_crud import views, viewsets

from core.api import ModelAPIViewSet
from oauth.authentication import OAuthTokenAuthentication
from user.filters import UserFilterSchema
from user.models import User
from user.schemas import UserCreateSchema, UserUpdateSchema, UserSchema

router_v1_users = Router()

from core.api.permission import BasePermission


class UserViewSet(ModelAPIViewSet):
    api = router_v1_users
    model = User

    authentication_classes = [OAuthTokenAuthentication]
    permission_classes = [BasePermission]

    filter_class = UserFilterSchema
    ordering_fields = ["username", "email", "first_name"]
    default_ordering_fields = ["username"]

    list_response_body = List[UserSchema]
    retrieve_response_body = UserSchema

    create_request_body = UserCreateSchema
    create_response_body = UserSchema

    update_request_body = UserUpdateSchema
    update_response_body = UserSchema

    # Define all CRUD operations with minimal code
    # list_departmencacts = views.ListView(response_body=List[UserDisplayNameSchema])
    # create_department = views.CreateView(request_body=DepartmentIn, response_body=DepartmentOut)
    # read_department = views.ReadView(response_body=DepartmentOut)
    # update_department = views.UpdateView(request_body=DepartmentIn, response_body=DepartmentOut)
    # delete_department = views.DeleteView()

# # You can still add custom endpoints as needed using pure Django Ninja syntax
# @api.get("/stats/")
# def get_department_stats(request):
#     return {"total": Department.objects.count()}
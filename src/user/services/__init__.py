from injector import Module, Binder, singleton, inject, provider

from .user import UserModelService


class UserModule(Module):
    def configure(self, binder: Binder) -> Binder:
        binder.bind(UserModelService, to=UserModelService, scope=singleton)

    @provider
    @inject
    def provide_user_service(self) -> UserModelService:
        return UserModelService()

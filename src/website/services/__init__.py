from injector import Module, Binder, singleton, inject, provider

from .page import PageModelService

class WebsiteModule(Module):
    def configure(self, binder: Binder) -> Binder:
        binder.bind(PageModelService, to=PageModelService, scope=singleton)

    @provider
    @inject
    def provide_user_service(self) -> PageModelService:
        return PageModelService()

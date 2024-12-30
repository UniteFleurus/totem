from injector import Module, Binder, singleton, inject, provider

from .menu import MenuModelService
from .page import PageModelService

class WebsiteModule(Module):
    def configure(self, binder: Binder) -> Binder:
        binder.bind(PageModelService, to=PageModelService, scope=singleton)

    @provider
    @inject
    def provide_page_service(self) -> PageModelService:
        return PageModelService()

    @provider
    @inject
    def provide_menu_service(self) -> MenuModelService:
        return MenuModelService()

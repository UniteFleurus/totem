from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.config import settings, INSTALLED_ADDONS
from app.core.utils.module_loading import autodiscover_modules, module_has_submodule


# Generate the models python packages to import
models_to_import = []
for addon in INSTALLED_ADDONS:
    if module_has_submodule(f"app.{addon}", "models"):
        models_to_import.append(f"app.{addon}.models")


app = FastAPI()
register_tortoise(
    app,
    db_url=settings.DATABASE_URL,
    modules={'models': models_to_import},
    add_exception_handlers=True,
    generate_schemas=True,
)

# Auto discover app modules :
# - api: Restfull API, each app is responsible to expose its endpoint
autodiscover_modules(INSTALLED_ADDONS, "api", prefix="app")

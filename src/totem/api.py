from ninja import Redoc
from ninja_extra import NinjaExtraAPI


api_v1 = NinjaExtraAPI(
    version='1',
    docs=Redoc(),
    # openapi_extra={
    #    "info": {
    #        # "termsOfService": "https://example.com/terms/",
    #    }
    # },
    title="Totem API",
    description="This is a demo API with dynamic OpenAPI info section"
)

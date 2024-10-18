from django.urls import include, path
from oauth2_provider import views

base_urlpatterns = [
    path("authorize/", views.AuthorizationView.as_view(), name="authorize"),
    path("token/", views.TokenView.as_view(), name="token"),
    path("revoke-token/", views.RevokeTokenView.as_view(), name="revoke-token"),
    path("introspect/", views.IntrospectTokenView.as_view(), name="introspect"),
]

urlpatterns = [
    path(
        "o/",
        include((base_urlpatterns, "oauth2_provider"), namespace="oauth2_provider"),
    ),
]

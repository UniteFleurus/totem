from django.urls import path

from . import views


urlpatterns = [
    path('', views.HomePageView.as_view(), name='homepage'),
    path('page/<slug:slug>/', views.PageView.as_view(), name='page'),
]

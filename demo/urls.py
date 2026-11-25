"""URL routes for the demo project."""

from django.urls import include, path

from demo import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("playground/", views.PlaygroundView.as_view(), name="playground"),
    path("nested/", views.NestedView.as_view(), name="nested"),
    path("without-cotton/", views.PlainView.as_view(), name="plain"),
    path("sidebar-behavior/", views.SidebarBehaviorView.as_view(), name="sidebar_behavior"),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]

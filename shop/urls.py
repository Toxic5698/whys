from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path(
        "api/token/",
        jwt_views.TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/",
        jwt_views.TokenRefreshView.as_view(),
        name="token_refresh"
    ),
    path("register/", views.registerPage, name="register"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("import/", views.Import.as_view(), name="import"),
    path("detail/<str:model_name>/", views.RecordsList.as_view(), name="list"),
    path(
        "detail/<str:model_name>/<int:pk>/",
        views.RecordDetail.as_view(),
        name="detail"
    ),
    path("product/", views.ProductList.as_view(), name="product"),
]

from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt import views as jwt_views

# from .views import RecordsList, RecordDetail


urlpatterns = [
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),


    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),

    path('import/', views.Import.as_view(), name='import'),
    path('detail/', views.Records.as_view(), name='detail'),
    path('detail/<str:modelName>/', views.RecordsList.as_view(), name='detail'),
    path('detail/<str:modelName>/<int:pk>/', views.RecordDetail.as_view()),
    path('product/', views.ProductList.as_view(), name='product'),
    path('product/search/', views.ProductList.as_view(), name='search'),


]

urlpatterns = format_suffix_patterns(urlpatterns)

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

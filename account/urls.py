from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('accounts', views.AccountViewSet)

urlpatterns = [
    # path('accounts/', views.ListAccount.as_view()),
    # path('accounts/<str:pk>/', views.AccountDetail.as_view()),
    path('', include(router.urls)),
    path('deposit/', views.deposit),
    path('withdraw/', views.withdraw),
    path('create', views.CreateAccount.as_view()),
]

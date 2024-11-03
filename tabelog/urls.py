from django.urls import path, include
from .views import TopView

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('', TopView.as_view(), name='top')
]

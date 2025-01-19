from django.urls import path, include
from .views import UserDetailView, UserUpdateView, CreditRegisterView, CreditDeleteView, CreditUpdateView, ShopListView, ShopDetailView, ReviewCreateView, ReviewEditView, ReviewDeleteView, fav_shop, BookingCreateView, BookingListView, BookingDeleteView, BookingEditView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('', ShopListView.as_view(), name='top'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user'),
    path('user/update/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
    path('credit/register/', CreditRegisterView.as_view(), name='credit-register'),
    path('credit/delete/', CreditDeleteView.as_view(), name='credit-delete'),
    path('credit/update/', CreditUpdateView.as_view(), name='credit-update'),
    path('shop/<int:pk>/', ShopDetailView.as_view(), name='shop-detail'),
    path('user/<int:pk>/fav/', fav_shop, name='fav-shop'),
    path('shop/<int:pk>/review/create', ReviewCreateView.as_view(), name='review-create'),
    path('shop/<int:shop_pk>/review/<int:pk>/edit/', ReviewEditView.as_view(), name='review-edit'),
    path('shop/<int:shop_pk>/review/<int:pk>/delete/', ReviewDeleteView.as_view(), name='review-delete'),
    path('user/<int:pk>/booking/', BookingListView.as_view(), name='booking'),
    path('shop/<int:pk>/booking/create/', BookingCreateView.as_view(), name='booking-create'),
    path('shop/<int:shop_pk>/booking/<int:pk>/delete/', BookingDeleteView.as_view(), name='booking-delete'),
    path('shop/<int:shop_pk>/booking/<int:pk>/edit/', BookingEditView.as_view(), name='booking-edit')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
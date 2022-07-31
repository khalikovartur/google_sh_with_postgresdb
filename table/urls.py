from django.urls import path
from . views import OrderListView, OrderDetailView

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('<pk>', OrderDetailView.as_view(), name='order_detail')
]
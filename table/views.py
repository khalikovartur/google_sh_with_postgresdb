from .models import Order
from django.views.generic import ListView, DetailView

class OrderListView(ListView):
    model = Order
    context_object_name = 'order_list'
    template_name = 'order_list.html'
    
class OrderDetailView(DetailView):
    model = Order
    context_object_name = 'order'
    template_name = 'order_detail.html'
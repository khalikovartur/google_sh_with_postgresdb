from django.db import models
from django.urls import reverse


class Order(models.Model):
    field_number = models.IntegerField(blank=True)
    order_number = models.IntegerField(primary_key=True)
    cost_in_dollars = models.IntegerField()
    deliver_time = models.DateField(blank=True)
    cost_in_rubles = models.DecimalField(max_digits=50,
                                         decimal_places=2)
    
    class Meta:
        ordering = ('field_number',)
    
    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': str(self.pk)})
    

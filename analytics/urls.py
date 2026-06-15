from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('chart/<int:product_id>/', views.generate_price_chart, name='chart'),
]

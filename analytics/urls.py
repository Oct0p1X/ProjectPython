from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('',views.index, name = 'index'),#главная страница
    path('chart/<int:product_id>/', views.generate_price_chart, name='chart'),
    path('competitor/<int:pk/edit/', views.edit_competitor, name='edit_competitor'),
]

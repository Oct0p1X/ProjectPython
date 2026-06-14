from django.contrib import admin
from .models import Product, CompetitorPriceHistory, DumpingAlert

@admin.register(Product)#Настройка параметров отображения
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'nm_id', 'my_current_price', 'min_acceptable_price', 'user')
    search_fields = ('title', 'nm_id')
    list_filter = ('created_at',)

@admin.register(CompetitorPriceHistory)
class CompetitorPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'competitor_nm_id', 'competitor_name', 'price_with_discount', 'checked_at')
    search_fields = ('competitor_name', 'competitor_nm_id')
    list_filter = ('checked_at',)

@admin.register(DumpingAlert)
class DumpingAlertAdmin(admin.ModelAdmin):
    list_display = ('product', 'detected_at', 'lowest_competitor_price', 'deviation_percent', 'lost_profit_rub')
    search_fields = ('product__title',)
    list_filter = ('detected_at',)
#list_display - какие поля модели должны быть видны в таблице
#search_fields -строка поиска над списком записей (поисковик)

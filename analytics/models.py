from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Селлер')
    nm_id = models.CharField(max_length=50, verbose_name='Артикул WB')
    title = models.CharField(max_length=255, verbose_name='Название товара')
    my_current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Моя текущая цена')
    min_acceptable_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Минимально допустимая цена')
    tolerance_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='Процент терпимости (%)')
    
    target_competitor_urls = models.TextField(blank=True, null=True, verbose_name='Артикулы конкурентов (через запятую)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def str(self):
        return f"{self.title} ({self.nm_id})"


class CompetitorPriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    competitor_nm_id = models.CharField(max_length=50, verbose_name='Артикул конкурента')
    competitor_name = models.CharField(max_length=255, verbose_name='Имя конкурента')
    price_before_discount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена до скидки', null=True, blank=True)
    price_with_discount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена со скидкой')
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name='Время проверки')

    def str(self):
        return f"{self.competitor_name} - {self.price_with_discount} руб."


class DumpingAlert(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alerts')
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name='Время обнаружения')
    lowest_competitor_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Мин. цена конкурента')
    deviation_percent = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Процент отклонения')
    lost_profit_rub = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Упущенная выгода (руб)')

    def str(self):
        return f"Алерт: {self.product.title} - падение на {self.deviation_percent}%"
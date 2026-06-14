from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    #Модель №1 Товар продавца который нужно защитить от демпинга
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь (Селлер)")
    nm_id = models.BigIntegerField(unique=True, verbose_name="Артикул WB")
    title = models.CharField(max_length=255, verbose_name="Название товара")
    my_current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Текущая цена селлера")
    min_acceptable_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Критический порог цены (демпинг)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Товар селлера"
        verbose_name_plural = "Товары селлеров"

    def str(self):
        return f"{self.title} ({self.nm_id})"


class CompetitorPriceHistory(models.Model):
    #Модель №2 История изменения цен конкурентов
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="price_history", verbose_name="Наш товар")
    competitor_nm_id = models.BigIntegerField(verbose_name="Артикул конкурента")
    competitor_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Имя конкурента")
    price_before_discount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена до скидки")
    price_with_discount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Финальная цена")
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name="Время проверки")

    class Meta:
        verbose_name = "История цен конкурента"
        verbose_name_plural = "История цен конкурентов"
        ordering = ['-checked_at']

    def str(self):
        return f"{self.competitor_name} - {self.price_with_discount} руб."


class DumpingAlert(models.Model):
    #Модель №3 Сигнал о зафиксированном демпинге
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="alerts", verbose_name="Наш товар")
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name="Время обнаружения")
    lowest_competitor_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Минимальная цена конкурента")
    deviation_percent = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Процент отклонения")
    lost_profit_rub = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Упущенная выгода (руб.)")

    class Meta:
        verbose_name = "Сигнал о демпинге"
        verbose_name_plural = "Сигналы о демпинге"
        ordering = ['-detected_at']

    def str(self):
        return f"Демпинг: {self.product.title} (-{self.deviation_percent}%)"

import random
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from analytics.models import Product, CompetitorPriceHistory, DumpingAlert


#тесты для проверки работспособности
class Command(BaseCommand):
    help = 'Генерация 15 тестовых записей'

    def handle(self, *args, **kwargs):
        # 1. Создаем тестового пользователя-селлера
        user, created = User.objects.get_or_create(username='test_seller')
        if created:
            user.set_password('password123')
            user.save()

        #Очищаем старые тестовые данные
        Product.objects.filter(user=user).delete()

        #Создаем товары
        products_data = [
            {'nm_id': 111111, 'title': 'Беспроводные наушники', 'my_price': '2500.00', 'min_price': '2000.00'},
            {'nm_id': 222222, 'title': 'Умные часы', 'my_price': '4500.00', 'min_price': '3800.00'},
            {'nm_id': 333333, 'title': 'Чехол для телефона', 'my_price': '500.00', 'min_price': '350.00'}
        ]

        products = []
        for p in products_data:
            obj = Product.objects.create(
                user=user,
                nm_id=p['nm_id'],
                title=p['title'],
                my_current_price=Decimal(p['my_price']),
                min_acceptable_price=Decimal(p['min_price'])
            )
            products.append(obj)

        competitor_names = ['ИП Иванов', 'MegaStore', 'WB-Shop', 'ГаджетПлюс']

        #создаем 15 записей истории цен
        for i in range(15):
            product = random.choice(products)
            price_drop = Decimal(random.randint(50, 800))#Искуственные цены на большом отрезке что бы увидеть отличие от нормы
            comp_price = product.my_current_price - price_drop

            history = CompetitorPriceHistory.objects.create(
                product=product,
                competitor_nm_id=product.nm_id + random.randint(1, 9),
                competitor_name=random.choice(competitor_names),
                price_before_discount=comp_price + Decimal('500.00'),
                price_with_discount=comp_price,
            )
            
            #сдвигаем время создания в прошлое для красивого графика
            history.checked_at = timezone.now() - timedelta(days=15-i)
            history.save()

            #Если зафиксирован демпинг создаем инцидент
            if comp_price < product.min_acceptable_price:
                deviation = ((product.min_acceptable_price - comp_price) / product.min_acceptable_price) * Decimal('100.0')
                lost = product.my_current_price - comp_price
                
                DumpingAlert.objects.create(
                    product=product,
                    lowest_competitor_price=comp_price,
                    deviation_percent=round(deviation, 2),
                    lost_profit_rub=round(lost, 2)
                )

        self.stdout.write(self.style.SUCCESS('Успешно создано более 15 тестовых записей'))

from decimal import Decimal
from .models import Product, CompetitorPriceHistory, DumpingAlert
from .services import get_wb_product_data

def run_competitor_analysis(product):
    """
    Функция берет товар пользователя, извлекает артикулы конкурентов, 
    опрашивает их цены через API и фиксирует демпинг.
    """
    if not product.target_competitor_urls:
        return

    #разбиваем строку из формы в список артикулов
    raw_urls = product.target_competitor_urls.split(',')
    competitor_ids = [nm_id.strip() for nm_id in raw_urls if nm_id.strip().isdigit()]

    #осматриваем каждого конкурента по очереди
    for comp_id in competitor_ids:
        data = get_wb_product_data(comp_id)
        if not data:
            continue

        comp_price = Decimal(str(data['price_with_discount']))
        
        #сохраняем историю цен конкурента для будущих графиков
        CompetitorPriceHistory.objects.create(
            product=product,
            competitor_nm_id=comp_id,
            competitor_name=data['name'],
            price_before_discount=Decimal(str(data['price_before_discount'])),
            price_with_discount=comp_price
        )

        #проверка демпинга
        tolerance_value = product.min_acceptable_price * (product.tolerance_percent / Decimal('100.00'))
        dumping_threshold = product.min_acceptable_price - tolerance_value

        if comp_price < dumping_threshold:
            #расчет потерь
            deviation = ((product.min_acceptable_price - comp_price) / product.min_acceptable_price) * Decimal('100.00')
            lost_profit = product.my_current_price - comp_price

            #создаем событие
            DumpingAlert.objects.create(
                product=product,
                lowest_competitor_price=comp_price,
                deviation_percent=round(deviation, 2),
                lost_profit_rub=round(lost_profit, 2)
            )
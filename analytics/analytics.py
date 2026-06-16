from decimal import Decimal
from .models import Product, CompetitorPriceHistory, DumpingAlert
from .services import get_wb_product_data

def run_price_check(product, competitor_nm_id):
    #Основной алгоритм: получает реальную цену конкурента через API, сохраняет в историю и проверяет на демпинг с учетом пользовательской процентной погрешности.

    #Получаем данные с WB
    wb_data = get_wb_product_data(competitor_nm_id)
    
    if not wb_data['success']:
        return False, wb_data.get('error')
        
    #сохраняем цену конкурента в историю
    history = CompetitorPriceHistory.objects.create(
        product=product,
        competitor_nm_id=competitor_nm_id,
        competitor_name=wb_data['brand'],
        price_before_discount=wb_data['price_before_discount'],
        price_with_discount=wb_data['price_with_discount']
    )
    
    #проверяем демпинг с учетом процента КОНКРЕТНОГО товара
    competitor_price = Decimal(str(wb_data['price_with_discount']))
    
    #вычисляем динамическую границу в рублях из настроек селлера
    tolerance_rubles = product.min_acceptable_price * (product.tolerance_percent / Decimal('100'))
    
    if competitor_price < (product.min_acceptable_price - tolerance_rubles):
        
        #считаем процент отклонения
        deviation = ((product.min_acceptable_price - competitor_price) / product.min_acceptable_price) * 100
        
        #считаем упущенную выгоду
        lost_profit = product.my_current_price - competitor_price
        
        #фиксируем инцидент в базе данных
        DumpingAlert.objects.create(
            product=product,
            lowest_competitor_price=competitor_price,
            deviation_percent=round(deviation, 2),
            lost_profit_rub=lost_profit
        )
        return True, f"Зафиксирован демпинг, отклонение превысило {product.tolerance_percent}%."
        
    return True, "Цена в пределах допустимой нормы"

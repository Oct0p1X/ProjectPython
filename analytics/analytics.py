from decimal import Decimal
from .models import Product, CompetitorPriceHistory, DumpingAlert
from .services import fetch_wb_price

def analyze_competitor_price(product, competitor_nm_id):
    #Основная функция запрашивает цену по API и сохраняет в историю
    #проверяет на демпинг и рассчитывает упущенную выгоду
    #получаем свежие данные через наш сервис интеграции
    api_response = fetch_wb_price(competitor_nm_id)
    
    if not api_response.get('success'):
        print(f"Ошибка парсинга для артикула {competitor_nm_id}: {api_response.get('error')}")
        return False
        
    #преобразуем полученные числа в точный тип Decimal для финансовых расчетов
    price_with_discount = Decimal(str(api_response['price_with_discount']))
    price_before_discount = Decimal(str(api_response['price_before_discount']))
    
    #сохраняем результат в историю цен
    CompetitorPriceHistory.objects.create(
        product=product,
        competitor_nm_id=competitor_nm_id,
        competitor_name=api_response['competitor_name'],
        price_before_discount=price_before_discount,
        price_with_discount=price_with_discount)
    
    #блок проверки условий демпинга
    if price_with_discount < product.min_acceptable_price:
        
        #расчет процента отклонения от допустимого минимума
        deviation = ((product.min_acceptable_price - price_with_discount) / product.min_acceptable_price) * Decimal('100.0')
        
        #расчет упущенной выгоды (потеря маржи с каждой проданной единицы)
        lost_profit = product.my_current_price - price_with_discount
        
        #фиксируем инцидент
        DumpingAlert.objects.create(
            product=product,
            lowest_competitor_price=price_with_discount,
            deviation_percent=round(deviation, 2),
            lost_profit_rub=round(lost_profit, 2))
        return True #зафиксирован
        
    return False #все в норме

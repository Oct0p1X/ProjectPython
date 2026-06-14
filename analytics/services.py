import requests
import logging


logger = logging.getLogger(name)

def fetch_wb_price(nm_id):
    #Функция делает GET запрос к открытому API Wildberries и возвращает актуальную цену товара по артикулу (nm_id)
    #Публичный эндпоинт карточки товара
    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&nm={nm_id}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Проверка на ошибки HTTP (404, 500 и т.д.)
        data = response.json()
        
        # Парсинг JSON ответа. Структура WB: data -> products -> [0] -> salePriceU
        if data and 'data' in data and 'products' in data['data'] and len(data['data']['products']) > 0:
            product_data = data['data']['products'][0]
            
            #Названия продавцов и товаров
            brand = product_data.get('brand', 'Неизвестный бренд')
            name = product_data.get('name', 'Без названия')
            competitor_name = f"{brand} - {name}"
            
            #WB хранит цены в копейках из-за чего делим на 100
            price_with_discount = product_data.get('salePriceU', 0) / 100
            price_before_discount = product_data.get('priceU', 0) / 100
            
            return {
                'success': True,
                'competitor_name': competitor_name,
                'price_before_discount': price_before_discount,
                'price_with_discount': price_with_discount
            }
        else:
            return {'success': False, 'error': 'Товар не найден в выдаче API'}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при обращении к API WB для артикула {nm_id}: {e}")
        return {'success': False, 'error': str(e)}

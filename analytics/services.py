import requests

def get_wb_product_data(nm_id):
    #Публичный api WB для получения данных по артикулу
    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&nm={nm_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Проверка вернул ли маркетплейс данные о товаре
        if data.get('data') and data['data'].get('products'):
            product = data['data']['products'][0]
            
            # В API WB цены хранятся с двумя лишними нулями на конце (копейки), поэтому делим на 100
            price_before = product.get('priceU', 0) / 100
            price_discount = product.get('salePriceU', 0) / 100
            
            return {
                'success': True,
                'name': product.get('name', 'Неизвестно'),
                'brand': product.get('brand', 'Неизвестно'),
                'price_before_discount': price_before,
                'price_with_discount': price_discount
            }
        return {'success': False, 'error': 'Товар не найден'}
        
    except requests.RequestException as e:
        return {'success': False, 'error': f'Ошибка соединения с API: {e}'}

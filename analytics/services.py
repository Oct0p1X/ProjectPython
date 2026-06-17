import requests

def get_wb_product_data(nm_id):
    #публичный api Wildberries для получения цен
    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&nm={nm_id}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('data', {}).get('products'):
            product = data['data']['products'][0]
            #цены в api Wildberries умножены на 100 поэтому делим
            price_with_discount = product.get('salePriceU', 0) / 100
            price_before_discount = product.get('priceU', 0) / 100
            name = product.get('name', 'Неизвестный товар')
            
            return {
                'price_with_discount': price_with_discount,
                'price_before_discount': price_before_discount,
                'name': name
            }
    except Exception as e:
        print(f"Ошибка парсинга артикула {nm_id}: {e}")
        
    return None
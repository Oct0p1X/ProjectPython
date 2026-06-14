import io
import urllib
import base64
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from django.shortcuts import render, get_object_or_404
from .models import Product, CompetitorPriceHistory


def generate_price_chart(request, product_id):
    #рисует график динамики цен конкурентов для конкретного товара

    #Получаем наш товар из базы данных
    product = get_object_or_404(Product, pk=product_id)
    
    #Выгружаем историю цен конкурентов по этому товару
    history = CompetitorPriceHistory.objects.filter(product=product).values('checked_at', 'price_with_discount', 'competitor_name')
    
    if not history:
        #Если данных нет возвращаем простой шаблон с сообщением
        return render(request, 'analytics/chart.html', {'product': product, 'chart': None, 'error': 'Нет данных для построения графика'})

    #передаем данные в DataFrame
    df = pd.DataFrame(list(history))
    
    #сортировка по времени
    df['checked_at'] = pd.to_datetime(df['checked_at'])
    df = df.sort_values(by='checked_at')
    
    #настройка графиков
    plt.switch_backend('AGG') #отключаем интерактивный режим
    plt.figure(figsize=(10, 5))
    
    #группируем данные по конкурентам, чтобы нарисовать линию для каждого из них
    for name, group in df.groupby('competitor_name'):
        plt.plot(group['checked_at'], group['price_with_discount'], marker='o', label=name)

    #Рисуем линию нашего критического порога
    plt.axhline(y=float(product.min_acceptable_price), color='r', linestyle='--', label='Наш порог демпинга')
    
    #Оформление графика (подписи)
    plt.title(f'Динамика цен по товару: {product.title}')
    plt.xlabel('Дата и время')
    plt.ylabel('Цена (руб.)')
    plt.legend()
    plt.grid(True)
    
    #форматирование дат на оси х
    plt.gca().xaxis.set_major_formatter(DateFormatter('%d-%m %H:%M'))
    plt.gcf().autofmt_xdate()

    #Сохранение графика в строку base64 для передачи в HTML
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    string = base64.b64encode(buffer.read())
    uri = urllib.parse.quote(string)
    
    plt.close()

    #возвращаем шаблон передавая в него сгенерированный URI картинки
    return render(request, 'analytics/chart.html', {'product': product, 'chart': uri})

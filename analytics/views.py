import io
import urllib
import base64
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, CompetitorPriceHistory
from .forms import ProductForm
from .services import get_wb_product_data


@login_required
def index(request):

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            
            #автоматический сбор названия и цены через API по введенному артикулу
            api_data = get_wb_product_data(product.nm_id)
            if api_data:
                product.title = api_data.get('name', 'Неизвестный товар')
                product.my_current_price = api_data.get('price_with_discount', 0)
            else:
                product.title = "Товар не найден"
                product.my_current_price = 0
                
            product.save()
            return redirect('analytics:index')
    else:
        form = ProductForm()

    products = Product.objects.filter(user=request.user)
    return render(request, 'analytics/index.html', {'products': products, 'form': form})

@login_required
def generate_price_chart(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    history = CompetitorPriceHistory.objects.filter(product=product).order_by('checked_at')

    if not history.exists():
        # Если истории еще нет, выводим шаблон с сообщением
        return render(request, 'analytics/chart.html', {'product': product, 'error': 'Нет данных для графика.'})

    data = []
    for h in history:
        data.append({
            'date': h.checked_at,
            'price': h.price_with_discount,
            'competitor_name': h.competitor_name
        })
    df = pd.DataFrame(data)

    #генерация графиков
    plt.figure(figsize=(10, 5))
    
    #разделяем данные, чтобы у каждого конкурента была своя линия
    for name, group in df.groupby('competitor_name'):
        plt.plot(group['date'], group['price'], marker='o', label=name)

    #рисуем красную пунктирную линию визуализация критического порога
    plt.axhline(y=float(product.min_acceptable_price), color='r', linestyle='--', label='Мин. допустимая цена')

    plt.title(f'Динамика цен конкурентов: {product.title}')
    plt.xlabel('Дата и время')
    plt.ylabel('Цена (руб.)')
    plt.legend()
    plt.grid(True)
    
    #форматирование дат на оси X
    ax = plt.gca()
    ax.xaxis.set_major_formatter(DateFormatter('%d.%m %H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    #конвертация изображения
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close()

    return render(request, 'analytics/chart.html', {'product': product, 'chart_uri': uri})
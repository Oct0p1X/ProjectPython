import io
import urllib
import base64
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, CompetitorPriceHistory
from .forms import ProductForm, CompetitorPriceForm
from .services import get_wb_product_data


@login_required
def index(request):
    products = Product.objects.filter(user=request.user)
    
    product_form = ProductForm()
    competitor_form = CompetitorPriceForm()

    if request.method == 'POST':
        #пользователь добавляет свой новый товар
        if 'add_product' in request.POST:
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                product = product_form.save(commit=False)
                product.user = request.user
                product.save()
                return redirect('analytics:index')

        #пользователь добавляет конкурента к существующему товару
        elif 'add_competitor' in request.POST:
            competitor_form = CompetitorPriceForm(request.POST)
            product_id = request.POST.get('product_id') 
            
            if competitor_form.is_valid() and product_id:
                competitor = competitor_form.save(commit=False)
                competitor.product = get_object_or_404(Product, id=product_id, user=request.user)
                competitor.save()
                return redirect('analytics:index')

    context = {
        'products': products,
        'product_form': product_form,
        'competitor_form': competitor_form,
    }
    return render(request, 'analytics/index.html', context)

@login_required
def generate_price_chart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    #история цен конкурентов
    history = CompetitorPriceHistory.objects.filter(product=product).order_by('checked_at')
    
    #если конкурентов еще не добавляли
    if not history.exists():
        return render(request, 'analytics/chart.html', {
            'product': product, 
            'error': 'История цен конкурентов пока пуста.'
        })

    #передаем данные в pandas
    df = pd.DataFrame(list(history.values('competitor_nm_id', 'price_with_discount', 'checked_at')))
    
    #если датафрейм почему то пуст
    if df.empty:
        return render(request, 'analytics/chart.html', {
            'product': product, 
            'error': 'Не удалось обработать данные для графика.'
        })

    plt.figure(figsize=(10, 5))
    
    for name, group in df.groupby('competitor_nm_id'):
        plt.plot(group['checked_at'], group['price_with_discount'], marker='o', label=f'Артикул {name}')

    if product.min_acceptable_price:
        plt.axhline(y=product.min_acceptable_price, color='r', linestyle='--', label='Мой минимум (порог)')

    #оформление графика
    plt.title(f'Динамика демпинга: {product.title}')
    #plt.xlabel('Дата фиксации')
    plt.ylabel('Цена конкурента (руб.)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close()

    return render(request, 'analytics/chart.html', {'product': product, 'chart': uri})
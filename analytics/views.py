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
    product = get_object_or_404(Product, id=product_id, user=request.user)
    history = CompetitorPriceHistory.objects.filter(product=product).order_by('checked_at')

    #защита от пустой базы
    if not history.exists():
        return render(request, 'analytics/chart.html', {
            'product': product, 
            'chart_uri': None,
            'dumping_info': []
        })

    #Генерируем график
    df = pd.DataFrame(list(history.values('competitor_name', 'competitor_nm_id', 'price_with_discount', 'checked_at')))
    plt.figure(figsize=(10, 5))
    
    for name, group in df.groupby('competitor_nm_id'):
        plt.plot(group['checked_at'], group['price_with_discount'], marker='o', label=f'Артикул: {name}')

    plt.axhline(y=float(product.min_acceptable_price), color='r', linestyle='--', label='Мин. порог цены')
    plt.title(f'Динамика цен для {product.title}')
    plt.xlabel('Дата')
    plt.ylabel('Цена (руб)')
    plt.legend()
    plt.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close()

    #поиск демпингующих конкурентов
    dumping_info = []
    tolerance_val = product.min_acceptable_price * (product.tolerance_percent / 100)
    threshold = product.min_acceptable_price - tolerance_val

    latest_history = CompetitorPriceHistory.objects.filter(product=product).order_by('-checked_at')
    processed_skus = set()

    for record in latest_history:
        if record.competitor_nm_id not in processed_skus:
            processed_skus.add(record.competitor_nm_id)
            if record.price_with_discount < threshold:
                diff = product.my_current_price - record.price_with_discount
                dumping_info.append({
                    'sku': record.competitor_nm_id,
                    'price': record.price_with_discount,
                    'diff': diff
                })

    return render(request, 'analytics/chart.html', {
        'product': product, 
        'chart_uri': uri,
        'dumping_info': dumping_info  
    })
def edit_competitor(request, pk):
    competitor = get_object_or_404(CompetitorPriceHistory, id=pk, product__user=request.user)
    
    if request.method == 'POST':
        form = CompetitorPriceForm(request.POST, instance=competitor)
        if form.is_valid():
            form.save()
            return redirect('analytics:index')
    else:
        form = CompetitorPriceForm(instance=competitor)
        
    return render(request, 'analytics/edit_competitor.html', {'form': form, 'competitor': competitor})
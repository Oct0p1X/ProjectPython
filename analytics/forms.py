from django import forms
from .models import Product, CompetitorPriceHistory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['nm_id', 'title', 'my_current_price', 'min_acceptable_price', 'tolerance_percent']
        widgets = {
            'nm_id': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Артикул вашего товара (например: 12345678)'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Название товара'
            }),
            'my_current_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваша текущая цена'
            }),
            'min_acceptable_price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Минимальная цена (например: 1500)'
            }),
            'tolerance_percent': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Процент терпимости (например: 5)'
            }),
            'target_competitor_urls': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Артикулы конкурентов через запятую (например: 111111, 222222)'
            }),
        }

    def clean_nm_id(self):
        nm_id = self.cleaned_data.get('nm_id')
        nm_id_str = str(nm_id)
        if not nm_id_str.isdigit():
            raise forms.ValidationError('Артикул должен состоять только из цифр.')
        return nm_id
    
class CompetitorPriceForm(forms.ModelForm):
    class Meta:
        model = CompetitorPriceHistory
        fields = ['competitor_nm_id', 'price_with_discount']
        widgets = {
            'competitor_nm_id': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Артикул конкурента'}),
            'price_with_discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'Текущая цена конкурента'}),
        }
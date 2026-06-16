from django import forms
from django.core.exceptions import ValidationError
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        #выводим все нужные поля
        fields = ['nm_id', 'title', 'my_current_price', 'min_acceptable_price', 'tolerance_percent']
        
        #настраиваем внешний вид полей
        widgets = {
            'nm_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Артикул WB'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название товара'}),
            'my_current_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_acceptable_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'tolerance_percent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 2 (в процентах)'}),
        }
        
        labels = {
            'nm_id': 'Артикул товара',
            'title': 'Название',
            'my_current_price': 'Ваша текущая цена (руб)',
            'min_acceptable_price': 'Порог демпинга (руб)',
            'tolerance_percent': 'Допустимая погрешность (%)',
        }

    def clean_nm_id(self):
        nm_id = self.cleaned_data.get('nm_id')
        
        #проверка что артикул состоит только из цифр
        if not nm_id.isdigit():
            raise ValidationError("Артикул Wildberries должен состоять только из цифр.")
            
        #пример проверки на длину
        if len(nm_id) < 5 or len(nm_id) > 15:
            raise ValidationError("Некорректная длина артикула.")
            
        return nm_id

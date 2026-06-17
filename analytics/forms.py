from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['nm_id', 'min_acceptable_price', 'tolerance_percent', 'target_competitor_urls']
        widgets = {
            'nm_id': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Артикул вашего товара (например: 12345678)'
            }),
            'min_acceptable_price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Минимальная цена (например: 1500)'
            }),
            'tolerance_percent': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Процент терпимости (например: 5)'
            }),
            # Используем Textarea, чтобы пользователю было удобно вводить несколько артикулов
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
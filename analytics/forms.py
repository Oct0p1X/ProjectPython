from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        #какие поля из модели выводить в форме
        fields = ['nm_id', 'title', 'my_current_price', 'min_acceptable_price']
        #настраиваем классы Bootstrap для красивого отображения
        widgets = {
            'nm_id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 123456789'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название товара'}),
            'my_current_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_acceptable_price': forms.NumberInput(attrs={'class': 'form-control'}),}

    def clean_nm_id(self):
        #проверка корректности артикула WB
        nm_id = self.cleaned_data.get('nm_id')
        if nm_id <= 0:
            raise forms.ValidationError("Артикул Wildberries должен быть положительным числом.")
        #доп проверка на длину артикула для вб от 5 до 15)
        if len(str(nm_id)) < 5:
             raise forms.ValidationError("Слишком короткий артикул. Проверьте правильность ввода.")
        return nm_id

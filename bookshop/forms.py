from django import forms
from django.core.exceptions import ValidationError

from .models import Book
from ckeditor.widgets import CKEditorWidget
from ckeditor.fields import RichTextFormField

class BookForm(forms.ModelForm):
    full_description = forms.CharField(widget=CKEditorWidget(), required=False)
    class Meta:
        model = Book
        fields = ['title', 'slug', 'author', 'category', 'publication_year', 'description', 'price',
                  'is_discount', 'discount', 'image', 'quantity', 'is_featured', 'full_description']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Narx musbat bo'lishi kerak.")
        return price

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount < 0 or discount > 100:
            raise forms.ValidationError("Chegirma foizi 0 va 100 orasida bo'lishi kerak.")
        return discount

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 0:
            raise forms.ValidationError("Kitob soni manfiy bo'lmasligi kerak.")
        return quantity

    def update(self, book_instance):
        book_instance.title = self.cleaned_data.get('title')
        book_instance.slug = self.cleaned_data.get('slug')
        book_instance.author = self.cleaned_data.get('author')
        book_instance.category = self.cleaned_data.get('category')
        book_instance.publication_year = self.cleaned_data.get('publication_year')
        book_instance.description = self.cleaned_data.get('description')
        book_instance.price = self.cleaned_data.get('price')
        book_instance.is_discount = self.cleaned_data.get('is_discount')
        book_instance.discount = self.cleaned_data.get('discount')
        if self.cleaned_data.get('image'):
            book_instance.image = self.cleaned_data.get('image')
        book_instance.cart_quantity = self.cleaned_data.get('quantity')
        book_instance.is_featured = self.cleaned_data.get('is_featured')

        book_instance.save()
        return book_instance



class CommentForm(forms.Form):
    rating = forms.IntegerField(
        required=True,
        label="Your Rating",
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'rating',
            'min': '1',
            'max': '5',
            'type': 'hidden',
            'value': 1
        })
    )

    content = forms.CharField(
        required=True,
        label="Your Review",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'content',
            'rows': 5,
            'cols': 30,
            'name': 'content',
            'placeholder': 'Typing here...'
        })
    )

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not (1 <= rating <= 5):
            raise ValidationError("Mahsulotni 1 dan 5gacha baholang")
        return rating

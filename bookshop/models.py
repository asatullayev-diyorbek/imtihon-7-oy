from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField

from user.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nomi")
    slug = models.SlugField(max_length=100, verbose_name="Slug")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'


class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Nomi")
    slug = models.SlugField(max_length=200, verbose_name="Slug")
    author = models.CharField(max_length=100, verbose_name="Muallif")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategoriya")
    publication_year = models.IntegerField(verbose_name="Yili")
    description = models.TextField(verbose_name="Tavsif")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Narxi (so'm)")
    is_discount = models.BooleanField(default=False, verbose_name="Chegirmadami?")
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name="Chegirish qiymati (%)")
    image = models.ImageField(upload_to='books/', verbose_name="Rasmi")
    quantity = models.IntegerField(verbose_name="Soni")
    views = models.IntegerField(default=0, verbose_name="Ko'rishlar")
    is_featured = models.BooleanField(default=False, verbose_name="Tavsiya qilinsinmi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")
    full_description = RichTextField(null=True, blank=True, default="Yo'q", verbose_name="Tavsif")

    def __str__(self):
        return self.author + ' - ' + self.title

    def get_image(self):
        if self.image:
            return self.image.url
        return None

    class Meta:
        verbose_name = 'Kitob'
        verbose_name_plural = 'Kitoblar'
        ordering = ['-created_at']

    def current_price(self):
        if self.is_discount:
            return round(self.price * (1 - self.discount / 100), 2)
        return self.price

    def get_rating(self):
        comments = self.comment_set.all()
        if comments.exists():
            return '{:.2f}'.format(sum(comment.rating for comment in comments) / comments.count())
        return 0

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Book, self).save(*args, **kwargs)


class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Kitob")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    rating = models.IntegerField(default=0, verbose_name="Baho")
    content = models.TextField(verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqtih")

    def __str__(self):
        return self.user.username +'-'+ self.book.title

    class Meta:
        verbose_name = 'Izoh'
        verbose_name_plural = 'Izohlar'

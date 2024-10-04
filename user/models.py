from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    image = models.ImageField(upload_to='users/profile/', null=True, blank=True)
    phone = models.CharField(max_length=13, null=True, blank=True)
    address = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def get_image(self):
        if self.image:
            return self.image.url
        return "https://png.pngitem.com/pimgs/s/111-1114675_user-login-person-man-enter-person-login-icon.png"

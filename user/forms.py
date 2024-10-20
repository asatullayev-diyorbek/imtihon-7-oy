from django import forms
from user.models import User
import re
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList


class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(
        label='First name', max_length=30, required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'First name',
                'class': 'form-control'
            }
        )
    )
    last_name = forms.CharField(
        label='Last name', max_length=30, required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Last name',
                'class': 'form-control'
            }
        )
    )
    username = forms.CharField(
        label='Username', max_length=30, required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Username',
                'class': 'form-control'
            }
        )
    )
    email = forms.EmailField(
        label='Email', required=True,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Emial',
                'class': 'form-control'
            }
        )
    )
    password1 = forms.CharField(
        label='Make password', required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password',
                'class': 'form-control'
            }
        )
    )
    password2 = forms.CharField(
        label='Make password', required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password',
                'class': 'form-control'
            }
        )
    )
    phone = forms.CharField(label='Phone number', max_length=15, required=False)
    address = forms.CharField(label='Address', max_length=150, required=False)
    image = forms.ImageField(label='Profile picture', required=False)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and len(password1) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long')
        if password2 and password1 != password2:
            raise forms.ValidationError('Passwords must match')
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email address already exists')
        if (not email.endswith('@gmail.com')) and (not email.endswith('@mail.ru')) and (not email.endswith('@yandex.com')):
            raise forms.ValidationError('Email must be from gmail.com, yandex.com or mail.ru')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username[0].isalpha():
            raise forms.ValidationError('Username birinchi belgisi harf bo\'lishi kerak')
        if not re.match(r'^[A-Za-z][A-Za-z0-9_]*$', username):
            raise forms.ValidationError('Username faqat harflar, raqamlar va _ belgisidan iborat bo\'lishi mumkin')
        if len(username) < 5:
            raise forms.ValidationError('Kamida 5ta belgi')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists')
        return username

    def create_user(self):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'phone', 'address', 'image')


class LoginForm(forms.ModelForm):
    username = forms.CharField(
        label='Username', max_length=30, required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Username',
                'class': 'form-control',
                'id': 'username'
            }
        )
    )
    password = forms.CharField(
        label='Password', required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password',
                'class': 'form-control',
                'id': 'password1'
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'password')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username does not exist')
        user = User.objects.get(username=username)
        if not user.is_active:
            raise forms.ValidationError("Unverified user.   <a href='/user/activate/resend-activation/'>Click here</a>")
        if not user.check_password(password):
            raise forms.ValidationError('Incorrect password')
        self.cleaned_data['user'] = self.get_user()
        return self.cleaned_data

    def get_user(self):
        username = self.cleaned_data.get('username')
        return User.objects.get(username=username)


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        label="Amaldagi parol",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control mb-2',
                'id': 'current_password'
            }
        )
    )
    new_password = forms.CharField(
        label="Yangi parol",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control mb-2',
                'id': 'new_password'
            }
        )
    )
    confirm_new_password = forms.CharField(
        label="Yangi parolni qayta kiriting",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control mb-2',
                'id': 'confirm_new_password'
            }
        )
    )

    def __init__(
            self,
            data=None,
            files=None,
            auto_id="id_%s",
            prefix=None,
            initial=None,
            error_class=ErrorList,
            label_suffix=None,
            empty_permitted=False,
            field_order=None,
            use_required_attribute=None,
            renderer=None,
    ):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, field_order,
                         use_required_attribute, renderer)
        self.user = None

    def set_user(self, user):
        assert isinstance(user, User)
        self.user = user

    def clean_current_password(self):
        user = self.user
        current_password = self.cleaned_data['current_password']
        if not user.check_password(current_password):
            raise ValidationError("Amaldagi parolga to'g'ri kelmadi!")
        return current_password

    def clean_new_password(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")

        if new_password and len(new_password) < 8:
            raise ValidationError("Parolda uzunligi kamida 8ta belgi bo'lishi kerak")
        return new_password

    def clean_confirm_new_password(self):
        confirm_new_password = self.cleaned_data.get('confirm_new_password')
        new_password = self.cleaned_data.get('new_password')
        if confirm_new_password != new_password:
            raise ValidationError("Yangi parollar mos kelmadi.")
        return confirm_new_password


class UpdateProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        label="Ism",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'first_name'})
    )
    last_name = forms.CharField(
        max_length=50,
        label="Familiya",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'last_name'})
    )
    email = forms.CharField(
        max_length=100,
        label="Email",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'email'})
    )
    phone = forms.CharField(
        max_length=13,
        label="Telefon raqam",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone'})
    )
    address = forms.CharField(
        max_length=255,
        label="Manzil",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'address'})
    )
    username = forms.CharField(
        label='Username',
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'username'
            }
        )
    )


    class Meta:
        model = User
        fields = ('first_name', 'last_name','email', 'phone', 'username', 'address')

    def clean_phone(self):
        phone_regex = r"^\+998([- ])?(90|91|93|94|95|98|99|33|97|71)([- ])?(\d{3})([- ])?(\d{2})([- ])?(\d{2})$"
        phone = self.cleaned_data['phone']
        if not re.fullmatch(phone_regex, phone) and phone:
            raise ValidationError("Telefon raqami talabga mos emas!")
        if User.objects.filter(phone=self.cleaned_data['phone']).exclude(id=self.instance.id).exists():
            raise ValidationError("Bu telefon raqami band!")
        return phone

    def clean_email(self):
        email = self.cleaned_data['email']
        allowed_domains = ['gmail.com', 'mail.ru', 'yandex.ru']
        domain = email.split('@')[-1]
        if domain not in allowed_domains and email:
            raise ValidationError(f"Email quyidagi formatlarda bo'lishi mumkin: {', '.join(allowed_domains)}")
        if User.objects.filter(email=self.cleaned_data['email']).exclude(id=self.instance.id).exists():
            raise ValidationError("Bu email band!")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if len(first_name) < 4 and first_name:
            raise ValidationError("Ismning uzunligi kamida 4 ta belgi bo'lishi kerak!")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if len(last_name) < 4 and last_name:
            raise ValidationError("Familiyaning uzunligi kamida 4 ta belgi bo'lishi kerak!")
        return last_name

    def clean_address(self):
        address = self.cleaned_data['address']
        if len(address) < 10 and address:
            raise ValidationError("Kamida 10 ta belgi")
        return address

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username[0].isalpha():
            raise forms.ValidationError('Username birinchi belgisi harf bo\'lishi kerak')
        if not re.match(r'^[A-Za-z][A-Za-z0-9_]*$', username):
            raise forms.ValidationError('Username faqat harflar, raqamlar va _ belgisidan iborat bo\'lishi mumkin')
        if len(username) < 5:
            raise forms.ValidationError('Kamida 5ta belgi')
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise ValidationError("Bu email band!")
        return username


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(
        label='Email', required=True,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Email',
                'class': 'form-control',
                'id': 'email'
            }
        )
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError("Bunday emailga ega foydalanuvchi topilmadi")
        return email


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        label='Yangi parol',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    confirm_password = forms.CharField(
        label='Parolni tasdiqlang',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Parollar mos kelmadi.")

        return cleaned_data


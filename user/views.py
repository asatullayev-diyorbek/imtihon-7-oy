from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode, urlencode
from django.views.generic import View, FormView
from django.contrib import messages
from .forms import RegisterForm, LoginForm, UpdateProfileForm, PasswordChangeForm, ResetPasswordForm, SetNewPasswordForm
from .models import User
from django.contrib.auth import update_session_auth_hash



class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile_form = UpdateProfileForm(instance=request.user)
        password_form = PasswordChangeForm()
        context = {
            'profile_form': profile_form,
            'password_form': password_form,
            'title': 'Profilim',
            'page_name': 'Profile',
        }
        return render(request, 'user/profile.html', context)

    def post(self, request):
        return redirect('user:profile')


class UpdateProfileImageView(LoginRequiredMixin, View):
    def post(self, request):
        if 'image' in request.FILES:
            image = request.FILES['image']
            if image.name.endswith(('.jpg', '.jpeg', '.png')):
                user = request.user
                user.image = image
                user.save()
                messages.success(request, 'Profil rasmi o\'zgartirildi!')
            else:
                messages.error(request, 'Noto\'g\'ri fayl formati. JPG, JPEG yoki PNG formatidagi rasmni tanlang.')
                return redirect('user:profile')
        messages.error(request, 'Rasmni yuklashda xato!')
        return redirect('user:profile')


class PasswordChangeView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'title': 'Parolni yangilash',
            'password_form': PasswordChangeForm(),
        }
        return render(request, 'user/password_change.html', context)
    def post(self, request):
        user = get_object_or_404(User, id=request.user.id)
        password_form = PasswordChangeForm(request.POST)
        password_form.set_user(self.request.user)

        if password_form.is_valid():
            new_password = password_form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Parolingiz yangilandi!")
            return redirect('user:profile')

        context = {
            'title': 'Parolni yangilash - Student Office',
            'password_form': password_form,
            'profile_form': UpdateProfileForm(),
        }
        return render(request, 'user/password_change.html', context)


class UpdateProfileView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'profile_form': UpdateProfileForm(instance=request.user),
            'title': "Ma'lumotlarni tahrirlash",
        }
        return render(request, 'user/personal_information.html', context)

    def post(self, request):
        profile_form = UpdateProfileForm(self.request.POST, instance=request.user)

        if profile_form.is_valid():
            email = profile_form.cleaned_data['email']
            phone = profile_form.cleaned_data['phone']

            if email:
                request.user.email = email
            if phone:
                request.user.phone = phone
            request.user.first_name = profile_form.cleaned_data['first_name']
            request.user.last_name = profile_form.cleaned_data['last_name']
            request.user.address = profile_form.cleaned_data['address']
            request.user.save()
            messages.success(request, "Ma'lumotlar muvafaqqiyatli yangilandi!")
            return redirect('user:profile')

        context = {
            'profile_form': profile_form,
            'title': 'Profilim',
            'page_name': 'Profile',
        }
        return render(request, 'user/personal_information.html', context)


class ResetPasswordView(View):
    def get(self, request):
        context = {
            'title': "Parolni unutdim",
            'reset_form': ResetPasswordForm(),
        }
        return render(request, 'user/password_reset.html', context)

    def post(self, request):
        reset_form = ResetPasswordForm(request.POST)
        if reset_form.is_valid():
            email = reset_form.cleaned_data['email']
            user = User.objects.get(email=email)
            token_generator = PasswordResetTokenGenerator()

            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_link = reverse_lazy('user:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_url = self.request.build_absolute_uri(reset_link)

            email_subject = 'Parolingizni qayta tiklash'
            email_body = "Sizning emailingizga parolni qayta tiklash uchun so'rovingiz asosida link yuborildi."\
                f"Link: {reset_url} "\
                "Ushbu link orqali parolingizni almashtirishingiz mumkin"

            send_mail(
                email_subject, email_body,
                None, [user.email],
                fail_silently=False,
            )
            messages.success(request, "Sizning emailingizga parol almashtirish uchun link va qo'llanma yuborildi.")
            return redirect('book:home')


        context = {
            'title': "Parolni unutdim",
            'reset_form': reset_form,
        }
        return render(request, 'user/password_reset.html', context)


class PasswordResetConfirmView(FormView):
    template_name = 'user/password_reset_confirm.html'
    form_class = SetNewPasswordForm
    success_url = reverse_lazy('user:login')

    def dispatch(self, request, *args, **kwargs):
        self.uidb64 = kwargs['uidb64']
        self.token = kwargs['token']
        self.user = self.get_user()

        token_generator = PasswordResetTokenGenerator()
        if self.user is not None and token_generator.check_token(self.user, self.token):
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, "Bu link yaroqli emas!")
            return redirect('user:password_reset')

    def get_user(self):
        try:
            uid = urlsafe_base64_decode(self.uidb64).decode()
            return User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

    def form_valid(self, form):
        new_password = form.cleaned_data['new_password']
        self.user.set_password(new_password)
        self.user.save()

        update_session_auth_hash(self.request, self.user)
        messages.success(self.request, "Parolingiz muvafaqqiyatli o'zgartirildi!")

        return super().form_valid(form)


class Register(View):
    def get(self, request):
        context = {
            'form': RegisterForm(),
            'title': "Ro'yxatdan o'tish",
        }
        return render(request, 'user/register.html', context)

    def post(self, request):
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.create_user()
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Ro\'yxatdan o\'tishni tasdiqlash'
            message = render_to_string('user/email_verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            email = EmailMessage(
                subject,
                message,
                'asatullayevblog@gmail.com',
                [user.email],
            )
            email.content_subtype = "html"
            email.send(fail_silently=True)

            messages.success(request, "Ro'yxatdan o'tdingiz! Tasdiqlash uchun emailingizni tekshiring.")
            return redirect('user:login')

        context = {
            'form': form,
            'title': "Ro'yxatdan o'tish",
        }
        return render(request, 'user/register.html', context)


class ActivateAccount(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            subject = 'Ro\'yxatdan o\'tishingiz muvaffaqiyatli tasdiqlandi!'
            message = render_to_string('user/verification_succes.html', {
                'full_name': user.get_full_name()
            })

            email = EmailMessage(
                subject,
                message,
                'asatullayevblog@gmail.com',
                [user.email],
            )
            email.content_subtype = "html"
            email.send(fail_silently=True)
            messages.success(request, "Sizning hisobingiz muvaffaqiyatli tasdiqlandi!")
            return redirect('user:login')
        else:
            messages.error(request, "Tasdiqlash havolasi yaroqsiz yoki muddati o'tgan.")
            return redirect('user:register')


class ResendActivationEmail(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('book:home')
        context = {
            'title': "Profilni tasdiqlash"
        }
        return render(request, 'user/resend_activate.html', context)

    def post(self, request):
        email = request.POST.get('email')  # Foydalanuvchi emailini olish
        try:
            user = User.objects.get(email=email)
            if not user.is_active:  # Agar foydalanuvchi hali tasdiqlanmagan bo'lsa
                current_site = get_current_site(request)
                subject = 'Ro\'yxatdan o\'tishni tasdiqlash'
                message = render_to_string('user/email_verification.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })

                email = EmailMessage(
                    subject,
                    message,
                    'asatullayevblog@gmail.com',
                    [user.email],
                )
                email.content_subtype = "html"
                email.send(fail_silently=True)
                messages.success(request, "Tasdiqlash uchun emailingizni tekshiring.")
            else:
                messages.info(request, "Hisobingiz allaqachon tasdiqlangan.")
            return redirect('user:login')
        except User.DoesNotExist:
            messages.error(request, "Bunday emailga ega foydalanuvchi topilmadi.")
        return redirect('user:resend_activation_email')


class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('book:home')

        context = {
            'form': LoginForm(),
            'title': 'Kirish'
        }
        return render(request, 'user/login.html', context)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('book:home')
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, f"Salom {user.username} siz tizimga kirdingiz!")
            to = request.GET.get('next', request.META.get('HTTP_REFERER', 'book:main'))
            return redirect(to)
        else:
            context = {
                'form': form,
                'title': 'Kirish',
            }
            return render(request, 'user/login.html', context)


@login_required
def logout_user(request):
    logout(request)
    messages.warning(request, 'Siz tizimdan chiqdingiz!')
    return redirect('user:login')
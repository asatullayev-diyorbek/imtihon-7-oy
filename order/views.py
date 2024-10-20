from django.shortcuts import redirect, get_object_or_404, render
from django.views import View
from .models import Order, OrderItem, Book

class CheckoutView(View):
    def get(self, request):
        # Agar savat bo'sh bo'lsa yoki foydalanuvchi tizimga kirmagan bo'lsa, kerakli yo'naltirishni amalga oshiramiz
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('cart_detail')
        if not request.user.is_authenticated:
            return redirect('login')  # Foydalanuvchini tizimga kiritish uchun login sahifasiga yo'naltirish

        context = {
            'cart': cart,
        }
        return render(request, 'checkout/checkout.html', context)

    def post(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('cart_detail')  # Agar savat bo'sh bo'lsa, qaytarish

        order = Order.objects.create(
            user=request.user,  # Agar foydalanuvchi tizimga kirmagan bo'lsa, login talab qilinadi
            total_price=0,  # Bu qiymatni keyinchalik yangilaymiz
            status='Pending'
        )

        total_price = 0

        # Savatdagi kitoblarni buyurtma elementlariga aylantirish
        for book_id, quantity in cart.items():
            book = get_object_or_404(Book, id=book_id)  # Kitob mavjudligini tekshirish
            OrderItem.objects.create(
                order=order,
                book=book,
                quantity=quantity,
                price=book.price
            )
            total_price += book.price * quantity

        # Buyurtmaning umumiy narxini yangilash
        order.total_price = total_price
        order.save()

        # Checkoutdan keyin savatni bo'shatish
        request.session['cart'] = {}

        # Buyurtma tafsilotlariga o'tkazish
        return redirect('order_detail', order_id=order.id)

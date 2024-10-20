from django.shortcuts import render, redirect
from django.views.generic import View
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages

from .forms import CommentForm, BookForm
from .models import Category, Book, Comment


class HomeView(View):
    def get(self, request):
        books = Book.objects.all()
        featured_books = Book.objects.filter(is_featured=True)[:8]
        popular = Book.objects.annotate(avg_rating=models.Avg('comment__rating')) \
                              .order_by('-avg_rating')[:8]
        new_books = books.order_by('-created_at')[:8]

        context = {
            'title': 'Bosh sahifa',
            'page_name': 'Home',
            'books': books,
            'featured_books': featured_books,
            'popular_books': popular,
            'new_books': new_books,
        }
        return render(request, 'bookshop/index.html', context)


class BookListView(View):
    def get(self, request):
        category_slug = request.GET.get('category', None)
        if category_slug:
            selected_category = Category.objects.filter(slug=category_slug).first()
            if not selected_category:
                return redirect('book:book_list')
            books = Book.objects.filter(category=selected_category)
        else:
            selected_category = None
            books = Book.objects.all()
        context = {
            'title': 'Barcha kitoblar' if selected_category is None else selected_category.name,
            'page_name': 'Book List',
            'books': books,
            'selected_category': "Barchasi" if selected_category is None else selected_category,
        }
        return render(request, 'bookshop/book_list.html', context)


class BookDetailView(View):
    def get(self, request, slug):
        comment_form = CommentForm()
        book = Book.objects.filter(slug=slug).first()
        cart = request.session.get('cart')
        if cart:
            book_cart_quantity = cart.get(str(book.pk), 0)
        else:
            book_cart_quantity = 0
        if not book:
            return redirect('book:book_list')
        context = {
            'title': book.title,
            'page_name': 'Book Detail',
            'book': book,
            'comment_form': comment_form,
            'book_cart_quantity': book_cart_quantity,
        }
        return render(request, 'bookshop/book_detail.html', context)


class BookCreateView(View):
    def get(self, request):
        form = BookForm()
        return render(request, 'bookshop/book_form.html', {'form': form})

    def post(self, request):
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Kitob muvaffaqiyatli qo'shildi!")
            return redirect('book:book_list')
        return render(request, 'bookshop/book_form.html', {'form': form, 'title': 'QO\'shish'})



class BookUpdateView(View):
    def get(self, request, slug):
        book = Book.objects.get(slug=slug)
        form = BookForm(instance=book)
        return render(request, 'bookshop/book_form.html', {'form': form, 'title': 'Yangilash'})

    def post(self, request, slug):
        book = Book.objects.get(slug=slug)
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Kitob muvaffaqiyatli tahrirlandi!")
            return redirect('book:book_detail', slug=book.slug)
        return render(request, 'bookshop/book_form.html', {'form': form})


class BookDeleteView(View):
    def get(self, request, slug):
        book = Book.objects.get(slug=slug)
        book.delete()
        messages.success(request, "Kitob muvaffaqiyatli o'chirildi!")
        return redirect('book:book_list')


class CommentView(LoginRequiredMixin, View):
    def post(self, request, slug):
        book = Book.objects.get(slug=slug)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            Comment.objects.create(
                content=comment_form.cleaned_data['content'],
                rating=comment_form.cleaned_data['rating'],
                user=request.user,
                book=book,
            )
        return redirect('book:book_detail', slug=slug)


class AboutView(View):
    def get(self, request):
        context = {
            'title': 'Haqida',
            'page_name': 'About',
        }
        return render(request, 'bookshop/about.html', context)


class ContactView(View):
    def get(self, request):
        context = {
            'title': 'Bog\'lanish',
            'page_name': 'Contact',
        }
        return render(request, 'bookshop/contact.html', context)


class CartListView(View):
    def get(self, request):
        cart = request.session.get('cart', {})
        books = Book.objects.filter(id__in=cart.keys())
        full_price = 0
        for book in books:
            book.cart_quantity = cart[str(book.id)]
            book.total_price = float(book.current_price()) * cart[str(book.id)]
            full_price += book.total_price
        context = {
            'title': 'Savat',
            'books': books,
            'full_price': full_price,
        }
        return render(request,'bookshop/cart_list.html', context)


class CartAddView(View):
    def get(self, request, pk):
        cart = request.session.get('cart', {})
        p_id = str(pk)

        if cart.get(p_id):
            cart[p_id] += 1
            message = "Cart yangilandi"
        else:
            cart[p_id] = 1
            message = "Cartga qo'shildi"

        request.session['cart'] = cart
        return JsonResponse({'status': 'success', 'cart': cart, 'message': message})


class CartRemoveView(View):
    def get(self, request, pk):
        cart = request.session.get('cart', {})
        p_id = str(pk)
        p = cart.get(p_id)
        if p:
            if p > 1:
                cart[p_id] -= 1
                message = "Cart yangilandi"
            elif p == 1:
                del cart[p_id]
                message = "Cartdan o'chirildi"
            else:
                message = "Mavjud emas"
        else:
            message = "Cartda mavjud emas"
        request.session['cart'] = cart
        return JsonResponse({'status': 'success', 'cart': cart, 'message': message})


class CartDeleteView(View):
    def get(self, request, pk):
        cart = request.session.get('cart', {})
        p_id = str(pk)
        if p_id in cart:
            del cart[p_id]
        request.session['cart'] = cart
        return redirect('book:cart_list')

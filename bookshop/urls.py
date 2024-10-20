from django.urls import path
from . import views

app_name = 'book'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('book/list/', views.BookListView.as_view(), name='book_list'),
    path('book/<slug:slug>/detail/', views.BookDetailView.as_view(), name='book_detail'),

    path('book/create/', views.BookCreateView.as_view(), name='book_create'),
    path('book/<slug:slug>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('book/<slug:slug>/delete/', views.BookDeleteView.as_view(), name='book_delete'),

    path('cart/', views.CartListView.as_view(), name='cart_list'),
    path('cart/<int:pk>/add/', views.CartAddView.as_view(), name='cart_add'),
    path('cart/<int:pk>/remove/', views.CartRemoveView.as_view(), name='cart_remove'),
    path('cart/<int:pk>/delete/', views.CartDeleteView.as_view(), name='cart_delete'),

    path('product/<slug:slug>/comment/', views.CommentView.as_view(), name='comment'),


    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]
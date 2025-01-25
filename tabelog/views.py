from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from .models import CustomUser, Shop, Review, Category, Booking
from django.urls import reverse_lazy, reverse
from .form import UserForm, ReviewForm, BookingForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import requests
import stripe
from myproject import settings
from django.db.models import Q


@login_required
def fav_shop(request, pk):
    shop = get_object_or_404(Shop, pk=pk)
    if request.method == 'POST':
        if request.user.is_authenticated:
            if shop in request.user.favorite_shop.all():
                # If already in favorites, remove it
                request.user.favorite_shop.remove(shop)
            else:
                # If not in favorites, add it
                request.user.favorite_shop.add(shop)
            return redirect('shop-detail', pk=pk)
    return HttpResponseForbidden()

class UserDetailView(UserPassesTestMixin, DetailView):
    def test_func(self):
        user = CustomUser.objects.get(id=self.kwargs['pk'])
        return self.request.user.is_authenticated and user.id == self.request.user.id

    def handle_no_permission(self):
        return redirect('top')

    raise_exception = False
    login_url = reverse_lazy('top')

    model = CustomUser
    template_name = 'user_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.get_object()
        ctx['reviews'] = Review.objects.filter(user=user)
        ctx['fav_shops'] = user.favorite_shop.all()  # Add this line to include favorite shops
        return ctx


class UserUpdateView(View):
    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(id=request.user.id)
        form = UserForm(
            None,
            initial={
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        )
        return render(request, 'user_update.html', {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = UserForm(request.POST or None)
        if form.is_valid():
            user = CustomUser.objects.get(id=request.user.id)
            user.last_name = form.cleaned_data['last_name']
            user.first_name = form.cleaned_data['first_name']
            user.save()
            return redirect('top')
        return render(request, 'user_update.html', {'form': form})


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreditRegisterView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and not self.request.user.is_paid

    def handle_no_permission(self):
        return redirect('top')

    raise_exception = False
    login_url = reverse_lazy('top')

    def get(self, request):
        ctx = {
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        }
        return render(request, 'credit_register.html', ctx)

    def post(self, request):
        email = self.request.user.email
        customer = stripe.Customer.create(
            name=email,
            email=email,
        )

        card = stripe.Customer.create_source(
            customer.id,
            source=request.POST['stripeToken'],
        )

        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': settings.STRIPE_PRICE_ID}],
        )

        custom_user = CustomUser.objects.get(email=email)
        custom_user.stripe_customer_id = customer.id
        custom_user.stripe_card_id = card.id
        custom_user.stripe_subscription_id = subscription.id
        custom_user.is_paid = True
        custom_user.save()

        return redirect('top')
    

class CreditDeleteView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_paid

    def handle_no_permission(self):
        return redirect('top')

    raise_exception = False
    login_url = reverse_lazy('top')

    def get(self, request):
        return render(request, 'credit_delete.html')

    def post(self, request):
        custom_user = CustomUser.objects.get(email=request.user.email)
        stripe.Subscription.delete(custom_user.stripe_subscription_id)
        stripe.Customer.delete(custom_user.stripe_customer_id)

        custom_user.stripe_customer_id = None
        custom_user.stripe_card_id = None
        custom_user.stripe_subscription_id = None
        custom_user.is_paid = False
        custom_user.save()

        return redirect('top')


class CreditUpdateView(UserPassesTestMixin, View):
    # ユーザー認証済み・有料会員の場合
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_paid

    # トップへ戻る
    def handle_no_permission(self):
        return redirect('top')

    raise_exception = False
    login_url = reverse_lazy('top')

    # 画面表示したときに動く（Viewの中の関数）
    def get(self, request):
        email = self.request.user.email
        custom_user = CustomUser.objects.get(email=email)
        url = f'https://api.stripe.com/v1/customers/{custom_user.stripe_customer_id}/cards/{custom_user.stripe_card_id}'
        response = requests.get(url, auth=(settings.STRIPE_SECRET_KEY, ''))

        stripe_customer_json = response.json()

        ctx = {
            'card_brand': stripe_customer_json['brand'],
            'card_last4': stripe_customer_json['last4'],
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        }
        return render(request, 'credit_update.html', ctx)

    def post(self, request):
        email = self.request.user.email
        custom_user = CustomUser.objects.get(email=email)

        card = stripe.Customer.create_source(
            custom_user.stripe_customer_id,
            source=request.POST['stripeToken'],
        )

        stripe.Customer.delete_source(
            custom_user.stripe_customer_id,
            custom_user.stripe_card_id,
        )

        custom_user.stripe_card_id = card.id
        custom_user.save()

        return redirect('top')


class ShopListView(ListView):
    model = Shop
    template_name = 'shop_list.html'

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        query = self.request.GET.get('query')
        category = self.request.GET.get('category')

        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(category__name__icontains=query))

        if category:
            queryset = queryset.filter(category__id=category)
        return queryset
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categorys'] = Category.objects.all()
        return ctx


class ShopDetailView(DetailView):
    model = Shop
    template_name = 'shop_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 該当ショップのレビューを取得
        context['reviews'] = Review.objects.filter(shop=self.get_object())
        return context


class ReviewCreateView(UserPassesTestMixin, CreateView):
    model = Review
    template_name = 'review_create.html'
    form_class = ReviewForm

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_paid

    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = get_object_or_404(Shop, pk=self.kwargs['pk'])
        context['shop'] = shop
        return context

    def form_valid(self, form):
        shop = get_object_or_404(Shop, pk=self.kwargs['pk'])
        user = self.request.user
        
        # 既にレビューが存在するか確認
        if Review.objects.filter(shop=shop, user=user).exists():
            # 既にレビューが存在する場合はエラーを返す
            form.add_error(None, '既にこの店舗にレビューを投稿しています。')
            return self.form_invalid(form)
        
        form.instance.shop = shop
        form.instance.user = user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('shop-detail', kwargs={'pk': self.object.shop.pk})

class ReviewEditView(UserPassesTestMixin, UpdateView):
    model = Review
    template_name = 'review_edit.html'
    form_class = ReviewForm

    def test_func(self):
        review = self.get_object()
        return self.request.user.is_authenticated and self.request.user.is_paid and self.request.user == review.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = get_object_or_404(Shop, pk=self.kwargs['shop_pk'])
        context['shop'] = shop
        return context
    
    def get_object(self):
        # Reviewのインスタンスを返すメソッド
        return get_object_or_404(Review, pk=self.kwargs['pk'])

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('shop-detail', kwargs={'pk': self.object.shop.pk})
    

class ReviewDeleteView(UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'review_delete_confirm.html'

    def test_func(self):
        review = self.get_object()
        return self.request.user.is_authenticated and self.request.user.is_paid and self.request.user == review.user

    def get_success_url(self):
        # 削除後にユーザーページに戻る
        return reverse('user', kwargs={'pk': self.request.user.pk})


class BookingCreateView(UserPassesTestMixin, CreateView):
    model = Booking
    template_name = 'booking_create.html'
    form_class = BookingForm

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_paid

    login_url = '/accounts/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        shop = get_object_or_404(Shop, pk=self.kwargs['pk'])
        kwargs['shop'] = shop
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = get_object_or_404(Shop, pk=self.kwargs['pk'])
        context['shop'] = shop
        return context

    def form_valid(self, form):
        shop = get_object_or_404(Shop, pk=self.kwargs['pk'])
        user = self.request.user
        form.instance.shop = shop
        form.instance.user = user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('shop-detail', kwargs={'pk': self.object.shop.pk})
    

class BookingListView(UserPassesTestMixin, ListView):
    model = Booking
    template_name = 'booking_list.html'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_paid

    login_url = '/accounts/login/'

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        pk = self.kwargs['pk']
        queryset = queryset.filter(user__id=pk)
        

        return queryset    


class BookingDeleteView(UserPassesTestMixin, DeleteView):
    model = Booking
    template_name = 'booking_delete_confirm.html'

    def test_func(self):
        booking = self.get_object()
        return self.request.user.is_authenticated and self.request.user.is_paid and self.request.user == booking.user

    def get_success_url(self):
        # 削除後にユーザーページに戻る
        return reverse('user', kwargs={'pk': self.request.user.pk})
    

class BookingEditView(UserPassesTestMixin, UpdateView):
    model = Booking
    template_name = 'booking_edit.html'
    form_class = BookingForm

    def test_func(self):
        booking = self.get_object()
        return self.request.user.is_authenticated and self.request.user.is_paid and self.request.user == booking.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = get_object_or_404(Shop, pk=self.kwargs['shop_pk'])
        context['shop'] = shop
        return context
    
    def get_object(self):
        return get_object_or_404(Booking, pk=self.kwargs['pk'])

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('user', kwargs={'pk': self.object.user.pk})
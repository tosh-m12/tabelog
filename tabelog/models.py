from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(verbose_name='メールアドレス', unique=True)
    last_name = models.CharField(verbose_name='姓', max_length=20)
    first_name = models.CharField(verbose_name='名', max_length=20)
    favorite_shop = models.ManyToManyField('Shop', verbose_name='お気に入り店舗', blank=True)
    is_paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_card_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'


class Category(models.Model):
    name = models.CharField(verbose_name='カテゴリ名', max_length=50)
    created_datetime = models.DateTimeField(verbose_name='登録日時', auto_now_add=True) 
    updated_datetime = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    def __str__(self):
        return self.name


class Shop(models.Model):
    name = models.CharField(verbose_name='店名', max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    image = models.ImageField(verbose_name='店舗画像', blank=True, default='noImage.png')
    description = models.TextField(verbose_name='説明', blank=True, null=True)
    price_min = models.PositiveIntegerField(verbose_name='価格帯（下限値）')
    price_max = models.PositiveIntegerField(verbose_name='価格帯（上限値）')
    opening_time = models.TimeField(verbose_name='営業時間（開店）')
    closing_time = models.TimeField(verbose_name='営業時間（閉店）')
    postal_code = models.CharField(verbose_name='郵便番号', max_length=7)
    address = models.CharField(verbose_name='住所', max_length=100)
    phone = models.CharField(verbose_name='電話番号', max_length=20)
    regular_holiday = models.CharField(verbose_name='定休日', max_length=20)
    created_datetime = models.DateTimeField(verbose_name='登録日時', auto_now_add=True) 
    updated_datetime = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField(verbose_name='レビューコメント', blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('shop', 'user')

class Booking(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    booking_date = models.DateField(verbose_name='予約日')
    booking_time = models.TimeField(verbose_name='予約時間')
    head_count = models.IntegerField(verbose_name='予約人数')

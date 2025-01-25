from django import forms
from django.forms import ModelForm, DateInput, TimeInput
from .models import CustomUser, Review, Booking
from datetime import timedelta, time, date, datetime
from django.utils import timezone


class UserForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['comment']

class BookingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        shop = kwargs.pop('shop', None)
        super().__init__(*args, **kwargs)
        
        if shop:
            # 現在日付を取得
            today = date.today()

            # フォームで使うデータ取得
            opening_time = shop.opening_time
            closing_time = shop.closing_time

            # フォームの予約日から予約時間選択肢を取得
            self.fields['booking_time'].choices = self.get_valid_time_choices(opening_time, closing_time, today)

    def get_valid_time_choices(self, opening_time, closing_time, booking_date):
        now = timezone.localtime()
        valid_times = []
        current_time = datetime.combine(booking_date, opening_time)
        closing_datetime = datetime.combine(booking_date, closing_time)

        while current_time < closing_datetime:
            valid_times.append((current_time.time(), current_time.strftime('%H:%M')))
            current_time += timedelta(minutes=30)

        return valid_times

    booking_date = forms.DateField(widget=DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}), label='予約日')
    booking_time = forms.ChoiceField(widget=forms.Select(attrs={'class': 'time-selector'}), label='予約時間')

    HEAD_COUNT_CHOICES = [(i, str(i)) for i in range(1, 21)]
    head_count = forms.ChoiceField(choices=HEAD_COUNT_CHOICES, label='予約人数', initial=1)

    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'head_count']
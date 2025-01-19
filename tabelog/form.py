from django import forms
from django.forms import ModelForm, DateInput, TimeInput
from .models import CustomUser, Review, Booking
from datetime import timedelta, time, date
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

    def round_up_to_next_half_hour():
        now = timezone.now()
        minutes = now.minute
        if minutes < 30:
            rounded_time = now.replace(minute=30, second=0, microsecond=0)
        else:
            rounded_time = (now + timedelta(hours=1)).replace(minute=30, second=0, microsecond=0)
        return rounded_time.time()
    
    time_choices = [
        (time(hour=h, minute=0), f'{h:02}:00') for h in range(24)
    ] + [
        (time(hour=h, minute=30), f'{h:02}:30') for h in range(24)
    ]

    booking_date = forms.DateField(widget=DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}), label='予約日', initial=date.today)
    booking_time = forms.ChoiceField(choices=time_choices, widget=forms.Select(attrs={'class': 'time-selector'}), label='予約時間', initial=round_up_to_next_half_hour)

    HEAD_COUNT_CHOICES = [(i, str(i)) for i in range(1, 21)]
    
    head_count = forms.ChoiceField(
        choices=HEAD_COUNT_CHOICES,
        label='予約人数',
        initial=1
    )

    # def clean_head_count(self):
    #     head_count = self.cleaned_data.get('head_count')
    #     if head_count < 1:
    #         raise forms.ValidationError('予約人数は１名以上である必要があります。')
    #     return head_count

    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'head_count']
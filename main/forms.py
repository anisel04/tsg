from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Request, Notification, Debt, Message, Payment

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'first_name',
            'surname',
            'apartment_number',
            'phone_number',
        ]
        labels = {
            'username': 'Логин',
            'email': 'Почта',
            'first_name': 'Имя',
            'surname': 'Фамилия',
            'apartment_number': 'Номер квартиры',
            'phone_number': 'Номер телефона',
        }

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'description']

        labels = {
            'title': 'Тема',
            'description': 'Описание',
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'first_name',
            'surname',
            'apartment_number',
            'phone_number',
        ]

        labels = {
            'username': 'Логин',
            'email': 'Почта',
            'password1': 'Пароль',
            'password2': 'Пароль',
            'first_name': 'Имя',
            'surname': 'Фамилия',
            'apartment_number': 'Номер квартиры',
            'phone_number': 'Номер телефона',
                }

class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['user', 'amount', 'due_date', 'description', 'is_paid']

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message', 'is_important']

        labels = {
            'title': 'Тема',
            'message': 'Сообщение',
            'is_important': 'Важное',
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['user', 'amount', 'due_date', 'description', 'is_paid']

        labels = {
            'user': 'Жилец',
            'amount': 'Сумма',
            'due_date': 'Срок',
            'is_paid': 'Оплачено',
            'description': 'Описание',
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['user', 'request', 'text']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control', 'id': 'user-select'}),
            'request': forms.Select(attrs={'class': 'form-control', 'id': 'request-select'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

        labels = {
            'user': 'Жилец',
            'request': 'Заявка',
            'text': 'Сообщение',
        }
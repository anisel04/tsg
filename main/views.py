from .forms import CustomUserCreationForm, RequestForm, DebtForm, PaymentForm, NotificationForm, UserProfileEditForm, PasswordChangeForm, MessageForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Request, Notification, Debt, Payment, Message, CustomUser
from django.utils.timezone import datetime
from django.utils.timezone import now
import io
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from .utils import update_debts
from django.http import JsonResponse
import base64
from django.http import HttpResponseBadRequest
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def debts_report(request):
    payments = Payment.objects.all()
    users = CustomUser.objects.all()
    if not payments.exists():
        return render(request, 'main/error.html', {'message': 'Нет данных для отчёта о задолжнотях.'})
    debts = payments.filter(due_date__lt=now(), is_paid=False)  # Платежи с истёкшим сроком
    not_debts = payments.filter(due_date__gte=now(), is_paid=False)
    debts_count = debts.count()
    not_debts_c = not_debts.count()

    total_payments = debts_count + not_debts_c
    if total_payments == 0:
        return render(request, 'main/error.html', {'message': 'Нет данных для построения графика.'})

    labels = ['Просроченные', 'Ожидаемые']
    sizes = [debts_count, not_debts_c]
    colors = ['#FF5722', '#4CAF50']
    explode = (0.1, 0)

    # Построение графика
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Отчёт о задолженностях')
    plt.axis('equal')

    # Сохранение графика в формате base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    plt.close('all')

    # Передача данных в шаблон
    context = {
        'chart': image_base64,
        'debts_count': debts_count,
        'not_debts_c': not_debts_c,
        'users' : users
    }
    return render(request, 'main/debts_report.html', context)

def payment_report(request):
    payments = Payment.objects.all()

    if not payments.exists():
        return render(request, 'main/error.html', {'message': 'Нет данных для отчёта о платежах.'})

    paid = payments.filter(is_paid=True).count()
    unpaid = payments.filter(is_paid=False).count()

    labels = ['Оплачено', 'Не оплачено']
    sizes = [paid, unpaid]
    colors = ['#4CAF50', '#F44336']
    explode = (0.1, 0)  # Выделяем сегмент "Оплачено"

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Статистика платежей')
    plt.axis('equal')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    plt.close('all')

    context = {
        'chart': image_base64,
        'paid_count': paid,
        'unpaid_count': unpaid,
        'paid': paid,
        'unpaid': unpaid
    }
    return render(request, 'main/payment_report.html', context)

def request_report(request):
    # Данные для графика
    new_requests = Request.objects.filter(status='new').count()
    in_progress_requests = Request.objects.filter(status='in_progress').count()
    completed_requests = Request.objects.filter(status='completed').count()

    total_requests = new_requests + in_progress_requests + completed_requests

    if total_requests == 0:
        return render(request, 'main/error.html', {'message': 'Нет данных для отчёта о заявках.'})

    # Построение графика
    labels = ['Новые', 'В процессе', 'Завершённые']
    sizes = [new_requests, in_progress_requests, completed_requests]
    colors = ['#2196F3', '#FFC107', '#4CAF50']
    explode = (0.1, 0, 0)  # Выделяем сегмент "Новые"

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Статистика заявок')
    plt.axis('equal')

    # Сохранение графика в формате base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Закрытие всех графиков
    plt.close('all')

    # Передача данных в шаблон
    context = {
        'chart': image_base64,
        'new_requests': new_requests,
        'in_progress_requests': in_progress_requests,
        'completed_requests': completed_requests,
    }
    return render(request, 'main/request_report.html', context)

def get_user_requests(request, user_id):
    requests = Request.objects.filter(user_id=user_id).values('id', 'description')
    return JsonResponse({'requests': list(requests)})

def manage_payments(request):
    if not request.user.is_superuser:  # Если пользователь не администратор
        return redirect('home')

    payments = Payment.objects.all().order_by('-created_at')  # Все платежи

    if request.method == "POST":
        payment_id = request.POST.get('payment_id')
        is_paid = request.POST.get('is_paid') == 'on'

        # Получаем объект платежа
        payment = get_object_or_404(Payment, id=payment_id)

        # Обновляем статус
        payment.is_paid = is_paid

        # Если был загружен файл чека, сохраняем его
        if 'receipt' in request.FILES:
            payment.receipt = request.FILES['receipt']

        payment.save()

        return redirect('manage_payments')

    return render(request, 'main/manage_payments.html', {'payments': payments})

def notifications(request):
    notifications = Notification.objects.all().order_by('-created_at')

    # Получаем параметры фильтрации из GET-запроса
    importance_filter = request.GET.get('importance')
    date_n_filter = request.GET.get('date_n')

    # Фильтрация по важности
    if importance_filter == 'important':
        notifications = notifications.filter(is_important=True)
    elif importance_filter == 'not_important':
        notifications = notifications.filter(is_important=False)

    if date_n_filter == 'new':
        notifications = notifications.order_by('-created_at')
    elif date_n_filter == 'old':
        notifications = notifications.order_by('created_at')

    return render(request, 'main/notifications.html', {'notifications': notifications})

def manage_debts(request):
    if not request.user.is_staff:  # Только для администратора
        return redirect('home')

    # Фильтрация
    debts = Debt.objects.all()
    user_filter = request.GET.get('user')
    status_filter = request.GET.get('status')

    if user_filter:
        debts = debts.filter(user_id=user_filter)
    if status_filter == 'paid':
        debts = debts.filter(is_paid=True)
    elif status_filter == 'unpaid':
        debts = debts.filter(is_paid=False)

    # Список пользователей для фильтрации
    users = CustomUser.objects.all()

    # Форма для добавления/изменения задолженности
    if request.method == 'POST':
        form = DebtForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_debts')
    else:
        form = DebtForm()

    return render(request, 'main/manage_debts.html', {'form': form, 'debts': debts, 'users': users})

def my_debts(request):
    update_debts()  # Обновляем задолженности
    debts = Debt.objects.filter(user=request.user, is_paid=False).order_by('-due_date')
    return render(request, 'main/my_debts.html', {'debts': debts})

def user_payments(request):
    payments = Payment.objects.filter(user=request.user).order_by('-due_date')
    return render(request, 'main/payments.html', {
        'payments': payments,
        'now': timezone.now(),
    })

def send_notification(request):
    if not request.user.is_superuser:  # Только для администратора
        return redirect('home')

    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('notifications')
    else:
        form = NotificationForm()
    return render(request, 'main/send_notification.html', {'form': form})

def all_requests(request):
    if request.method == "POST":
        request_id = request.POST.get("request_id")

        if "delete_request" in request.POST:
            # Обработка удаления заявки
            try:
                req = get_object_or_404(Request, id=request_id)
                req.delete()
                messages.success(request, "Заявка успешно удалена.")
            except Request.DoesNotExist:
                return HttpResponseBadRequest("Заявка не найдена")
        else:
            # Обработка изменения статуса заявки
            new_status = request.POST.get("new_status")
            try:
                req = get_object_or_404(Request, id=request_id)
                if new_status in dict(Request.STATUS_CHOICES).keys():
                    req.status = new_status
                    req.save()
                    messages.success(request, "Статус заявки обновлён.")
                else:
                    return HttpResponseBadRequest("Недопустимый статус")
            except Request.DoesNotExist:
                return HttpResponseBadRequest("Заявка не найдена")

        return redirect("all_requests")

    # Отображение списка заявок
    requests = Request.objects.all().order_by("-created_at")
    return render(request, "main/all_requests.html", {"requests": requests})

def my_payments(request):
    payments = Payment.objects.filter(user=request.user)
    return render(request, 'main/payments.html', {'payments': payments})

def add_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_payment')
    else:
        form = PaymentForm()
    return render(request, 'main/add_payment.html', {'form': form})

def send_message(request):
    if not request.user.is_superuser:  # Только для администратора
        return redirect('home')
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('send_message')  # После отправки обновляем страницу
    else:
        form = MessageForm()

    requests = Request.objects.all()
    return render(request, 'main/send_message.html', {'form': form, 'requests': requests})

def my_messages(request):
    messages = Message.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/my_messages.html', {'messages': messages})

def my_requests(request):
    requests = Request.objects.filter(user=request.user)
    return render(request, 'main/my_requests.html', {'requests': requests})

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # перенаправление после успешного входа
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'main/login.html')

def edit_profile(request):
    user = request.user
    password_form = None
    profile_form = None

    if request.method == 'POST':
        if 'edit_profile' in request.POST:
            profile_form = UserProfileEditForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Профиль успешно обновлен!')
                return redirect('profile')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.POST)
            if password_form.is_valid():
                old_password = password_form.cleaned_data['old_password']
                new_password1 = password_form.cleaned_data['new_password1']
                new_password2 = password_form.cleaned_data['new_password2']

                if user.check_password(old_password):
                    if new_password1 == new_password2:
                        user.set_password(new_password1)
                        user.save()
                        update_session_auth_hash(request, user)  # Чтобы пользователь не разлогинился
                        messages.success(request, 'Пароль успешно изменен!')
                        return redirect('profile')
                    else:
                        messages.error(request, 'Новые пароли не совпадают.')
                else:
                    messages.error(request, 'Неверный старый пароль.')
    else:
        profile_form = UserProfileEditForm(instance=user)
        password_form = PasswordChangeForm()

    return render(request, 'main/edit_profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # предполагаем, что будет страница входа
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form})

def home(request):
    # Получаем последние 3 уведомления (важные идут первыми)
    notifications = Notification.objects.order_by('-is_important', '-created_at')[:3]

    context = {
        'notifications': notifications,
    }
    return render(request, 'main/home.html', context)

def user_logout(request):
    logout(request)
    return redirect('home')

def profile(request):

    requests_count = Request.objects.filter(user=request.user).count()
    payments_count = Payment.objects.filter(user=request.user).count()
    debts_count = Debt.objects.filter(user=request.user, is_paid=False).count()
    responses_count = Message.objects.filter(user=request.user).count()
    context = {
        'profile': profile,
        'requests_count': requests_count,
        'payments_count': payments_count,
        'debts_count': debts_count,
        'responses_count': responses_count,
    }
    return render(request, 'main/profile.html', context)

def create_request(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.user = request.user
            new_request.save()
            return redirect('my_requests')
    else:
        form = RequestForm()
    return render(request, 'main/create_request.html', {'form': form})
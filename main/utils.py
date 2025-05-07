from datetime import date
from .models import Payment, Debt

def update_debts():
    overdue_payments = Payment.objects.filter(is_paid=False, due_date__lt=date.today())
    for payment in overdue_payments:
        # Если задолженность уже существует, пропускаем
        if not hasattr(payment, 'debt'):
            Debt.objects.create(
                user=payment.user,
                payment=payment,
                amount=payment.amount,
                due_date=payment.due_date,
                description=f"Задолженность по платежу ID {payment.id}"
            )




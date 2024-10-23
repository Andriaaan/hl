from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import update_last_login
from .models import User, Transfer, Paymethod
import json

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        firstname = data.get('firstname')
        lastname = data.get('lastname')

        if not email or not password or not username:
            return JsonResponse({'error': 'Required fields are missing'}, status=400)

        user = User.objects.create_user(email=email, username=username, password=password,
                                        firstname=firstname, lastname=lastname)
        return JsonResponse({'message': 'User registered successfully'}, status=201)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        print(f'E: {email}, P: {password}')

 
        try:
            user = User.objects.get(email=email)  
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

        if user.check_password(password):  # Перевірити правильність пароля
            login(request, user)
            return JsonResponse({'message': 'Logged in successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

@login_required
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'}, status=200)


@login_required
def create_paymethod(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        card_number = data.get('cardNumber')
        balance = data.get('balance')

        if not card_number or not balance:
            return JsonResponse({'error': 'Required fields are missing'}, status=400)

        paymethod = Paymethod.objects.create(
            cardNumber=card_number,
            balance=balance,
            user=request.user
        )
        return JsonResponse({'message': 'Payment method created successfully'}, status=201)

@login_required
def get_paymethods(request):
    paymethods = Paymethod.objects.filter(user=request.user)
    paymethods_data = [{'cardNumber': pm.cardNumber, 'balance': str(pm.balance)} for pm in paymethods]
    return JsonResponse({'paymethods': paymethods_data}, status=200)

@login_required
def transfer_funds(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        source_card = data.get('sourceCard')
        destination_card = data.get('destinationCard')
        amount = data.get('amount')

        try:
            source_paymethod = Paymethod.objects.get(cardNumber=source_card, user=request.user)
            destination_paymethod = Paymethod.objects.get(cardNumber=destination_card)
        except Paymethod.DoesNotExist:
            return JsonResponse({'error': 'Invalid payment method'}, status=400)

        if source_paymethod.balance < float(amount):
            return JsonResponse({'error': 'Insufficient balance'}, status=400)

        # Оновлюємо баланс
        source_paymethod.balance -= float(amount)
        destination_paymethod.balance += float(amount)

        source_paymethod.save()
        destination_paymethod.save()

        # Створюємо запис у таблиці Transfer
        transfer = Transfer.objects.create(
            transferValue=amount,
            source_paymethod=source_paymethod,
            destination_paymethod=destination_paymethod,
            status='approved'
        )
        return JsonResponse({'message': 'Transfer successful'}, status=200)
        
@csrf_exempt
@login_required
def create_paymethod(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        card_number = data.get('cardNumber')
        balance = data.get('balance')  # Ви можете використовувати баланс або іншу властивість

        if not card_number or not balance:
            return JsonResponse({'error': 'Required fields are missing'}, status=400)

        # Створити новий платіжний метод
        paymethod = Paymethod.objects.create(
            cardNumber=card_number,
            balance=balance,
            user=request.user  # Прив'язати карту до користувача
        )
        print(f"Payment method created: {paymethod}")
        return JsonResponse({'message': 'Payment method created successfully'}, status=201)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

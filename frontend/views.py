import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator


API_BASE = 'http://127.0.0.1:8000/api'


def get_token(request):
    """Obtiene el token de sesión del usuario."""
    return request.session.get('token')


def login_view(request):
    """Vista de login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        response = requests.post(
            f'{API_BASE}/auth/login/',
            json={'username': username, 'password': password}
        )
        if response.status_code == 200:
            request.session['token'] = response.json()['token']
            request.session['username'] = username
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'frontend/login.html')


def logout_view(request):
    """Vista de logout."""
    request.session.flush()
    return redirect('login')


def dashboard(request):
    """Vista del dashboard con resumen de estadísticas."""
    token = get_token(request)
    if not token:
        return redirect('login')

    headers = {'Authorization': f'Token {token}'}
    providers = requests.get(f'{API_BASE}/providers/', headers=headers).json()
    transactions = requests.get(
        f'{API_BASE}/transactions/', headers=headers
    ).json()

    stats = {
        'total_providers': len(providers),
        'total_transactions': len(transactions),
        'pending': sum(1 for t in transactions if t['status'] == 'pending'),
        'completed': sum(1 for t in transactions if t['status'] == 'completed'),
        'failed': sum(1 for t in transactions if t['status'] == 'failed'),
    }

    return render(request, 'frontend/dashboard.html', {
        'stats': stats,
        'username': request.session.get('username'),
    })


def providers(request):
    """Vista de gestión de proveedores."""
    token = get_token(request)
    if not token:
        return redirect('login')

    headers = {'Authorization': f'Token {token}'}

    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'api_key': request.POST.get('api_key'),
            'environment': request.POST.get('environment'),
        }
        requests.post(f'{API_BASE}/providers/', json=data, headers=headers)
        return redirect('providers')

    provider_list = requests.get(
        f'{API_BASE}/providers/', headers=headers
    ).json()
    return render(request, 'frontend/providers.html', {
        'providers': provider_list,
        'username': request.session.get('username'),
    })


def transactions(request):
    """Vista de gestión de transacciones con filtros."""
    token = get_token(request)
    if not token:
        return redirect('login')

    headers = {'Authorization': f'Token {token}'}
    provider_list = requests.get(
        f'{API_BASE}/providers/', headers=headers
    ).json()

    if request.method == 'POST':
        data = {
            'provider': request.POST.get('provider'),
            'amount': request.POST.get('amount'),
            'currency': request.POST.get('currency'),
            'status': 'pending',
        }
        requests.post(
            f'{API_BASE}/transactions/', json=data, headers=headers
        )
        return redirect('transactions')

    params = {}
    if request.GET.get('status'):
        params['status'] = request.GET.get('status')
    if request.GET.get('provider'):
        params['provider'] = request.GET.get('provider')

    ordering = request.GET.get('ordering', '-created_at')
    params['ordering'] = ordering

    transaction_list = requests.get(
        f'{API_BASE}/transactions/', headers=headers, params=params
    ).json()

    paginator = Paginator(transaction_list, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'frontend/transactions.html', {
        'transactions': page_obj,
        'page_obj': page_obj,
        'providers': provider_list,
        'username': request.session.get('username'),
        'selected_status': request.GET.get('status', ''),
        'selected_provider': request.GET.get('provider', ''),
        'ordering': ordering,
    })


def update_transaction(request, transaction_id):
    """Actualiza el estado e incidencia de una transacción."""
    token = get_token(request)
    if not token:
        return redirect('login')

    if request.method == 'POST':
        headers = {'Authorization': f'Token {token}'}
        data = {
            'provider': request.POST.get('provider'),
            'amount': request.POST.get('amount'),
            'currency': request.POST.get('currency'),
            'status': request.POST.get('status'),
            'incident_type': request.POST.get('incident_type', ''),
        }
        requests.put(
            f'{API_BASE}/transactions/{transaction_id}/',
            json=data,
            headers=headers
        )
    return redirect('transactions')


def delete_provider(request, provider_id):
    """Elimina un proveedor."""
    token = get_token(request)
    if not token:
        return redirect('login')

    if request.method == 'POST':
        headers = {'Authorization': f'Token {token}'}
        requests.delete(
            f'{API_BASE}/providers/{provider_id}/',
            headers=headers
        )
    return redirect('providers')


def delete_transaction(request, transaction_id):
    """Elimina una transacción."""
    token = get_token(request)
    if not token:
        return redirect('login')

    if request.method == 'POST':
        headers = {'Authorization': f'Token {token}'}
        requests.delete(
            f'{API_BASE}/transactions/{transaction_id}/',
            headers=headers
        )
    return redirect('transactions')

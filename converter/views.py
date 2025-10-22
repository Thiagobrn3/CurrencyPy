# converter/views.py
import requests
from django.shortcuts import render

# (La función get_currencies() se mantiene igual, no la borres)
def get_currencies():
    # ... tu código existente aquí ...
    try:
        url = 'https://api.frankfurter.app/currencies'
        response = requests.get(url)
        data = response.json()
        currencies_list = [{'code': code, 'name': name} for code, name in data.items()]
        return currencies_list
    except Exception:
        return [
            {'code': 'USD', 'name': 'Dólar Americano'},
            {'code': 'EUR', 'name': 'Euro'},
            {'code': 'JPY', 'name': 'Yen Japonés'},
        ]

def home(request):
    currencies = get_currencies()
    context = {'currencies': currencies}

    # ---- NUEVO: OBTENER TABLA DE COTIZACIONES ----
    try:
        # Hacemos una petición para obtener las tasas más recientes con base en USD
        rates_url = 'https://api.frankfurter.app/latest?from=USD'
        rates_response = requests.get(rates_url)
        rates_data = rates_response.json()
        
        # Guardamos el diccionario de tasas en el contexto
        # Le pasamos también el nombre de la moneda base
        context['rates'] = rates_data.get('rates', {})
        context['base_currency'] = rates_data.get('base', 'USD')

    except Exception:
        # Si falla, simplemente no mostraremos la tabla
        context['rates'] = {}
        context['base_currency'] = 'USD'
    # ---------------------------------------------

    if request.method == 'POST':
        # ... (TODA TU LÓGICA POST SE MANTIENE EXACTAMENTE IGUAL) ...
        # No necesitas cambiar nada aquí.
        amount_str = request.POST.get('amount')
        from_currency = request.POST.get('from_currency')
        to_currency = request.POST.get('to_currency')
        context['from_currency'] = from_currency
        context['to_currency'] = to_currency
        if not amount_str:
            context['error'] = 'Por favor, ingresa un monto.'
            return render(request, 'converter/index.html', context)
        try:
            amount = float(amount_str)
            context['original_amount'] = f"{amount:,.2f}"
            if from_currency == to_currency:
                context['converted_amount'] = f"{amount:,.2f}"
                return render(request, 'converter/index.html', context)
            url = f'https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}'
            response = requests.get(url)
            data = response.json()
            if 'rates' not in data:
                context['error'] = data.get('message', 'No se pudo obtener la tasa de cambio.')
            else:
                converted_amount = data['rates'][to_currency]
                context['converted_amount'] = f"{converted_amount:,.2f}"
        except ValueError:
            context['error'] = 'El monto ingresado no es un número válido.'
        except Exception as e:
            context['error'] = f'Ocurrió un error inesperado. Por favor, intenta de nuevo.'


    return render(request, 'converter/index.html', context)
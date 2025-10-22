import requests
from django.shortcuts import render

# --- PEGA TU API KEY AQUÍ ---
API_KEY = '0e4ca44e95444245cdcb3a1c'
# -------------------------

def get_currencies():
    """Obtiene la lista de monedas desde ExchangeRate-API."""
    try:
        url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/codes'
        response = requests.get(url)
        data = response.json()
        
        # La API devuelve una lista de listas, ej: [['USD', 'United States Dollar'], ...]
        supported_codes = data.get('supported_codes', [])
        currencies_list = [{'code': code, 'name': name} for code, name in supported_codes]
        return currencies_list
    except Exception:
        return [{'code': 'USD', 'name': 'Dólar Americano'}, {'code': 'EUR', 'name': 'Euro'}]

def get_exchange_table_data():
    """
    Prepara los datos para la tabla de conversión cruzada usando la API profesional.
    Esta es la versión definitiva y más eficiente.
    """
    try:
        column_codes = ['USD', 'EUR', 'BRL', 'CHF', 'GBP', 'ARS', 'MXN']
        row_codes = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'ARS', 'BRL', 'MXN']

        # Hacemos una única llamada para obtener todas las tasas con base en USD
        url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD'
        response = requests.get(url)
        data = response.json()
        rates_from_usd = data.get('conversion_rates', {})

        if not rates_from_usd: # Si no obtenemos tasas, retornamos vacío
            return None, None

        table_data = []
        for base_code in row_codes:
            row = {'base': base_code, 'rates': []}
            for quote_code in column_codes:
                if base_code in rates_from_usd and quote_code in rates_from_usd:
                    # Fórmula de conversión cruzada: (tasa_usd_a_quote) / (tasa_usd_a_base)
                    cross_rate = rates_from_usd[quote_code] / rates_from_usd[base_code]
                    row['rates'].append(cross_rate)
                else:
                    row['rates'].append(None)
            table_data.append(row)
        
        return table_data, column_codes
    except Exception:
        return None, None

def home(request):
    currencies = get_currencies()
    exchange_table, column_currencies = get_exchange_table_data()
    
    context = {
        'currencies': currencies,
        'exchange_table': exchange_table,
        'column_currencies': column_currencies
    }

    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        from_currency = request.POST.get('from_currency')
        to_currency = request.POST.get('to_currency')

        context.update({'from_currency': from_currency, 'to_currency': to_currency})

        if not amount_str:
            context['error'] = 'Por favor, ingresa un monto.'
            return render(request, 'converter/index.html', context)
        
        try:
            amount = float(amount_str)
            context['original_amount'] = f"{amount:,.2f}"

            if from_currency == to_currency:
                context['converted_amount'] = f"{amount:,.2f}"
                return render(request, 'converter/index.html', context)
            
            # La URL de conversión de esta API es un poco diferente
            url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}/{amount}'
            response = requests.get(url)
            data = response.json()

            if data.get('result') == 'success':
                converted_amount = data.get('conversion_result')
                context['converted_amount'] = f"{converted_amount:,.2f}"
            else:
                context['error'] = data.get('error-type', 'No se pudo realizar la conversión.')

        except ValueError:
            context['error'] = 'El monto ingresado no es un número válido.'
        except Exception:
            context['error'] = 'Ocurrió un error inesperado. Por favor, intenta de nuevo.'

    return render(request, 'converter/index.html', context)
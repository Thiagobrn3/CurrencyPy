# converter/views.py
import requests
from django.shortcuts import render

def get_currencies():
    """
    Función para obtener la lista de monedas y sus nombres desde la API.
    """
    try:
        url = 'https://api.frankfurter.app/currencies'
        response = requests.get(url)
        data = response.json()
        # Convertimos el diccionario de la API a una lista de diccionarios
        # que nuestra plantilla pueda usar fácilmente.
        currencies_list = [{'code': code, 'name': name} for code, name in data.items()]
        return currencies_list
    except Exception:
        # En caso de que la API de monedas falle, usamos una lista de respaldo.
        return [
            {'code': 'USD', 'name': 'Dólar Americano'},
            {'code': 'EUR', 'name': 'Euro'},
            {'code': 'JPY', 'name': 'Yen Japonés'},
        ]

def home(request):
    # Obtenemos la lista de monedas actualizada
    currencies = get_currencies()
    context = {'currencies': currencies}

    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        from_currency = request.POST.get('from_currency')
        to_currency = request.POST.get('to_currency')

        # Guardamos las selecciones del usuario en el contexto
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
            
            # Llamamos a la API para la conversión
            url = f'https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}'
            response = requests.get(url)
            data = response.json()

            # Verificamos si la API devolvió un error
            if 'rates' not in data:
                context['error'] = data.get('message', 'No se pudo obtener la tasa de cambio.')
            else:
                converted_amount = data['rates'][to_currency]
                context['converted_amount'] = f"{converted_amount:,.2f}"

        except ValueError:
            context['error'] = 'El monto ingresado no es un número válido.'
        except Exception as e:
            # Ahora mostramos un error más genérico si algo más falla
            context['error'] = f'Ocurrió un error inesperado. Por favor, intenta de nuevo.'

    return render(request, 'converter/index.html', context)
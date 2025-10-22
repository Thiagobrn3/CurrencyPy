# converter/views.py
import requests
from django.shortcuts import render

def home(request):
    # Lista de monedas para los menús desplegables
    currencies = [
        {'code': 'USD', 'name': 'Dólar Americano'},
        {'code': 'EUR', 'name': 'Euro'},
        {'code': 'GBP', 'name': 'Libra Esterlina'},
        {'code': 'JPY', 'name': 'Yen Japonés'},
        {'code': 'ARS', 'name': 'Peso Argentino'},
        {'code': 'BRL', 'name': 'Real Brasileño'},
        {'code': 'CLP', 'name': 'Peso Chileno'},
    ]

    context = {
        'currencies': currencies
    }

    # Si el formulario fue enviado (método POST)
    if request.method == 'POST':
        try:
            # 1. OBTENER DATOS DEL FORMULARIO
            amount_str = request.POST.get('amount')
            from_currency = request.POST.get('from_currency')
            to_currency = request.POST.get('to_currency')

            # Validar que el monto no esté vacío
            if not amount_str:
                context['error'] = 'Por favor, ingresa un monto.'
                return render(request, 'converter/index.html', context)
            
            amount = float(amount_str)

            # 2. LLAMAR A LA API DE FRANKFURTER
            # La API convierte el monto por nosotros
            url = f'https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}'
            response = requests.get(url)
            data = response.json()

            # 3. CALCULAR Y PREPARAR EL RESULTADO
            # El resultado está en el diccionario 'rates'
            converted_amount = data['rates'][to_currency]
            
            # 4. PREPARAR EL CONTEXTO PARA MOSTRAR EN LA PLANTILLA
            context['converted_amount'] = f"{converted_amount:,.2f}" # Formateado con 2 decimales
            context['original_amount'] = f"{amount:,.2f}"
            context['from_currency'] = from_currency
            context['to_currency'] = to_currency

        except Exception as e:
            # Manejo de errores (ej: la API no responde o la moneda no existe)
            context['error'] = f'Ocurrió un error: {e}'

    # Renderizar la página (tanto para GET como después de un POST)
    return render(request, 'converter/index.html', context)
from django.shortcuts import render

def home(request):
    # 1. Creamos una lista de monedas de ejemplo para enviar a la plantilla.
    #    Más adelante, esta lista vendrá de una API.
    currencies = [
        {'code': 'USD', 'name': 'Dólar Americano'},
        {'code': 'EUR', 'name': 'Euro'},
        {'code': 'GBP', 'name': 'Libra Esterlina'},
        {'code': 'JPY', 'name': 'Yen Japonés'},
        {'code': 'ARS', 'name': 'Peso Argentino'},
        {'code': 'BRL', 'name': 'Real Brasileño'},
        {'code': 'CLP', 'name': 'Peso Chileno'},
    ]

    # 2. Creamos un diccionario de "contexto". Esta es la forma en que Django
    #    pasa datos desde la vista a la plantilla.
    context = {
        'currencies': currencies
    }

    # 3. Le pasamos el contexto a la plantilla al momento de renderizarla.
    return render(request, 'converter/index.html', context)
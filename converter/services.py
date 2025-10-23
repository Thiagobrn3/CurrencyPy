# converter/services.py
import requests
from datetime import date, timedelta
from django.core.cache import cache

API_KEY = '0e4ca44e95444245cdcb3a1c' # Es recomendable mover esto a variables de entorno

def get_currencies():
    """Obtiene la lista de monedas desde la API o caché."""
    currencies_list = cache.get('currencies_list')
    if currencies_list is None:
        try:
            url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/codes'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            supported_codes = data.get('supported_codes', [])
            currencies_list = [{'code': code, 'name': name} for code, name in supported_codes]
            cache.set('currencies_list', currencies_list, 21600) # Cache por 6 horas
        except requests.RequestException:
            # Fallback en caso de error de la API
            return [{'code': 'USD', 'name': 'Dólar Americano'}, {'code': 'EUR', 'name': 'Euro'}]
    return currencies_list

def get_exchange_table_data():
    """Obtiene los datos para la tabla de conversión cruzada."""
    cached_data = cache.get('exchange_table_data')
    if cached_data is None:
        try:
            column_codes = ['USD', 'EUR', 'BRL', 'CHF', 'GBP', 'ARS', 'MXN']
            row_codes = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'ARS', 'BRL', 'MXN']
            url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            rates_from_usd = data.get('conversion_rates', {})
            if not rates_from_usd:
                return None, None
            
            table_data = []
            for base_code in row_codes:
                row = {'base': base_code, 'rates': []}
                for quote_code in column_codes:
                    if base_code in rates_from_usd and quote_code in rates_from_usd:
                        cross_rate = rates_from_usd[quote_code] / rates_from_usd[base_code]
                        row['rates'].append(cross_rate)
                    else:
                        row['rates'].append(None)
                table_data.append(row)
            
            cached_data = (table_data, column_codes)
            cache.set('exchange_table_data', cached_data, 3600) # Cache por 1 hora
        except requests.RequestException:
            return None, None
    return cached_data

def get_conversion_result(amount, from_currency, to_currency):
    """Realiza la conversión de una moneda a otra."""
    if from_currency == to_currency:
        return amount

    try:
        url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}/{amount}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('result') == 'success':
            return data.get('conversion_result')
        else:
            return None
    except requests.RequestException:
        return None

def get_charts_data():
    """Obtiene los datos históricos para los gráficos de monedas."""
    base_currency = 'USD'
    quote_currencies = ['EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'CNY']
    symbols_string = ",".join(quote_currencies)
    cache_key = f'charts_data_{base_currency}_{symbols_string}'
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    charts_data = {}

    try:
        url = f"https://api.frankfurter.app/{start_date}..{end_date}?from={base_currency}&to={symbols_string}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "rates" in data:
            for currency in quote_currencies:
                charts_data[currency] = {'dates': [], 'rates': []}

            for date_str, daily_rates in sorted(data["rates"].items()):
                for currency_code, rate in daily_rates.items():
                    charts_data[currency_code]['dates'].append(date_str)
                    charts_data[currency_code]['rates'].append(rate)
        
        cache.set(cache_key, charts_data, 10800) # Cache por 3 horas
        return charts_data
    except requests.RequestException:
        return {}
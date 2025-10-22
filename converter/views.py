import requests
from django.shortcuts import render
import json
from datetime import date, timedelta
from django.core.cache import cache

API_KEY = '0e4ca44e95444245cdcb3a1c'

def get_currencies():
    currencies_list = cache.get('currencies_list')
    if currencies_list is None:
        try:
            url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/codes'
            response = requests.get(url)
            data = response.json()
            supported_codes = data.get('supported_codes', [])
            currencies_list = [{'code': code, 'name': name} for code, name in supported_codes]
            cache.set('currencies_list', currencies_list, 21600)
        except Exception:
            return [{'code': 'USD', 'name': 'DÃ³lar Americano'}, {'code': 'EUR', 'name': 'Euro'}]
    return currencies_list

def get_exchange_table_data():
    cached_data = cache.get('exchange_table_data')
    if cached_data is None:
        try:
            column_codes = ['USD', 'EUR', 'BRL', 'CHF', 'GBP', 'ARS', 'MXN']
            row_codes = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'ARS', 'BRL', 'MXN']
            url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD'
            response = requests.get(url)
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
            cache.set('exchange_table_data', cached_data, 3600)
        except Exception:
            return None, None
    return cached_data

def home(request):
    currencies = get_currencies()
    # OptimizaciÃ³n: llamamos a la funciÃ³n una sola vez
    table_info = get_exchange_table_data()
    exchange_table, column_currencies = table_info if table_info else (None, None)
    
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
            url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}/{amount}'
            response = requests.get(url)
            data = response.json()
            if data.get('result') == 'success':
                converted_amount = data.get('conversion_result')
                context['converted_amount'] = f"{converted_amount:,.2f}"
            else:
                context['error'] = data.get('error-type', 'No se pudo realizar la conversiÃ³n.')
        except ValueError:
            context['error'] = 'El monto ingresado no es un nÃºmero vÃ¡lido.'
        except Exception:
            context['error'] = 'OcurriÃ³ un error inesperado. Por favor, intenta de nuevo.'

    return render(request, 'converter/index.html', context)

def charts_view(request):
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    # --- CAMBIAMOS ARS POR EUR PARA QUE EL GRÃFICO FUNCIONE ---
    base_currency = 'USD'
    quote_currency = 'EUR'
    
    dates, rates = [], []
    cache_key = f'chart_data_{base_currency}_{quote_currency}'
    chart_data = cache.get(cache_key)

    if chart_data is None:
        try:
            url = f"https://api.frankfurter.app/{start_date}..{end_date}?from={base_currency}&to={quote_currency}"
            response = requests.get(url)
            data = response.json()
            
            timeseries_data = sorted(data.get("rates", {}).items())
            for date_str, daily_rates in timeseries_data:
                if quote_currency in daily_rates:
                    dates.append(date_str)
                    rates.append(daily_rates[quote_currency])
            
            chart_data = {'dates': dates, 'rates': rates}
            cache.set(cache_key, chart_data, 10800)
        except Exception as e:
            print(f"Error al obtener datos de Frankfurter: {e}")
    else:
        dates = chart_data['dates']
        rates = chart_data['rates']

    context = {
        'dates_json': json.dumps(dates),
        'rates_json': json.dumps(rates),
        'base_currency': base_currency,
        'quote_currency': quote_currency,
    }
    
    return render(request, 'converter/charts.html', context)
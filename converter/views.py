# converter/views.py
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
import json
from . import services

class HomeView(View):
    template_name = 'converter/index.html'

    def get_context_data(self, **kwargs):
        """Prepara el contexto base para la plantilla."""
        currencies = services.get_currencies()
        exchange_table, column_currencies = services.get_exchange_table_data()
        
        context = {
            'currencies': currencies,
            'exchange_table': exchange_table,
            'column_currencies': column_currencies,
        }
        context.update(kwargs) # Combina con otros argumentos de contexto
        return context

    def get(self, request, *args, **kwargs):
        """Maneja las solicitudes GET para mostrar el formulario."""
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Maneja las solicitudes POST para la conversión de moneda."""
        amount_str = request.POST.get('amount')
        from_currency = request.POST.get('from_currency')
        to_currency = request.POST.get('to_currency')

        context = self.get_context_data(
            from_currency=from_currency,
            to_currency=to_currency
        )
        
        if not amount_str:
            context['error'] = 'Por favor, ingresa un monto.'
            return render(request, self.template_name, context)

        try:
            amount = float(amount_str)
            context['original_amount'] = f"{amount:,.2f}"

            converted_amount = services.get_conversion_result(amount, from_currency, to_currency)
            
            if converted_amount is not None:
                context['converted_amount'] = f"{converted_amount:,.2f}"
            else:
                context['error'] = 'No se pudo realizar la conversión en este momento.'

        except ValueError:
            context['error'] = 'El monto ingresado no es un número válido.'
        
        return render(request, self.template_name, context)


class ChartsView(TemplateView):
    template_name = 'converter/charts.html'

    def get_context_data(self, **kwargs):
        """Obtiene los datos y los añade al contexto para la plantilla de gráficos."""
        context = super().get_context_data(**kwargs)
        charts_data = services.get_charts_data()
        
        context.update({
            'charts_data_json': json.dumps(charts_data),
            'base_currency': 'USD',
        })
        return context
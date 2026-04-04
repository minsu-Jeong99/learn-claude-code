from django import forms
from .models import Ticker, Position, Dividend

WIDGET_ATTRS = {'class': 'form-control'}
DATE_ATTRS = {'class': 'form-control', 'type': 'date'}


class TickerForm(forms.ModelForm):
    class Meta:
        model = Ticker
        fields = ['symbol', 'name', 'sector', 'current_price']
        widgets = {
            'symbol': forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'e.g. SCHD'}),
            'name': forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'Full name'}),
            'sector': forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'e.g. ETF, Technology'}),
            'current_price': forms.NumberInput(attrs={**WIDGET_ATTRS, 'step': '0.01', 'placeholder': '0.00'}),
        }


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['ticker', 'shares', 'cost_basis_per_share', 'date_acquired', 'notes']
        widgets = {
            'ticker': forms.Select(attrs=WIDGET_ATTRS),
            'shares': forms.NumberInput(attrs={**WIDGET_ATTRS, 'step': '0.0001', 'placeholder': '0.0000'}),
            'cost_basis_per_share': forms.NumberInput(attrs={**WIDGET_ATTRS, 'step': '0.01', 'placeholder': '0.00'}),
            'date_acquired': forms.DateInput(attrs=DATE_ATTRS),
            'notes': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}),
        }


class DividendForm(forms.ModelForm):
    class Meta:
        model = Dividend
        fields = ['ticker', 'ex_date', 'pay_date', 'amount_per_share']
        widgets = {
            'ticker': forms.Select(attrs=WIDGET_ATTRS),
            'ex_date': forms.DateInput(attrs=DATE_ATTRS),
            'pay_date': forms.DateInput(attrs=DATE_ATTRS),
            'amount_per_share': forms.NumberInput(attrs={**WIDGET_ATTRS, 'step': '0.000001', 'placeholder': '0.000000'}),
        }

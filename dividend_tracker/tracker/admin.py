from django.contrib import admin
from .models import Ticker, Position, Dividend


@admin.register(Ticker)
class TickerAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'sector', 'current_price', 'updated_at']
    search_fields = ['symbol', 'name']
    list_filter = ['sector']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'shares', 'cost_basis_per_share', 'date_acquired']
    list_filter = ['ticker']
    date_hierarchy = 'date_acquired'


@admin.register(Dividend)
class DividendAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'ex_date', 'pay_date', 'amount_per_share']
    list_filter = ['ticker']
    date_hierarchy = 'ex_date'

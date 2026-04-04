from decimal import Decimal
from datetime import date, timedelta
from django.db import models


class Ticker(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['symbol']

    def __str__(self):
        return self.symbol

    def save(self, *args, **kwargs):
        self.symbol = self.symbol.upper()
        super().save(*args, **kwargs)

    @property
    def annual_dividend_per_share(self):
        """Trailing 12-month dividend sum; annualizes if < 12 months of data."""
        one_year_ago = date.today() - timedelta(days=365)
        divs = self.dividend_set.filter(ex_date__gte=one_year_ago).order_by('ex_date')
        if not divs.exists():
            return Decimal('0')
        total = sum(d.amount_per_share for d in divs)
        # Annualize if we have less than 12 months of history
        oldest = self.dividend_set.order_by('ex_date').first()
        if oldest and oldest.ex_date > one_year_ago:
            count = divs.count()
            if count > 0:
                avg = total / count
                total = avg * 12
        return total

    @property
    def current_yield(self):
        """Annual dividend / current price * 100."""
        if not self.current_price or self.current_price == 0:
            return None
        return (self.annual_dividend_per_share / self.current_price) * 100


class Position(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    shares = models.DecimalField(max_digits=12, decimal_places=4)
    cost_basis_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    date_acquired = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['ticker__symbol', '-date_acquired']

    def __str__(self):
        return f"{self.ticker.symbol} × {self.shares}"

    @property
    def total_cost_basis(self):
        return self.shares * self.cost_basis_per_share

    @property
    def market_value(self):
        if not self.ticker.current_price:
            return None
        return self.shares * self.ticker.current_price

    @property
    def gain_loss(self):
        mv = self.market_value
        if mv is None:
            return None
        return mv - self.total_cost_basis

    @property
    def yield_on_cost(self):
        if not self.cost_basis_per_share or self.cost_basis_per_share == 0:
            return Decimal('0')
        return (self.ticker.annual_dividend_per_share / self.cost_basis_per_share) * 100

    @property
    def projected_annual_income(self):
        return self.ticker.annual_dividend_per_share * self.shares

    @property
    def projected_monthly_income(self):
        return self.projected_annual_income / 12


class Dividend(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    ex_date = models.DateField()
    pay_date = models.DateField(null=True, blank=True)
    amount_per_share = models.DecimalField(max_digits=10, decimal_places=6)

    class Meta:
        ordering = ['-ex_date']
        unique_together = [('ticker', 'ex_date')]

    def __str__(self):
        return f"{self.ticker.symbol} ${self.amount_per_share} on {self.ex_date}"

    @property
    def total_received(self):
        """Sum over positions held at ex_date."""
        total = Decimal('0')
        for position in self.ticker.position_set.filter(date_acquired__lte=self.ex_date):
            total += position.shares * self.amount_per_share
        return total

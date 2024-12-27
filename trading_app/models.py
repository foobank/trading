from django.db import models

class TradeOrder(models.Model):
    market = models.CharField(max_length=20)  # 예: KRW-BTC
    side = models.CharField(max_length=4)     # 'bid'(매수), 'ask'(매도)
    volume = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    order_type = models.CharField(max_length=10, default='limit')  # 'limit', 'market', 'price'
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='requested')  # 'requested', 'done', etc.

    def __str__(self):
        return f"[{self.market}] {self.side} - {self.volume or 0} @ {self.price or 0}"

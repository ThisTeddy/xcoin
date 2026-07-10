from django.db import models
from django.contrib.auth.models import AbstractUser


# ==========================
# USER
# ==========================

class User(AbstractUser):

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=20, blank=True)

    country = models.CharField(max_length=100, blank=True)

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


# ==========================
# WALLET
# ==========================

class Wallet(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wallet"
    )

    balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    bonus = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.email} Wallet"


# ==========================
# MARKET
# ==========================

class Asset(models.Model):

    TYPES = (

        ("crypto", "Crypto"),

        ("stock", "Stock"),

        ("forex", "Forex"),

        ("commodity", "Commodity"),

    )

    symbol = models.CharField(max_length=20)

    name = models.CharField(max_length=100)

    asset_type = models.CharField(
        max_length=20,
        choices=TYPES
    )

    current_price = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    logo = models.ImageField(
        upload_to="assets/",
        blank=True,
        null=True
    )

    active = models.BooleanField(default=True)

    def __str__(self):
        return self.symbol


# ==========================
# PORTFOLIO
# ==========================

class Portfolio(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=25,
        decimal_places=10,
        default=0
    )

    average_buy_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    class Meta:
        unique_together = ("user", "asset")

    def __str__(self):
        return f"{self.user.email} - {self.asset.symbol}"


# ==========================
# INVESTMENT PLANS
# ==========================

class InvestmentPlan(models.Model):

    name = models.CharField(max_length=100)

    minimum_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    maximum_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    roi_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    duration_days = models.PositiveIntegerField()

    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ==========================
# INVESTMENTS
# ==========================

class Investment(models.Model):

    STATUS = (

        ("running", "Running"),

        ("completed", "Completed"),

    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    plan = models.ForeignKey(
        InvestmentPlan,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    expected_profit = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="running"
    )

    start_date = models.DateTimeField(
        auto_now_add=True
    )

    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"


class Payment(models.Model):

    METHODS = (

        ("wallet","Wallet"),

        ("crypto","Crypto"),

        ("bank","Bank"),

    )

    PURPOSES = (

        ("deposit","Deposit"),

        ("investment","Investment"),

        ("buy_asset","Buy Asset"),

    )

    STATUS = (

        ("pending","Pending"),

        ("approved","Approved"),

        ("rejected","Rejected"),

    )

    user=models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    amount=models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    purpose=models.CharField(
        max_length=30,
        choices=PURPOSES
    )

    method=models.CharField(
        max_length=20,
        choices=METHODS
    )

    network=models.CharField(
        max_length=30,
        blank=True
    )

    txid=models.CharField(
        max_length=300,
        blank=True
    )

    proof=models.ImageField(
        upload_to="payments/",
        blank=True,
        null=True
    )

    reference=models.CharField(
        max_length=100,
        unique=True
    )

    metadata=models.JSONField(
        default=dict,
        blank=True
    )

    status=models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending"
    )

    created_at=models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.reference
# ==========================
# TRANSACTIONS
# ==========================

class Transaction(models.Model):

    TYPES = (

        ("deposit", "Deposit"),

        ("withdrawal", "Withdrawal"),

        ("buy", "Buy"),

        ("sell", "Sell"),

        ("investment", "Investment"),

        ("profit", "Profit"),

        ("bonus", "Bonus"),

    )

    STATUS = (

        ("pending", "Pending"),

        ("completed", "Completed"),

        ("failed", "Failed"),

    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    transaction_type = models.CharField(
        max_length=30,
        choices=TYPES
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="completed"
    )

    reference = models.CharField(
        max_length=100,
        unique=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.reference


# ==========================
# NOTIFICATIONS
# ==========================

class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=100)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


# ==========================
# DEPOSIT WALLET
# ==========================

class DepositWallet(models.Model):

    network = models.CharField(max_length=30)

    wallet_address = models.TextField()

    qr_code = models.ImageField(
        upload_to="wallets/",
        blank=True,
        null=True
    )

    active = models.BooleanField(default=True)

    def __str__(self):
        return self.network


# ==========================
# SITE SETTINGS
# ==========================

class SiteSettings(models.Model):

    site_name = models.CharField(max_length=100)

    support_email = models.EmailField()

    minimum_deposit = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=10
    )

    minimum_withdrawal = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=20
    )

    def __str__(self):
        return self.site_name
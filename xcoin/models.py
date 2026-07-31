from django.contrib.auth.models import AbstractUser
from django.db import models
import random 
import string 
from cloudinary.models import CloudinaryField

def generate_referral_code():
    while True:
        code = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )
        if not User.objects.filter(referral_code=code).exists():
            return code
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("Email address is required.")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email,
            password,
            **extra_fields
        )


class User(AbstractUser):

    username = None

    email = models.EmailField(
        unique=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=20,
        unique=True
    )

    country = models.CharField(
        max_length=120,
        blank=True
    )

    avatar = CloudinaryField(
    "avatar",
    folder="xcoin/avatars",
    blank=True,
    null=True,
    )

    email_verified = models.BooleanField(
        default=False
    )

    is_verified = models.BooleanField(
        default=False
    )

    is_suspended = models.BooleanField(
        default=False
    )

    referral_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    referred_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:

        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        if not self.referral_code:
            self.referral_code = generate_referral_code()

        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.email

    
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

    locked_balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        help_text="Funds locked in investments or pending trades"
    )

    total_deposit = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    total_withdrawal = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    total_profit = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    total_bonus = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def available_balance(self):
        return self.balance - self.locked_balance

    def __str__(self):
        return f"{self.user.email} Wallet"


from django.db import models


class Asset(models.Model):

    ASSET_TYPES = (
        ("crypto", "Cryptocurrency"),
        ("stock", "Stock"),
        ("forex", "Forex"),
        ("commodity", "Commodity"),
        ("etf", "ETF"),
        ("index", "Index"),
    )

    name = models.CharField(
        max_length=100
    )

    symbol = models.CharField(
        max_length=20,
        unique=True
    )

    asset_type = models.CharField(
        max_length=20,
        choices=ASSET_TYPES
    )

    logo = models.ImageField(
        upload_to="assets/",
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True
    )

    current_price = models.DecimalField(
        max_digits=20,
        decimal_places=8
    )

    market_cap = models.DecimalField(
        max_digits=25,
        decimal_places=2,
        default=0
    )

    volume_24h = models.DecimalField(
        max_digits=25,
        decimal_places=2,
        default=0
    )

    circulating_supply = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        default=0
    )

    high_24h = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=0
    )

    low_24h = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=0
    )

    ath = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=0,
        verbose_name="All Time High"
    )

    atl = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=0,
        verbose_name="All Time Low"
    )

    change = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="24 Hour Percentage Change"
    )

    active = models.BooleanField(
        default=True
    )

    featured = models.BooleanField(
        default=False
    )

    rank = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["rank", "name"]

    def __str__(self):
        return f"{self.symbol} ({self.name})"

class Portfolio(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="portfolio"
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="holders"
    )

    quantity = models.DecimalField(
        max_digits=30,
        decimal_places=10,
        default=0
    )

    average_buy_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        unique_together = ("user", "asset")

        ordering = ["asset__name"]

    def __str__(self):

        return f"{self.user.email} • {self.asset.symbol}"



class InvestmentPlan(models.Model):

    PLAN_TYPES = (

        ("fixed", "Fixed ROI"),

        ("flexible", "Flexible"),

    )

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    plan_type = models.CharField(
        max_length=20,
        choices=PLAN_TYPES,
        default="fixed"
    )

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

    active = models.BooleanField(
        default=True
    )

    featured = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["minimum_amount"]

    def __str__(self):

        return self.name


from django.db import models
from django.utils import timezone


class Investment(models.Model):

    STATUS = (

        ("pending", "Pending"),

        ("running", "Running"),

        ("completed", "Completed"),

        ("cancelled", "Cancelled"),

    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="investments"
    )

    plan = models.ForeignKey(
        InvestmentPlan,
        on_delete=models.PROTECT,
        related_name="investments"
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
        default="pending",
        db_index=True
    )

    start_date = models.DateTimeField(auto_now_add=True)

    end_date = models.DateTimeField()

    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [

            models.Index(fields=["user"]),

            models.Index(fields=["status"]),

            models.Index(fields=["end_date"]),

            models.Index(fields=["user", "status"]),

        ]

    @property
    def is_active(self):
        return (
            self.status == "running"
            and self.end_date > timezone.now()
        )

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

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
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    transaction_type = models.CharField(
        max_length=30,
        choices=TYPES
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=0
    )

    price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=0
    )
    txid = models.CharField(
    max_length=255,
    blank=True,
    null=True,
    )

    proof = models.ImageField(
    upload_to="deposit_proofs/",
    blank=True,
    null=True,
    )
    fee = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    reference = models.CharField(
        max_length=100,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending"
    )

    remarks = models.TextField(
        blank=True
    )

    metadata = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def total_value(self):
        return self.amount + self.fee

    def __str__(self):
        return f"{self.reference} ({self.transaction_type})"


class Payment(models.Model):

    METHODS = (

        ("wallet", "Wallet"),

        ("crypto", "Crypto"),

        ("bank", "Bank"),

    )

    PURPOSES = (

        ("deposit", "Deposit"),

        ("investment", "Investment"),

        ("buy_asset", "Buy Asset"),

    )

    NETWORKS = (

        ("", "Select Network"),

        ("BTC", "Bitcoin"),

        ("ETH", "Ethereum"),

        ("USDT_TRC20", "USDT (TRC20)"),

        ("USDT_ERC20", "USDT (ERC20)"),

        ("USDT_BEP20", "USDT (BEP20)"),

        ("BNB", "BNB Smart Chain"),

        ("SOL", "Solana"),

        ("LTC", "Litecoin"),

        ("DOGE", "Dogecoin"),

        ("BANK", "Bank Transfer"),

    )

    STATUS = (

        ("pending", "Pending"),

        ("approved", "Approved"),

        ("rejected", "Rejected"),

        ("cancelled", "Cancelled"),

    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    purpose = models.CharField(
        max_length=30,
        choices=PURPOSES,
        db_index=True
    )

    method = models.CharField(
        max_length=20,
        choices=METHODS,
        db_index=True
    )

    network = models.CharField(
        max_length=30,
        choices=NETWORKS,
        blank=True,
        default=""
    )

    txid = models.CharField(
        max_length=300,
        blank=True
    )

    proof = models.ImageField(
        upload_to="payments/",
        blank=True,
        null=True
    )

    reference = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    metadata = models.JSONField(
        default=dict,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending",
        db_index=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [

            models.Index(fields=["user"]),

            models.Index(fields=["status"]),

            models.Index(fields=["purpose"]),

            models.Index(fields=["method"]),

            models.Index(fields=["user", "status"]),

        ]

    def __str__(self):
        return f"{self.reference} ({self.user.email})"

from django.db import models

class DepositWallet(models.Model):

    NETWORKS = (
        ("BTC", "Bitcoin"),
        ("ETH", "Ethereum"),
        ("USDT_TRC20", "USDT (TRC20)"),
        ("USDT_ERC20", "USDT (ERC20)"),
        ("USDT_BEP20", "USDT (BEP20)"),
        ("BNB", "BNB Smart Chain"),
        ("SOL", "Solana"),
        ("LTC", "Litecoin"),
        ("DOGE", "Dogecoin"),
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="deposit_wallets",
    )

    network = models.CharField(
        max_length=30,
        choices=NETWORKS,
        unique=True
    )

    wallet_address = models.TextField()
    
    qr_code = CloudinaryField(
    "qr_code",
    folder="xcoin/wallets",
    blank=True,
    null=True,
    )
    active = models.BooleanField(
        default=True,
        db_index=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["network"]

    def __str__(self):
        return self.get_network_display()
    
class SiteSettings(models.Model):

    site_name = models.CharField(
        max_length=100
    )

    support_email = models.EmailField()

    support_phone = models.CharField(
        max_length=30,
        blank=True
    )

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

    maintenance_mode = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        self.pk = 1

        super().save(*args, **kwargs)

    class Meta:

        verbose_name = "Site Settings"

        verbose_name_plural = "Site Settings"

    def __str__(self):

        return self.site_name

class Notification(models.Model):

    TYPES = (

        ("system", "System"),

        ("deposit", "Deposit"),

        ("withdrawal", "Withdrawal"),

        ("investment", "Investment"),

        ("market", "Market"),

        ("security", "Security"),

    )

    PRIORITY = (

        ("low", "Low"),

        ("normal", "Normal"),

        ("high", "High"),

    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    notification_type = models.CharField(
        max_length=30,
        choices=TYPES,
        default="system",
        db_index=True
    )

    title = models.CharField(
        max_length=150
    )

    message = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY,
        default="normal"
    )

    is_read = models.BooleanField(
        default=False,
        db_index=True
    )
    send_email = models.BooleanField(default=False)
    action_url = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [

            models.Index(fields=["user"]),

            models.Index(fields=["user", "is_read"]),

            models.Index(fields=["notification_type"]),

        ]

    def __str__(self):

        return f"{self.user.email} - {self.title}"

class EmailTemplate(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    subject = models.CharField(
        max_length=200
    )

    html_body = models.TextField()

    text_body = models.TextField(
        blank=True
    )

    active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class EmailLog(models.Model):

    STATUS = (

        ("pending", "Pending"),

        ("sent", "Sent"),

        ("failed", "Failed"),

    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_logs"
    )

    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    subject = models.CharField(
        max_length=200
    )

    recipient = models.EmailField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending",
        db_index=True
    )

    error_message = models.TextField(
        blank=True
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} - {self.subject}"


from cloudinary.models import CloudinaryField
from django.db import models


class KYCVerification(models.Model):

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    # --------------------------------------------------
    # DOCUMENT TYPES
    # --------------------------------------------------

    DOCUMENT_TYPES = (
        ("passport", "Passport"),
        ("drivers_license", "Driver's License"),
        ("state_id", "State ID"),
        ("government_id", "Government ID"),
        ("national_id", "National ID"),
    )

    # --------------------------------------------------
    # USER
    # --------------------------------------------------

    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE,
        related_name="kyc",
    )

    # --------------------------------------------------
    # PERSONAL / VERIFICATION DETAILS
    # --------------------------------------------------

    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPES,
    )

    document_number = models.CharField(
        max_length=100,
        blank=True,
    )

    # --------------------------------------------------
    # DOCUMENT UPLOADS
    # --------------------------------------------------

    document_front = CloudinaryField(
        "document_front",
        folder="xcoin/kyc/documents",
    )

    document_back = CloudinaryField(
        "document_back",
        folder="xcoin/kyc/documents",
        blank=True,
        null=True,
    )

    # --------------------------------------------------
    # SELFIE
    # --------------------------------------------------

    selfie = CloudinaryField(
        "selfie",
        folder="xcoin/kyc/selfies",
    )

    # --------------------------------------------------
    # VERIFICATION STATUS
    # --------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )

    rejection_reason = models.TextField(
        blank=True,
    )

    # --------------------------------------------------
    # REVIEW INFORMATION
    # --------------------------------------------------

    submitted_at = models.DateTimeField(
        auto_now_add=True,
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # --------------------------------------------------
    # META
    # --------------------------------------------------

    class Meta:

        ordering = ["-submitted_at"]

        verbose_name = "KYC Verification"

        verbose_name_plural = "KYC Verifications"

    # --------------------------------------------------
    # STRING
    # --------------------------------------------------

    def __str__(self):

        return f"{self.user.email} - {self.get_status_display()}"
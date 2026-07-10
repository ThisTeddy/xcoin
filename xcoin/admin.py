from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    User,
    Wallet,
    Asset,
    Portfolio,
    InvestmentPlan,
    Investment,
    Payment,
    Transaction,
    Notification,
    DepositWallet,
    SiteSettings,
)


# ==========================
# USER
# ==========================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        "email",
        "username",
        "phone",
        "country",
        "email_verified",
        "is_staff",
        "date_joined",
    )

    list_filter = (
        "email_verified",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "email",
        "username",
        "phone",
    )

    ordering = (
        "-date_joined",
    )


# ==========================
# WALLET
# ==========================

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "balance",
        "bonus",
        "updated_at",
    )

    search_fields = (
        "user__email",
    )


# ==========================
# ASSETS
# ==========================

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):

    list_display = (
        "symbol",
        "name",
        "asset_type",
        "current_price",
        "change",
        "active",
    )

    list_filter = (
        "asset_type",
        "active",
    )

    search_fields = (
        "symbol",
        "name",
    )


# ==========================
# PORTFOLIO
# ==========================

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "asset",
        "quantity",
        "average_buy_price",
    )

    search_fields = (
        "user__email",
        "asset__symbol",
    )


# ==========================
# INVESTMENT PLAN
# ==========================

@admin.register(InvestmentPlan)
class InvestmentPlanAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "minimum_amount",
        "maximum_amount",
        "roi_percent",
        "duration_days",
        "active",
    )


# ==========================
# INVESTMENTS
# ==========================

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "plan",
        "amount",
        "expected_profit",
        "status",
        "start_date",
        "end_date",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "user__email",
    )


# ==========================
# PAYMENTS
# ==========================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "reference",
        "user",
        "purpose",
        "method",
        "amount",
        "status",
        "created_at",
    )

    list_filter = (
        "purpose",
        "method",
        "status",
    )

    search_fields = (
        "reference",
        "user__email",
    )


# ==========================
# TRANSACTIONS
# ==========================

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    list_display = (
        "reference",
        "user",
        "transaction_type",
        "amount",
        "status",
        "created_at",
    )

    list_filter = (
        "transaction_type",
        "status",
    )

    search_fields = (
        "reference",
        "user__email",
    )


# ==========================
# NOTIFICATIONS
# ==========================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "title",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
    )

    search_fields = (
        "user__email",
        "title",
    )


# ==========================
# DEPOSIT WALLET
# ==========================

@admin.register(DepositWallet)
class DepositWalletAdmin(admin.ModelAdmin):

    list_display = (
        "network",
        "wallet_address",
        "active",
    )


# ==========================
# SITE SETTINGS
# ==========================

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

    list_display = (
        "site_name",
        "support_email",
        "minimum_deposit",
        "minimum_withdrawal",
    )


# ==========================
# AUTO CREATE WALLET
# ==========================


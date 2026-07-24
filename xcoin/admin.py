from django.contrib import admin, messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


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
    EmailTemplate,
    EmailLog,
)


# ==========================================
# EMAIL HELPER
# ==========================================

def send_user_email(user, subject, message):

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )



# ==========================================
# USER
# ==========================================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "email",
        "username",
        "phone",
        "country",
        "email_verified",
        "is_active",
        "date_joined",
    )

    list_filter = (
        "email_verified",
        "is_active",
    )

    search_fields = (
        "email",
        "username",
        "phone",
    )



# ==========================================
# WALLET
# ==========================================

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



# ==========================================
# ASSET
# ==========================================

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



# ==========================================
# PORTFOLIO
# ==========================================

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "asset",
        "quantity",
        "average_buy_price",
    )



# ==========================================
# INVESTMENT PLAN
# ==========================================

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



# ==========================================
# INVESTMENTS
# ==========================================

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



# ==========================================
# PAYMENT ACTIONS
# ==========================================


def approve_payment(modeladmin, request, queryset):

    approved = 0


    for payment in queryset:


        if payment.status != "pending":
            continue



        wallet, created = Wallet.objects.get_or_create(
            user=payment.user
        )


        if payment.purpose == "deposit":

            wallet.balance += payment.amount

            wallet.save()



            Transaction.objects.create(

                user=payment.user,

                transaction_type="deposit",

                amount=payment.amount,

                status="completed",

                reference=f"DEP-{uuid.uuid4().hex[:10].upper()}"

            )



        payment.status = "approved"

        payment.save()



        Notification.objects.create(

            user=payment.user,

            title="Payment Approved",

            message=f"Your {payment.purpose} request has been approved."

        )



        send_user_email(

            payment.user,

            "Payment Approved",

            f"""
Hello {payment.user.username},

Your payment has been approved.

Purpose:
{payment.purpose}

Amount:
${payment.amount}

Reference:
{payment.reference}

Thank you.

"""

        )


        approved += 1



    messages.success(

        request,

        f"{approved} payments approved."

    )



approve_payment.short_description = "Approve selected payments"




def reject_payment(modeladmin, request, queryset):

    rejected = 0


    for payment in queryset:


        if payment.status != "pending":
            continue


        payment.status = "rejected"

        payment.save()



        Notification.objects.create(

            user=payment.user,

            title="Payment Rejected",

            message=f"Your {payment.purpose} request has been rejected."

        )



        send_user_email(

            payment.user,

            "Payment Rejected",

            f"""
Hello {payment.user.username},

Your payment request has been rejected.

Reference:
{payment.reference}

Please contact support.

"""

        )


        rejected += 1



    messages.success(

        request,

        f"{rejected} payments rejected."

    )



reject_payment.short_description = "Reject selected payments"




# ==========================================
# PAYMENT ADMIN
# ==========================================

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

        "status",
        "purpose",
        "method",

    )


    search_fields = (

        "reference",
        "user__email",

    )


    actions = [

        approve_payment,

        reject_payment,

    ]



# ==========================================
# TRANSACTION
# ==========================================

from django.contrib import admin
from django.contrib import messages

from .models import Transaction


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
        "user__username",
        "txid",
    )

    readonly_fields = (
        "reference",
        "txid",
        "proof",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    def save_model(self, request, obj, form, change):

        previous_status = None

        if change:

            previous = Transaction.objects.get(pk=obj.pk)
            previous_status = previous.status

        super().save_model(request, obj, form, change)

        if (
            obj.transaction_type == "deposit"
            and previous_status == "pending"
            and obj.status == "completed"
        ):

            wallet = obj.user.wallet

            wallet.balance += obj.amount

            wallet.total_deposit += obj.amount

            wallet.save()

            self.message_user(
                request,
                f"${obj.amount} credited to {obj.user.username}.",
                level=messages.SUCCESS,
            )

# ==========================================
# NOTIFICATIONS
# ==========================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (

        "user",
        "title",
        "is_read",
        "created_at",

    )



# ==========================================
# DEPOSIT WALLET
# ==========================================

@admin.register(DepositWallet)
class DepositWalletAdmin(admin.ModelAdmin):

    list_display = (

        "network",
        "active",

    )



# ==========================================
# SITE SETTINGS
# ==========================================

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

    list_display = (

        "site_name",
        "support_email",
        "minimum_deposit",
        "minimum_withdrawal",

    )



# ==========================================
# EMAIL TEMPLATE
# ==========================================

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):

    list_display = (

        "name",
        "active",
        "updated_at",

    )



# ==========================================
# EMAIL LOG
# ==========================================

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):

    list_display = (

        "recipient",
        "subject",
        "status",
        "created_at",

    )



# ==========================================
# AUTO CREATE WALLET
# ==========================================

@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):

    if created:

        Wallet.objects.get_or_create(
            user=instance
        )
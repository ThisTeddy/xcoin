from decimal import Decimal
import uuid

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

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

import random
import string

def generate_referral_code():
    while True:
        code = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )
        if not User.objects.filter(referral_code=code).exists():
            return code

def home(request):

    assets = Asset.objects.filter(active=True)[:8]

    plans = InvestmentPlan.objects.filter(active=True)

    return render(
        request,
        "home.html",
        {
            "assets": assets,
            "plans": plans,
        },
    )


def register(request):
    print("========== REGISTER ==========")
    print(request.method)

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        country = request.POST.get("country")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:

            messages.error(request, "Passwords do not match.")

            return redirect("register")

        if User.objects.filter(email=email).exists():

            messages.error(request, "Email already exists.")

            return redirect("register")

        if User.objects.filter(username=username).exists():

            messages.error(request, "Username already exists.")

            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            phone=phone,
            country=country,
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            password=password,
)
       
        Wallet.objects.get_or_create(user=user)

        Notification.objects.create(
            user=user,
            notification_type="system",
            title="Welcome",
            message="Welcome to our investment platform.",
            send_email=False,
        )
        

        messages.success(request, "Registration successful.")

        login(request, user)

        return redirect("dashboard")

    return render(request, "auth/register.html")

@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("home")

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

@login_required
def change_password(request):

    if request.method == "POST":

        current_password = request.POST.get("current_password")

        new_password = request.POST.get("new_password")

        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(current_password):

            messages.error(
                request,
                "Current password is incorrect."
            )

            return redirect("change_password")

        if new_password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("change_password")

        request.user.set_password(new_password)

        request.user.save()

        login(request, request.user)

        messages.success(
            request,
            "Password changed successfully."
        )

        return redirect("profile")

    return render(
        request,
        "change_password.html",
    )

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect

# ==========================================
# LOGIN
# ==========================================

def login_view(request):

    if request.user.is_authenticated:

        return redirect("dashboard")


    if request.method == "POST":

        email = request.POST.get(
            "email"
        )

        password = request.POST.get(
            "password"
        )


        user = authenticate(

            request,

            username=email,

            password=password

        )


        if user is not None:

            login(
                request,
                user
            )


            messages.success(

                request,

                "Welcome back!"

            )


            return redirect(
                "dashboard"
            )


        else:

            messages.error(

                request,

                "Invalid email or password."

            )


    return render(

        request,

        "auth/login.html"

    )

def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email").strip().lower()

        try:

            user = User.objects.get(email=email)

        except User.DoesNotExist:

            messages.error(
                request,
                "No account found with that email."
            )

            return redirect("forgot_password")

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )

        token = default_token_generator.make_token(user)

        reset_link = (
            f"{request.scheme}://"
            f"{request.get_host()}"
            f"/reset-password/{uid}/{token}/"
        )

        send_mail(

            subject="Password Reset",

            message=(
                f"Hello {user.username},\n\n"
                f"Click the link below to reset your password:\n\n"
                f"{reset_link}"
            ),

            from_email=settings.DEFAULT_FROM_EMAIL,

            recipient_list=[user.email],

            fail_silently=False,

        )

        messages.success(

            request,

            "Password reset email sent."

        )

        return redirect("login")

    return render(

        request,

        "forgot_password.html",

    )

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

def reset_password(request, uidb64, token):

    try:

        uid = force_str(
            urlsafe_base64_decode(uidb64)
        )

        user = User.objects.get(pk=uid)

    except Exception:

        user = None

    if user is None or not default_token_generator.check_token(user, token):

        messages.error(
            request,
            "Reset link is invalid or has expired."
        )

        return redirect("login")

    if request.method == "POST":

        password = request.POST.get("password")

        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect(
                "reset_password",
                uidb64=uidb64,
                token=token,
            )

        user.set_password(password)

        user.save()

        messages.success(
            request,
            "Password has been reset successfully."
        )

        return redirect("login")

    return render(
        request,
        "reset_password.html",
    )


from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

@login_required
def investment_plans(request):
    plans = InvestmentPlan.objects.filter(active=True).order_by("minimum_amount")

    return render(
        request,
        "investment/investment_plans.html",
        {
            "plans": plans,
        },
    )

@login_required
def invest(request, plan_id):

    plan = get_object_or_404(
        InvestmentPlan,
        pk=plan_id,
        active=True
    )

    wallet = request.user.wallet

    if request.method == "POST":

        try:

            amount = Decimal(
                request.POST.get("amount")
            )

        except:

            messages.error(
                request,
                "Invalid amount."
            )

            return redirect(
                "invest",
                plan.id
            )

        if amount < plan.minimum_amount:

            messages.error(
                request,
                f"Minimum investment is ${plan.minimum_amount}."
            )

            return redirect(
                "invest",
                plan.id
            )

        if amount > plan.maximum_amount:

            messages.error(
                request,
                f"Maximum investment is ${plan.maximum_amount}."
            )

            return redirect(
                "invest",
                plan.id
            )

        if wallet.balance < amount:

            messages.error(
                request,
                "Insufficient wallet balance."
            )

            return redirect(
                "invest",
                plan.id
            )

        expected_profit = (
            amount *
            plan.roi_percent /
            Decimal("100")
        )

        end_date = (
            timezone.now() +
            timedelta(days=plan.duration_days)
        )

        Investment.objects.create(

    user=request.user,

    plan=plan,

    amount=amount,

    expected_profit=expected_profit,

    end_date=end_date,

    status="active",

)

        wallet.balance -= amount

        wallet.save()

        Transaction.objects.create(

            user=request.user,

            transaction_type="investment",

            amount=amount,

            status="completed",

            reference=f"INV-{uuid.uuid4().hex[:12].upper()}"

        )

        Notification.objects.create(

            user=request.user,

            notification_type="investment",

            title="Investment Started",

            message=f"You invested ${amount} into {plan.name}.",

        )

        messages.success(

            request,

            "Investment created successfully."

        )

        return redirect(
            "my_investments"
        )

    context = {

        "plan": plan,

        "wallet": wallet,

    }

    return render(
        request,
        "investment/invest.html",
        context,
    )


@login_required
def my_investments(request):

    investments = Investment.objects.filter(

        user=request.user

    ).select_related(

        "plan"

    ).order_by(

        "-start_date"

    )

    context = {

        "investments": investments,

    }

    return render(

        request,

        "my_investments.html",

        context,

    )

@login_required
def investment_detail(request, investment_id):

    investment = get_object_or_404(

        Investment,

        id=investment_id,

        user=request.user,

    )

    context = {

        "investment": investment,

    }

    return render(

        request,

        "investment_detail.html",

        context,

    )


@login_required
def cancel_investment(request, investment_id):

    investment = get_object_or_404(

        Investment,

        id=investment_id,

        user=request.user,

        status="running",

    )

    messages.error(

        request,

        "Contact support to cancel this investment."

    )

    return redirect(
        "my_investments"
    )

@login_required
def deposit(request):

    wallets = DepositWallet.objects.filter(
        active=True
    ).order_by("network")

    if request.method == "POST":

        network = request.POST.get("network")

        amount = request.POST.get("amount")

        txid = request.POST.get("txid")

        proof = request.FILES.get("proof")

        if not network or not amount or not txid:

            messages.error(
                request,
                "Please complete all required fields."
            )

            return redirect("deposit")

        try:

            amount = Decimal(amount)

        except:

            messages.error(
                request,
                "Invalid deposit amount."
            )

            return redirect("deposit")

        wallet = get_object_or_404(

            DepositWallet,

            network=network,

            active=True,

        )

        Transaction.objects.create(

    user=request.user,

    transaction_type="deposit",

    amount=amount,

    quantity=Decimal("0"),

    price=Decimal("0"),

    fee=Decimal("0"),

    txid=txid,

    proof=proof,

    status="pending",

    reference=f"DEP-{uuid.uuid4().hex[:10].upper()}",

    remarks=f"Deposit via {wallet.get_network_display()}",

    metadata={
        "network": wallet.network,
        "wallet_address": wallet.wallet_address,
    }

)
            
        Notification.objects.create(

            user=request.user,

            notification_type="deposit",

            title="Deposit Submitted",

            message=f"Your ${amount} deposit via {wallet.get_network_display()} is awaiting confirmation."

        )

        messages.success(

            request,

            "Deposit submitted successfully. It will be credited after confirmation."

        )

        return redirect(
            "transaction_history"
        )

    context = {

        "wallets": wallets,

    }

    return render(

        request,

        "payment/deposit.html",

        context

    )
@login_required
def withdraw(request):

    wallet = request.user.wallet

    if request.method == "POST":

        amount = Decimal(
            request.POST.get("amount")
        )

        address = request.POST.get(
            "wallet_address"
        )

        network = request.POST.get(
            "network"
        )

        if amount <= 0:

            messages.error(
                request,
                "Invalid amount."
            )

            return redirect("withdraw")

        if amount > wallet.balance:

            messages.error(
                request,
                "Insufficient balance."
            )

            return redirect("withdraw")

        Payment.objects.create(

            user=request.user,

            amount=amount,

            purpose="withdrawal",

            method="crypto",

            network=network,

            reference=f"WTH-{uuid.uuid4().hex[:10].upper()}",

            metadata={
                "wallet_address": address
            },

            status="pending",

        )

        Notification.objects.create(

            user=request.user,

            notification_type="withdrawal",

            title="Withdrawal Requested",

            message="Your withdrawal request is pending approval.",

        )

        messages.success(

            request,

            "Withdrawal request submitted."

        )

        return redirect(
            "payment_history"
        )

    return render(
        request,
        "withdraw.html",
        {
            "wallet": wallet,
        },
    )


@login_required
def payment_history(request):

    payments = Payment.objects.filter(

        user=request.user

    ).order_by(

        "-created_at"

    )

    return render(

        request,

        "payment_history.html",

        {

            "payments": payments,

        },

    )


@login_required
def payment_detail(request, payment_id):

    payment = get_object_or_404(

        Payment,

        id=payment_id,

        user=request.user,

    )

    return render(

        request,

        "payment_detail.html",

        {

            "payment": payment,

        },

    )

@login_required
def profile(request):

    wallet = request.user.wallet

    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by("-created_at")[:5]

    investments = Investment.objects.filter(
        user=request.user
    ).count()

    context = {

        "user": request.user,

        "wallet": wallet,

        "transactions": transactions,

        "investment_count": investments,

    }

    return render(
        request,
        "profile.html",
        context,
    )

@login_required
def profile(request):

    wallet = request.user.wallet

    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by("-created_at")[:5]

    investments = Investment.objects.filter(
        user=request.user
    ).count()

    context = {

        "user": request.user,

        "wallet": wallet,

        "transactions": transactions,

        "investment_count": investments,

    }

    return render(
        request,
        "profile.html",
        context,
    )

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from decimal import Decimal

from .models import (
    Wallet,
    Portfolio,
    Investment,
    Transaction,
    Notification,
)

# ==========================================
# DASHBOARD
# ==========================================

@login_required
def dashboard(request):

    user = request.user


    # Wallet

    wallet, created = Wallet.objects.get_or_create(
        user=user
    )



    # Portfolio

    holdings = Portfolio.objects.filter(
        user=user
    ).select_related(
        "asset"
    )


    portfolio_value = Decimal("0")


    for holding in holdings:

        portfolio_value += (
            holding.quantity *
            holding.asset.current_price
        )



    # Investments

    investments = Investment.objects.filter(

        user=user

    ).order_by(

        "-start_date"

    )


    active_investments = investments.filter(

        status="running"

    )


    total_invested = investments.aggregate(

        total=Sum("amount")

    )["total"] or Decimal("0")



    total_profit = investments.aggregate(

        profit=Sum("expected_profit")

    )["profit"] or Decimal("0")




    # Recent Transactions

    transactions = Transaction.objects.filter(

        user=user

    ).order_by(

        "-created_at"

    )[:5]




    # Notifications

    notifications = Notification.objects.filter(

        user=user

    ).order_by(

        "-created_at"

    )[:5]




    context = {


        "wallet": wallet,


        "portfolio_value": portfolio_value,


        "holdings": holdings,


        "investments": investments,


        "active_investments": active_investments,


        "total_invested": total_invested,


        "total_profit": total_profit,


        "transactions": transactions,


        "notifications": notifications,


    }



    return render(

        request,

        "dashboard/dashboard.html",

        context

    )

# ==========================================
# ASSET DETAIL
# ==========================================

@login_required
def asset_detail(request, pk):

    asset = get_object_or_404(
        Asset,
        id=pk,
        active=True
    )


    portfolio = Portfolio.objects.filter(

        user=request.user,

        asset=asset

    ).first()



    return render(

        request,

        "market/asset_detail.html",

        {

            "asset": asset,

            "portfolio": portfolio,

        }

    )

# ==========================================
# EDIT PROFILE
# ==========================================

@login_required
def edit_profile(request):

    user = request.user


    if request.method == "POST":

        user.username = request.POST.get(
            "username"
        )

        user.phone = request.POST.get(
            "phone"
        )

        user.country = request.POST.get(
            "country"
        )


        if request.FILES.get("avatar"):

            user.avatar = request.FILES.get(
                "avatar"
            )


        user.save()


        messages.success(
            request,
            "Profile updated successfully."
        )


        return redirect(
            "profile"
        )


    return render(

        request,

        "profile/edit_profile.html",

        {

            "user": user

        }

    )
@login_required
def account_settings(request):

    settings = SiteSettings.objects.first()

    context = {

        "settings": settings,

    }

    return render(
        request,
        "account_settings.html",
        context,
    )

@login_required
def notifications(request):

    notifications = Notification.objects.filter(

        user=request.user

    ).order_by(

        "-created_at"

    )

    return render(

        request,

        "notifications.html",

        {

            "notifications": notifications,

        },

    )

@login_required
def notification_detail(request, notification_id):

    notification = get_object_or_404(

        Notification,

        id=notification_id,

        user=request.user,

    )

    if not notification.is_read:

        notification.is_read = True

        notification.save()

    return render(

        request,

        "notification_detail.html",

        {

            "notification": notification,

        },

    )

@login_required
def mark_notifications_read(request):

    Notification.objects.filter(

        user=request.user,

        is_read=False

    ).update(

        is_read=True

    )

    messages.success(

        request,

        "All notifications marked as read."

    )

    return redirect(
        "notifications"
    )

from django.views.decorators.http import require_http_methods


# ==========================================
# ABOUT
# ==========================================

@require_http_methods(["GET"])
def about(request):

    settings = SiteSettings.objects.first()

    context = {
        "settings": settings,
    }

    return render(
        request,
        "about.html",
        context,
    )


# ==========================================
# CONTACT
# ==========================================

@require_http_methods(["GET", "POST"])
def contact(request):

    settings = SiteSettings.objects.first()

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # Optional:
        # send email to support
        # create support ticket
        # save message to database

        messages.success(
            request,
            "Your message has been sent successfully. Our support team will contact you shortly."
        )

        return redirect("contact")

    context = {
        "settings": settings,
    }

    return render(
        request,
        "contact.html",
        context,
    )


# ==========================================
# HELP CENTER
# ==========================================

@require_http_methods(["GET"])
def help_center(request):

    settings = SiteSettings.objects.first()

    context = {
        "settings": settings,
    }

    return render(
        request,
        "help_center.html",
        context,
    )


# ==========================================
# FAQ
# ==========================================

@require_http_methods(["GET"])
def faq(request):

    settings = SiteSettings.objects.first()

    faqs = [

        {
            "question": "How do I make a deposit?",
            "answer": "Navigate to the Deposit page, choose a payment method, upload payment proof and wait for approval."
        },

        {
            "question": "When will my deposit reflect?",
            "answer": "Deposits are credited after confirmation by our finance department."
        },

        {
            "question": "How do investments work?",
            "answer": "Choose an investment plan, invest using your wallet balance and receive profits according to your selected plan."
        },

        {
            "question": "How long do withdrawals take?",
            "answer": "Withdrawal requests are processed after approval and are usually completed within the stated processing period."
        },

        {
            "question": "Can I cancel my investment?",
            "answer": "Cancellation depends on the investment agreement. Please contact support for assistance."
        },

    ]

    context = {

        "settings": settings,

        "faqs": faqs,

    }

    return render(
        request,
        "faq.html",
        context,
    )


# ==========================================
# PRIVACY POLICY
# ==========================================

@require_http_methods(["GET"])
def privacy_policy(request):

    settings = SiteSettings.objects.first()

    context = {

        "settings": settings,

    }

    return render(
        request,
        "privacy_policy.html",
        context,
    )


# ==========================================
# TERMS & CONDITIONS
# ==========================================

@require_http_methods(["GET"])
def terms_and_conditions(request):

    settings = SiteSettings.objects.first()

    context = {

        "settings": settings,

    }

    return render(
        request,
        "terms.html",
        context,
    )


# ==========================================
# COOKIE POLICY
# ==========================================

@require_http_methods(["GET"])
def cookie_policy(request):

    settings = SiteSettings.objects.first()

    context = {

        "settings": settings,

    }

    return render(
        request,
        "cookie_policy.html",
        context,
    )


# ==========================================
# RISK DISCLOSURE
# ==========================================

@require_http_methods(["GET"])
def risk_disclosure(request):

    settings = SiteSettings.objects.first()

    context = {

        "settings": settings,

    }

    return render(
        request,
        "risk_disclosure.html",
        context,
    )


# ==========================================
# AML POLICY
# ==========================================

@require_http_methods(["GET"])
def aml_policy(request):

    settings = SiteSettings.objects.first()

    context = {

        "settings": settings,

    }

    return render(
        request,
        "aml_policy.html",
        context,
    )


# ==========================================
# KYC POLICY
# ==========================================

@require_http_methods(["GET"])
def kyc_policy(request):

    settings = SiteSettings.objects.first()

    context = {

        "settings": settings,

    }

    return render(
        request,
        "kyc_policy.html",
        context,
    )


@login_required
def buy_asset(request, asset_id):

    asset = get_object_or_404(
        Asset,
        id=asset_id,
        active=True
    )

    wallet = request.user.wallet

    if request.method == "POST":

        amount_str = request.POST.get("amount")

        if not amount_str:
            messages.error(
                request,
                "Please enter an amount."
            )
            return redirect(
                "buy_asset",
                asset.id
            )

        try:
            amount = Decimal(amount_str)
        except Exception:
            messages.error(
                request,
                "Invalid amount."
            )
            return redirect(
                "buy_asset",
                asset.id
            )

        if amount <= Decimal("0"):
            messages.error(
                request,
                "Amount must be greater than zero."
            )
            return redirect(
                "buy_asset",
                asset.id
            )

        if wallet.balance < amount:
            messages.error(
                request,
                "Insufficient wallet balance."
            )
            return redirect(
                "buy_asset",
                asset.id
            )

        quantity = amount / asset.current_price

        wallet.balance -= amount
        wallet.save()

        portfolio, created = Portfolio.objects.get_or_create(
            user=request.user,
            asset=asset,
            defaults={
                "quantity": Decimal("0"),
                "average_buy_price": Decimal("0")
            }
        )

        total_cost = (
            portfolio.average_buy_price * portfolio.quantity
        ) + amount

        portfolio.quantity += quantity

        portfolio.average_buy_price = (
            total_cost / portfolio.quantity
        )

        portfolio.save()

        Transaction.objects.create(
            user=request.user,
            transaction_type="buy",
            amount=amount,
            status="completed",
            reference=f"BUY-{uuid.uuid4().hex[:10].upper()}"
        )

        Notification.objects.create(
            user=request.user,
            notification_type="transaction",
            title="Asset Purchased",
            message=f"You purchased {quantity:.8f} {asset.symbol} for ${amount}."
        )

        messages.success(
            request,
            f"You successfully purchased {quantity:.8f} {asset.symbol}."
        )

        return redirect("portfolio")

    return render(
        request,
        "buy_asset.html",
        {
            "asset": asset,
            "wallet": wallet,
        }
    )

from decimal import Decimal, InvalidOperation
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

@login_required
def sell_asset(request, asset_id):

    asset = get_object_or_404(
        Asset,
        id=asset_id,
        active=True
    )

    wallet = request.user.wallet

    portfolio = Portfolio.objects.filter(
    user=request.user,
    asset=asset
    ).first()

    if portfolio is None:
        messages.error(
        request,
        "You don't own this asset."
    )
        return redirect("portfolio")

    if request.method == "POST":

        quantity_str = request.POST.get("quantity")

        if not quantity_str:

            messages.error(
                request,
                "Please enter a quantity."
            )

            return redirect(
                "sell_asset",
                asset.id
            )

        try:

            quantity = Decimal(quantity_str)

        except InvalidOperation:

            messages.error(
                request,
                "Invalid quantity."
            )

            return redirect(
                "sell_asset",
                asset.id
            )

        if quantity <= Decimal("0"):

            messages.error(
                request,
                "Quantity must be greater than zero."
            )

            return redirect(
                "sell_asset",
                asset.id
            )

        if quantity > portfolio.quantity:

            messages.error(
                request,
                "You do not own enough of this asset."
            )

            return redirect(
                "sell_asset",
                asset.id
            )

        sale_amount = quantity * asset.current_price

        wallet.balance += sale_amount
        wallet.save()

        portfolio.quantity -= quantity

        if portfolio.quantity == Decimal("0"):

            portfolio.delete()

        else:

            portfolio.save()

        Transaction.objects.create(

            user=request.user,

            transaction_type="sell",

            amount=sale_amount,

            status="completed",

            reference=f"SELL-{uuid.uuid4().hex[:10].upper()}"

        )

        Notification.objects.create(

            user=request.user,

            notification_type="transaction",

            title="Asset Sold",

            message=f"You sold {quantity} {asset.symbol} for ${sale_amount}."

        )

        messages.success(

            request,

            "Asset sold successfully."

        )

        return redirect(
            "portfolio"
        )

    return render(

        request,

        "sell_asset.html",

        {

            "asset": asset,

            "wallet": wallet,

            "portfolio": portfolio,

        }

    )
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def portfolio(request):

    holdings = (
        Portfolio.objects.filter(
            user=request.user
        )
        .select_related("asset")
        .order_by("asset__name")
    )

    total_value = Decimal("0")
    total_cost = Decimal("0")

    for holding in holdings:

        current_price = holding.asset.current_price or Decimal("0")

        holding.current_value = (
            holding.quantity *
            current_price
        )

        holding.invested_value = (
            holding.quantity *
            holding.average_buy_price
        )

        holding.profit_loss = (
            holding.current_value -
            holding.invested_value
        )

        if holding.invested_value > 0:

            holding.profit_percent = (
                holding.profit_loss /
                holding.invested_value
            ) * Decimal("100")

        else:

            holding.profit_percent = Decimal("0")

        total_value += holding.current_value
        total_cost += holding.invested_value

    total_profit_loss = (
        total_value -
        total_cost
    )

    wallet = request.user.wallet

    recent_transactions = (
        Transaction.objects.filter(
            user=request.user
        )
        .select_related("asset")
        .order_by("-created_at")[:10]
    )

    context = {

        "holdings": holdings,

        "wallet": wallet,

        "total_value": total_value,

        "total_cost": total_cost,

        "total_profit_loss": total_profit_loss,

        "recent_transactions": recent_transactions,

    }

    return render(

        request,

        "portfolio.html",

        context,

    )
@login_required
def sell_asset(request, asset_id):

    asset = get_object_or_404(
        Asset,
        id=asset_id,
        active=True
    )

    portfolio = get_object_or_404(
        Portfolio,
        user=request.user,
        asset=asset
    )

    wallet = request.user.wallet


    if request.method == "POST":

        quantity = Decimal(
            request.POST.get("quantity")
        )


        if quantity <= 0:

            messages.error(
                request,
                "Invalid quantity."
            )

            return redirect(
                "asset_detail",
                asset.id
            )


        if portfolio.quantity < quantity:

            messages.error(
                request,
                "You do not own enough of this asset."
            )

            return redirect(
                "asset_detail",
                asset.id
            )


        # Calculate selling value

        amount = (
            quantity *
            asset.current_price
        )


        # Remove asset quantity

        portfolio.quantity -= quantity


        if portfolio.quantity == 0:

            portfolio.delete()

        else:

            portfolio.save()



        # Add money back to wallet

        wallet.balance += amount

        wallet.save()



        # Create transaction

        Transaction.objects.create(

            user=request.user,

            transaction_type="sell",

            amount=amount,

            status="completed",

            reference=f"SELL-{uuid.uuid4().hex[:10].upper()}"

        )



        # Notification

        Notification.objects.create(

            user=request.user,

            title="Asset Sold",

            message=f"You sold {asset.symbol} worth ${amount}."

        )



        # Email

        send_user_email(

            request.user,

            "Asset Sale Completed",

            f"""
Hello {request.user.username},

Your asset sale has been completed.

Asset:
{asset.name}

Quantity:
{quantity}

Amount:
${amount}

Thank you.

"""

        )


        messages.success(

            request,

            "Asset sold successfully."

        )


        return redirect(
            "portfolio"
        )


    return render(

        request,

        "sell_asset.html",

        {

            "asset": asset,

            "portfolio": portfolio,

        }

    )


from django.core.paginator import Paginator

@login_required
def transaction_history(request):

    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by(
        "-created_at"
    )


    transaction_type = request.GET.get(
        "type"
    )


    search = request.GET.get(
        "search"
    )


    if transaction_type:

        transactions = transactions.filter(
            transaction_type=transaction_type
        )


    if search:

        transactions = transactions.filter(
            reference__icontains=search
        )


    paginator = Paginator(
        transactions,
        15
    )


    page_number = request.GET.get(
        "page"
    )


    page_obj = paginator.get_page(
        page_number
    )


    context = {

        "transactions": page_obj,

        "selected_type": transaction_type,

        "search": search,

    }


    return render(

        request,

        "transactions.html",

        context

    )


@login_required
def transaction_detail(request, transaction_id):

    transaction = get_object_or_404(

        Transaction,

        id=transaction_id,

        user=request.user

    )


    return render(

        request,

        "transaction_detail.html",

        {

            "transaction": transaction

        }

    )
from django.db import models
@login_required
def market(request):

    assets = Asset.objects.filter(
        active=True
    )


    asset_type = request.GET.get(
        "type"
    )

    search = request.GET.get(
        "search"
    )


    # Filter by asset type

    if asset_type:

        assets = assets.filter(
            asset_type=asset_type
        )


    # Search assets

    if search:

        assets = assets.filter(

            models.Q(name__icontains=search) |

            models.Q(symbol__icontains=search)

        )


    assets = assets.order_by(
        "name"
    )

    context = {

        "assets": assets,

        "selected_type": asset_type,

        "search": search,

    }


    return render(

        request,

        "market.html",

        context

    )




@login_required
def notifications(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "notifications.html",
        {
            "notifications": notifications,
        },
    )

@login_required
def mark_notification_read(request, pk):

    notification = get_object_or_404(
        Notification,
        id=pk,
        user=request.user
    )

    notification.is_read = True
    notification.save()

    return redirect("notifications")


@login_required
def mark_all_notifications_read(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return redirect("notifications")

@login_required
def wallet(request):

    wallet = request.user.wallet

    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by("-created_at")[:15]

    return render(
        request,
        "wallet.html",
        {
            "wallet": wallet,
            "transactions": transactions,
        },
    )

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from decimal import Decimal

from django.db.models import Q

@login_required
def market(request):

    query = request.GET.get("q")

    assets = Asset.objects.filter(
        active=True
    )

    if query:

        assets = assets.filter(

            Q(name__icontains=query) |

            Q(symbol__icontains=query)

        )

    return render(

        request,

        "market.html",

        {

            "assets": assets,

            "query": query,

        }

    )


from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.shortcuts import render


from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.shortcuts import render

@staff_member_required
def admin_dashboard(request):

    total_users = User.objects.count()

    verified_users = User.objects.filter(
        is_verified=True
    ).count()

    total_assets = Asset.objects.count()

    active_assets = Asset.objects.filter(
        active=True
    ).count()

    total_notifications = Notification.objects.count()

    pending_deposits = Transaction.objects.filter(
        transaction_type="deposit",
        status="pending"
    )

    pending_withdrawals = Transaction.objects.filter(
        transaction_type="withdrawal",
        status="pending"
    )

    completed_deposits = (
        Transaction.objects.filter(
            transaction_type="deposit",
            status="completed"
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )

    completed_withdrawals = (
        Transaction.objects.filter(
            transaction_type="withdrawal",
            status="completed"
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )

    total_investments = (
        Investment.objects.aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0")
    )

    recent_transactions = Transaction.objects.select_related(
        "user",
        "asset"
    ).order_by("-created_at")[:10]

    recent_users = User.objects.order_by(
        "-date_joined"
    )[:10]

    context = {

        "total_users": total_users,

        "verified_users": verified_users,

        "total_assets": total_assets,

        "active_assets": active_assets,

        "completed_deposits": completed_deposits,

        "completed_withdrawals": completed_withdrawals,

        "total_investments": total_investments,

        "pending_deposits": pending_deposits,

        "pending_withdrawals": pending_withdrawals,

        "recent_transactions": recent_transactions,

        "recent_users": recent_users,

        "total_notifications": total_notifications,

    }

    return render(
        request,
        "admin_dashboard.html",
        context
    )

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@staff_member_required
def approve_deposit(request, transaction_id):

    tx = get_object_or_404(
        Transaction,
        id=transaction_id,
        transaction_type="deposit"
    )

    if tx.status != "completed":

        tx.status = "completed"
        tx.save()

        wallet = tx.user.wallet
        wallet.balance += tx.amount
        wallet.total_deposit += tx.amount
        wallet.save()

        Notification.objects.create(
            user=tx.user,
            notification_type="deposit",
            title="Deposit Approved",
            message=f"Your deposit of ${tx.amount} has been approved."
        )

    messages.success(request, "Deposit approved.")

    return redirect("admin_dashboard")

@staff_member_required
def reject_deposit(request, transaction_id):

    tx = get_object_or_404(
        Transaction,
        id=transaction_id,
        transaction_type="deposit"
    )

    tx.status = "failed"
    tx.save()

    Notification.objects.create(
        user=tx.user,
        notification_type="deposit",
        title="Deposit Rejected",
        message=f"Your deposit of ${tx.amount} was rejected."
    )

    messages.success(request, "Deposit rejected.")

    return redirect("admin_dashboard")
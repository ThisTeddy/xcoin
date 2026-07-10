from decimal import Decimal
from datetime import timedelta
import uuid

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, F, DecimalField
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

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


# =====================================
# HELPERS
# =====================================

def generate_reference(prefix="XC"):
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


# =====================================
# LANDING
# =====================================

def landing(request):

    assets = Asset.objects.filter(active=True)[:6]

    plans = InvestmentPlan.objects.filter(active=True)

    return render(
        request,
        "index.html",
        {
            "assets": assets,
            "plans": plans,
        },
    )


# =====================================
# REGISTER
# =====================================

def register(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")

        email = request.POST.get("email")

        password = request.POST.get("password")

        phone = request.POST.get("phone")

        country = request.POST.get("country")

        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return redirect("register")

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password,

            phone=phone,

            country=country,

        )

        login(request, user)

        messages.success(
            request,
            "Welcome to XCoin!"
        )

        return redirect("dashboard")

    return render(
        request,
        "register.html",
    )


# =====================================
# LOGIN
# =====================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        email = request.POST.get("email")

        password = request.POST.get("password")

        user = authenticate(

            request,

            username=email,

            password=password,

        )

        if user:

            login(request, user)

            return redirect("dashboard")

        messages.error(
            request,
            "Invalid login credentials."
        )

    return render(
        request,
        "login.html",
    )


# =====================================
# LOGOUT
# =====================================

@login_required
def logout_view(request):

    logout(request)

    return redirect("landing")


# =====================================
# DASHBOARD
# =====================================

@login_required
def dashboard(request):

    wallet = request.user.wallet

    portfolio = Portfolio.objects.filter(
        user=request.user
    )

    investments = Investment.objects.filter(
        user=request.user,
        status="running",
    )

    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by("-created_at")[:10]

    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False,
    )[:5]

    assets = Asset.objects.filter(
        active=True
    )[:6]

    portfolio_value = Decimal("0")

    for item in portfolio:

        portfolio_value += (
            item.quantity *
            item.asset.current_price
        )

    invested_amount = investments.aggregate(

        total=Sum("amount")

    )["total"] or Decimal("0")

    expected_profit = investments.aggregate(

        total=Sum("expected_profit")

    )["total"] or Decimal("0")

    context = {

        "wallet": wallet,

        "portfolio": portfolio,

        "assets": assets,

        "transactions": transactions,

        "notifications": notifications,

        "investments": investments,

        "portfolio_value": portfolio_value,

        "invested_amount": invested_amount,

        "expected_profit": expected_profit,

    }

    return render(

        request,

        "dashboard.html",

        context,

    )

# =====================================
# MARKET
# =====================================
from django.urls import reverse
@login_required
def market(request):

    assets = Asset.objects.filter(
        active=True
    ).order_by("symbol")

    return render(

        request,

        "market.html",

        {

            "assets": assets,

        },

    )


# =====================================
# PORTFOLIO
# =====================================

@login_required
def portfolio(request):

    portfolio = Portfolio.objects.filter(

        user=request.user

    ).select_related("asset")

    total_value = Decimal("0")

    total_cost = Decimal("0")

    holdings = []

    for item in portfolio:

        current_value = (
            item.quantity *
            item.asset.current_price
        )

        cost = (
            item.quantity *
            item.average_buy_price
        )

        profit = current_value - cost

        total_value += current_value

        total_cost += cost

        holdings.append({

            "holding": item,

            "current_value": current_value,

            "profit": profit,

        })

    context = {

        "holdings": holdings,

        "total_value": total_value,

        "total_profit": total_value - total_cost,

    }

    return render(

        request,

        "portfolio.html",

        context,

    )


# =====================================
# BUY ASSET
# =====================================

@login_required
def buy_asset(request, asset_id):

    asset = get_object_or_404(

        Asset,

        id=asset_id,

        active=True,

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

                "buy_asset",

                asset.id

            )

        if amount <= 0:

            messages.error(

                request,

                "Enter a valid amount."

            )

            return redirect(

                "buy_asset",

                asset.id

            )

        return redirect(

            f"/checkout/?purpose=buy_asset"

            f"&asset={asset.id}"

            f"&amount={amount}"

        )

    return render(

        request,

        "buy_asset.html",

        {

            "asset": asset,

            "wallet": wallet,

        }

    )


# =====================================
# SELL ASSET
# =====================================

@login_required
def sell_asset(request, asset_id):

    asset = get_object_or_404(

        Asset,

        id=asset_id,

        active=True,

    )

    portfolio = get_object_or_404(

        Portfolio,

        user=request.user,

        asset=asset,

    )

    if request.method == "POST":

        try:

            quantity = Decimal(

                request.POST.get("quantity")

            )

        except:

            messages.error(

                request,

                "Invalid quantity."

            )

            return redirect(

                "sell_asset",

                asset.id

            )

        if quantity <= 0:

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

                "Insufficient asset quantity."

            )

            return redirect(

                "sell_asset",

                asset.id

            )

        amount = quantity * asset.current_price

        return redirect(

            f"/checkout/?purpose=sell_asset"

            f"&asset={asset.id}"

            f"&quantity={quantity}"

            f"&amount={amount}"

        )

    return render(

        request,

        "sell_asset.html",

        {

            "asset": asset,

            "portfolio": portfolio,

        }

    )

# =====================================
# INVESTMENT PLANS
# =====================================

@login_required
def investment_plans(request):

    plans = InvestmentPlan.objects.filter(
        active=True
    )

    return render(

        request,

        "investments.html",

        {

            "plans": plans,

        }

    )


# =====================================
# INVEST
# =====================================

@login_required
def invest(request, plan_id):

    plan = get_object_or_404(

        InvestmentPlan,

        id=plan_id,

        active=True,

    )

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
                f"Minimum investment is ${plan.minimum_amount}"
            )

            return redirect(
                "invest",
                plan.id
            )

        if amount > plan.maximum_amount:

            messages.error(
                request,
                f"Maximum investment is ${plan.maximum_amount}"
            )

            return redirect(
                "invest",
                plan.id
            )

        checkout_url = reverse("checkout")

        return redirect(

            f"{checkout_url}"

            f"?purpose=investment"

            f"&plan={plan.id}"

            f"&amount={amount}"

        )

    return render(

        request,

        "invest.html",

        {

            "plan": plan,

        }

    )


# =====================================
# CHECKOUT
# =====================================

@login_required
@transaction.atomic
def checkout(request):

    purpose = request.GET.get("purpose")

    amount = Decimal(
        request.GET.get("amount", "0")
    )

    metadata = {}

    if request.GET.get("asset"):

        metadata["asset_id"] = request.GET.get("asset")

    if request.GET.get("plan"):

        metadata["plan_id"] = request.GET.get("plan")

    if request.GET.get("quantity"):

        metadata["quantity"] = request.GET.get("quantity")

    wallet = request.user.wallet

    asset = None
    plan = None

    if "asset_id" in metadata:

        asset = get_object_or_404(

            Asset,

            id=metadata["asset_id"]

        )

    if "plan_id" in metadata:

        plan = get_object_or_404(

            InvestmentPlan,

            id=metadata["plan_id"]

        )

    deposit_wallet = DepositWallet.objects.filter(
        active=True
    ).first()

    if request.method == "POST":

        method = request.POST.get("method")

        payment = Payment.objects.create(

            user=request.user,

            amount=amount,

            purpose=purpose,

            method=method,

            metadata=metadata,

            reference=generate_reference(),

        )

        if method != "wallet":

            messages.success(

                request,

                "Payment submitted successfully."

            )

            return redirect(
                "transactions"
            )

        if wallet.balance < amount:

            messages.error(

                request,

                "Insufficient wallet balance."

            )

            return redirect(
                "dashboard"
            )

        wallet.balance -= amount
        wallet.save()

        # BUY

        if purpose == "buy_asset":

            qty = amount / asset.current_price

            portfolio, created = Portfolio.objects.get_or_create(

                user=request.user,

                asset=asset,

                defaults={

                    "quantity": Decimal("0"),

                    "average_buy_price": asset.current_price,

                }

            )

            if created:

                portfolio.quantity = qty

            else:

                total_cost = (

                    portfolio.quantity *
                    portfolio.average_buy_price

                ) + amount

                new_qty = portfolio.quantity + qty

                portfolio.average_buy_price = (
                    total_cost / new_qty
                )

                portfolio.quantity = new_qty

            portfolio.save()

            tx_type = "buy"

        # INVESTMENT

        elif purpose == "investment":

            expected_profit = (

                amount *
                plan.roi_percent

            ) / Decimal("100")

            Investment.objects.create(

                user=request.user,

                plan=plan,

                amount=amount,

                expected_profit=expected_profit,

                end_date=timezone.now() +
                timedelta(days=plan.duration_days),

            )

            tx_type = "investment"

        # SELL

        elif purpose == "sell_asset":

            qty = Decimal(
                metadata["quantity"]
            )

            portfolio = get_object_or_404(

                Portfolio,

                user=request.user,

                asset=asset,

            )

            portfolio.quantity -= qty

            if portfolio.quantity <= 0:

                portfolio.delete()

            else:

                portfolio.save()

            wallet.balance += amount
            wallet.save()

            tx_type = "sell"

        else:

            tx_type = "deposit"

        payment.status = "completed"
        payment.save()

        Transaction.objects.create(

            user=request.user,

            transaction_type=tx_type,

            amount=amount,

            reference=payment.reference,

        )

        Notification.objects.create(

            user=request.user,

            title="Transaction Successful",

            message=f"{purpose.replace('_',' ').title()} completed successfully."

        )

        messages.success(

            request,

            "Transaction completed successfully."

        )

        return redirect(
            "dashboard"
        )

    return render(

        request,

        "checkout.html",

        {

            "purpose": purpose,

            "amount": amount,

            "wallet": wallet,

            "asset": asset,

            "plan": plan,

            "deposit_wallet": deposit_wallet,

            "quantity": metadata.get("quantity"),

        }

    )


# =====================================
# DEPOSIT
# =====================================

@login_required
def deposit(request):

    wallets = DepositWallet.objects.filter(
        active=True
    )

    return render(
        request,
        "deposit.html",
        {
            "wallets": wallets,
        }
    )


# =====================================
# WITHDRAW
# =====================================

@login_required
def withdraw(request):

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
            return redirect("withdraw")

        address = request.POST.get(
            "wallet_address"
        )

        network = request.POST.get(
            "network"
        )

        settings = SiteSettings.objects.first()

        if settings and amount < settings.minimum_withdrawal:

            messages.error(
                request,
                f"Minimum withdrawal is ${settings.minimum_withdrawal}"
            )

            return redirect("withdraw")

        if amount > wallet.balance:

            messages.error(
                request,
                "Insufficient balance."
            )

            return redirect("withdraw")

        wallet.balance -= amount
        wallet.save()

        payment = Payment.objects.create(

            user=request.user,

            amount=amount,

            purpose="withdrawal",

            method="crypto",

            status="pending",

            reference=generate_reference(),

            metadata={
                "network": network,
                "wallet_address": address,
            }

        )

        Transaction.objects.create(

            user=request.user,

            transaction_type="withdrawal",

            amount=amount,

            status="pending",

            reference=payment.reference,

        )

        Notification.objects.create(

            user=request.user,

            title="Withdrawal Requested",

            message="Your withdrawal request has been submitted."

        )

        messages.success(
            request,
            "Withdrawal request submitted."
        )

        return redirect(
            "transactions"
        )

    return render(

        request,

        "withdraw.html",

        {

            "wallet": wallet,

        }

    )


# =====================================
# TRANSACTIONS
# =====================================

@login_required
def transactions(request):

    transactions = Transaction.objects.filter(

        user=request.user

    ).order_by(

        "-created_at"

    )

    return render(

        request,

        "transactions.html",

        {

            "transactions": transactions,

        }

    )


# =====================================
# NOTIFICATIONS
# =====================================

@login_required
def notifications(request):

    notifications = Notification.objects.filter(

        user=request.user

    ).order_by(

        "-created_at"

    )

    Notification.objects.filter(

        user=request.user,

        is_read=False

    ).update(

        is_read=True

    )

    return render(

        request,

        "notifications.html",

        {

            "notifications": notifications,

        }

    )


# =====================================
# PROFILE
# =====================================

@login_required
def profile(request):

    if request.method == "POST":

        request.user.username = request.POST.get(
            "username"
        )

        request.user.phone = request.POST.get(
            "phone"
        )

        request.user.country = request.POST.get(
            "country"
        )

        if request.FILES.get("avatar"):

            request.user.avatar = request.FILES.get(
                "avatar"
            )

        request.user.save()

        messages.success(

            request,

            "Profile updated successfully."

        )

        return redirect(
            "profile"
        )

    return render(

        request,

        "profile.html",

        {

            "user": request.user,

        }

    )


# =====================================
# SETTINGS
# =====================================

@login_required
def settings(request):

    site = SiteSettings.objects.first()

    return render(

        request,

        "settings.html",

        {

            "site": site,

        }

    )

@login_required
def asset_detail(request, asset_id):

    asset = get_object_or_404(
        Asset,
        id=asset_id,
        active=True,
    )

    return render(
        request,
        "asset_detail.html",
        {
            "asset": asset,
        },
    )
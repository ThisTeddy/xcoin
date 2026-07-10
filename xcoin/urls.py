from django.urls import path
from . import views

urlpatterns = [

    path("", views.landing, name="landing"),

    path("register/", views.register, name="register"),

    path("login/", views.login_view, name="login"),

    path("logout/", views.logout_view, name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("market/", views.market, name="market"),

    path("portfolio/", views.portfolio, name="portfolio"),

    path("buy/<int:asset_id>/", views.buy_asset, name="buy_asset"),

    path("sell/<int:asset_id>/", views.sell_asset, name="sell_asset"),

    path("plans/", views.investment_plans, name="investment_plans"),

    path("invest/<int:plan_id>/", views.invest, name="invest"),

    path("checkout/", views.checkout, name="checkout"),

    path("deposit/", views.deposit, name="deposit"),

    path("withdraw/", views.withdraw, name="withdraw"),

    path("transactions/", views.transactions, name="transactions"),

    path("notifications/", views.notifications, name="notifications"),

    path("profile/", views.profile, name="profile"),

    path("settings/", views.settings, name="settings"),
    path(
    "asset/<int:asset_id>/",
    views.asset_detail,
    name="asset_detail",
),

]
from django.urls import path

from . import views


urlpatterns = [


    # ==================================
    # PUBLIC PAGES
    # ==================================

    path(
        "",
        views.home,
        name="home"
    ),
    path("about/", views.about, name="about"),
path("careers/", views.careers, name="careers"),
path("contact/", views.contact, name="contact"),
path("blog/", views.blog, name="blog"),
path("legal/", views.legal, name="legal"),
path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
path("terms-of-service/", views.terms_of_service, name="terms_of_service"),
path("risk-disclosure/", views.risk_disclosure, name="risk_disclosure"),
    path(
        "about/",
        views.about,
        name="about"
    ),
    path(
    "kyc/",
    views.kyc,
    name="kyc",
),

    path(
        "contact/",
        views.contact,
        name="contact"
    ),

    path(
        "help/",
        views.help_center,
        name="help_center"
    ),

    path(
        "faq/",
        views.faq,
        name="faq"
    ),

    path(
        "privacy-policy/",
        views.privacy_policy,
        name="privacy_policy"
    ),

    path(
        "terms/",
        views.terms_and_conditions,
        name="terms_and_conditions"
    ),



    # ==================================
    # AUTHENTICATION
    # ==================================

    path(
        "register/",
        views.register,
        name="register"
    ),
    path(
    "notifications/",
    views.notifications,
    name="notifications",
    ),

    path(
        "notifications/read/<int:pk>/",
        views.mark_notification_read,
        name="mark_notification_read",
    ),

    path(
        "notifications/read-all/",
        views.mark_all_notifications_read,
        name="mark_all_notifications_read",
    ),
    path(
        "sell/<int:asset_id>/",
        views.sell_asset,
        name="sell_asset",
    ),
    path(
    "wallet/",
    views.wallet,
    name="wallet",
    ),
    path(
    "admin-dashboard/",
    views.admin_dashboard,
    name="admin_dashboard",
    ),
    path(
    "approve-deposit/<int:transaction_id>/",
    views.approve_deposit,
    name="approve_deposit",
),

path(
    "reject-deposit/<int:transaction_id>/",
    views.reject_deposit,
    name="reject_deposit",
),
    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "forgot-password/",
        views.forgot_password,
        name="forgot_password"
    ),

    path(
        "reset-password/<uidb64>/<token>/",
        views.reset_password,
        name="reset_password"
    ),

    path(
        "change-password/",
        views.change_password,
        name="change_password"
    ),



    # ==================================
    # DASHBOARD
    # ==================================

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),



    # ==================================
    # MARKET
    # ==================================

    path(
        "market/",
        views.market,
        name="market"
    ),

    path(
        "asset/<int:pk>/",
        views.asset_detail,
        name="asset_detail"
    ),



    # ==================================
    # TRADING
    # ==================================

    path(
        "buy/<int:asset_id>/",
        views.buy_asset,
        name="buy_asset"
    ),

    path(
        "sell/<int:asset_id>/",
        views.sell_asset,
        name="sell_asset"
    ),

    path(
        "portfolio/",
        views.portfolio,
        name="portfolio"
    ),



    # ==================================
    # INVESTMENT
    # ==================================

    path(
        "investment-plans/",
        views.investment_plans,
        name="investment_plans"
    ),

    path(
        "invest/<int:plan_id>/",
        views.invest,
        name="invest"
    ),

    path(
        "my-investments/",
        views.my_investments,
        name="my_investments"
    ),

    path(
        "investment/<int:investment_id>/",
        views.investment_detail,
        name="investment_detail"
    ),



    # ==================================
    # PAYMENTS
    # ==================================

    path(
        "deposit/",
        views.deposit,
        name="deposit"
    ),

    path(
        "withdraw/",
        views.withdraw,
        name="withdraw"
    ),

    path(
        "payments/",
        views.payment_history,
        name="payment_history"
    ),

    path(
        "payments/<int:payment_id>/",
        views.payment_detail,
        name="payment_detail"
    ),



    # ==================================
    # TRANSACTIONS
    # ==================================

    path(
        "transactions/",
        views.transaction_history,
        name="transaction_history"
    ),

    path(
        "transactions/<int:transaction_id>/",
        views.transaction_detail,
        name="transaction_detail"
    ),



    # ==================================
    # PROFILE
    # ==================================

    path(
        "profile/",
        views.profile,
        name="profile"
    ),

    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile"
    ),

    path(
        "settings/",
        views.account_settings,
        name="account_settings"
    ),



    # ==================================
    # NOTIFICATIONS
    # ==================================

    path(
        "notifications/",
        views.notifications,
        name="notifications"
    ),

    path(
        "notifications/<int:notification_id>/",
        views.notification_detail,
        name="notification_detail"
    ),

    path(
        "notifications/read-all/",
        views.mark_notifications_read,
        name="mark_notifications_read"
    ),

]
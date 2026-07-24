from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from xcoin.models import (
    Asset,
    InvestmentPlan,
    DepositWallet,
    SiteSettings,
    EmailTemplate,
)


class Command(BaseCommand):
    help = "Seed XCoin demo data"

    @transaction.atomic
    def handle(self, *args, **kwargs):

        self.stdout.write("Seeding assets...")

        assets = [
            ("Bitcoin", "BTC", "crypto", 118450, 2.54),
            ("Ethereum", "ETH", "crypto", 4850, 1.82),
            ("BNB", "BNB", "crypto", 812, 2.11),
            ("Solana", "SOL", "crypto", 215, 4.12),
            ("XRP", "XRP", "crypto", 3.14, 1.71),
            ("Cardano", "ADA", "crypto", 1.28, -0.42),
            ("Dogecoin", "DOGE", "crypto", 0.39, 0.85),
            ("TRON", "TRX", "crypto", 0.41, 0.72),
            ("Avalanche", "AVAX", "crypto", 51, 2.40),
            ("Chainlink", "LINK", "crypto", 28, 1.60),
            ("Litecoin", "LTC", "crypto", 134, 1.90),
("Polkadot", "DOT", "crypto", 9.20, -0.61),
("Polygon", "POL", "crypto", 0.74, 0.82),
("Sui", "SUI", "crypto", 2.80, 4.10),
("Toncoin", "TON", "crypto", 8.10, 2.82),
("Stellar", "XLM", "crypto", 0.62, 0.44),
("Cosmos", "ATOM", "crypto", 8.90, -0.31),
("Near Protocol", "NEAR", "crypto", 5.70, 1.52),
("Aptos", "APT", "crypto", 11.40, 2.17),
("Shiba Inu", "SHIB", "crypto", 0.000025, 3.42),
("Pepe", "PEPE", "crypto", 0.000013, 5.10),
("Uniswap", "UNI", "crypto", 14.30, 1.60),
("Arbitrum", "ARB", "crypto", 1.21, -0.25),
("Optimism", "OP", "crypto", 2.45, 0.91),
("Internet Computer", "ICP", "crypto", 12.50, 1.84),
("Apple", "AAPL", "stock", 229, 0.81),
("Microsoft", "MSFT", "stock", 535, 0.72),
("NVIDIA", "NVDA", "stock", 184, 2.61),
("Tesla", "TSLA", "stock", 345, 1.35),
("Amazon", "AMZN", "stock", 242, 0.52),
("Meta", "META", "stock", 768, 1.72),
("Alphabet", "GOOGL", "stock", 191, 0.33),
("Netflix", "NFLX", "stock", 1440, 0.91),
("AMD", "AMD", "stock", 177, -0.43),
("Intel", "INTC", "stock", 25, -0.84),
("Oracle", "ORCL", "stock", 231, 0.65),
("Adobe", "ADBE", "stock", 498, 1.04),
("Salesforce", "CRM", "stock", 310, 0.74),
("Uber", "UBER", "stock", 92, 2.21),
("Palantir", "PLTR", "stock", 160, 3.42),
("Gold", "XAU", "commodity", 3412, 0.44),
("Silver", "XAG", "commodity", 38.60, 0.55),
("Crude Oil", "OIL", "commodity", 72, -0.22),
("Natural Gas", "NGAS", "commodity", 3.70, 1.14),
("Platinum", "PLAT", "commodity", 1425, 0.82),
("Copper", "COPPER", "commodity", 5.30, 0.33),
            ("EUR/USD", "EURUSD", "forex", 1.17, 0.12),
("GBP/USD", "GBPUSD", "forex", 1.36, -0.15),
("USD/JPY", "USDJPY", "forex", 149.50, 0.30),
("AUD/USD", "AUDUSD", "forex", 0.67, 0.11),
("USD/CAD", "USDCAD", "forex", 1.37, -0.10),
("USD/CHF", "USDCHF", "forex", 0.81, 0.08),
("NZD/USD", "NZDUSD", "forex", 0.61, -0.12),
("S&P 500 ETF", "SPY", "etf", 645, 0.61),
("Nasdaq ETF", "QQQ", "etf", 572, 0.74),
("Dow Jones ETF", "DIA", "etf", 451, 0.42),
("Vanguard S&P 500", "VOO", "etf", 593, 0.55),
("iShares Core S&P 500", "IVV", "etf", 596, 0.57),
("ARK Innovation ETF", "ARKK", "etf", 78, 1.62),
("S&P 500", "SPX", "index", 6490, 0.48),
("NASDAQ 100", "NDX", "index", 23800, 0.74),
("Dow Jones", "DJI", "index", 45200, 0.41),
("FTSE 100", "FTSE", "index", 9140, 0.22),
("Nikkei 225", "N225", "index", 42200, 0.61),
        ]

        for i, (name, symbol, asset_type, price, change) in enumerate(assets, start=1):

            Asset.objects.update_or_create(
                symbol=symbol,
                defaults={
                    "name": name,
                    "asset_type": asset_type,
                    "current_price": Decimal(str(price)),
                    "market_cap": Decimal("1000000000"),
                    "volume_24h": Decimal("50000000"),
                    "circulating_supply": Decimal("1000000"),
                    "high_24h": Decimal(str(price * 1.02)),
                    "low_24h": Decimal(str(price * 0.98)),
                    "ath": Decimal(str(price * 1.5)),
                    "atl": Decimal("0.01"),
                    "change": Decimal(str(change)),
                    "featured": i <= 5,
                    "rank": i,
                    "active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("✓ Assets seeded"))

        plans = [
            ("Starter", 100, 999, 15, 7),
            ("Bronze", 1000, 4999, 25, 14),
            ("Silver", 5000, 9999, 35, 21),
            ("Gold", 10000, 49999, 45, 30),
            ("VIP", 50000, 1000000, 60, 45),
        ]

        for name, minimum, maximum, roi, days in plans:

            InvestmentPlan.objects.update_or_create(
                name=name,
                defaults={
                    "description": f"{name} Investment Plan",
                    "plan_type": "fixed",
                    "minimum_amount": minimum,
                    "maximum_amount": maximum,
                    "roi_percent": roi,
                    "duration_days": days,
                    "featured": name in ["Starter", "Gold", "VIP"],
                    "active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("✓ Investment plans seeded"))

        wallets = [
            ("BTC", "bc1qxxxxxxxxxxxxxxxxxxxxxxxx"),
            ("ETH", "0x1234567890abcdef1234567890abcdef12345678"),
            ("USDT_TRC20", "TRxxxxxxxxxxxxxxxxxxxxxxxxxxxx"),
            ("USDT_ERC20", "0xabcdefabcdefabcdefabcdefabcdef"),
            ("BNB", "0xbnbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"),
        ]

        for network, address in wallets:

            DepositWallet.objects.update_or_create(
                network=network,
                defaults={
                    "wallet_address": address,
                    "active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("✓ Deposit wallets seeded"))

        SiteSettings.objects.update_or_create(
            pk=1,
            defaults={
                "site_name": "XCoin",
                "support_email": "support@xcoin.com",
                "support_phone": "+1 800 555 1000",
                "minimum_deposit": Decimal("50"),
                "minimum_withdrawal": Decimal("100"),
                "maintenance_mode": False,
            },
        )

        self.stdout.write(self.style.SUCCESS("✓ Site settings seeded"))

        templates = [
            ("welcome", "Welcome to XCoin"),
            ("deposit", "Deposit Approved"),
            ("withdrawal", "Withdrawal Approved"),
            ("investment", "Investment Started"),
        ]

        for name, subject in templates:

            EmailTemplate.objects.update_or_create(
                name=name,
                defaults={
                    "subject": subject,
                    "html_body": f"<h2>{subject}</h2>",
                    "text_body": subject,
                    "active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("✓ Email templates seeded"))

        self.stdout.write(
            self.style.SUCCESS(
                "\n🎉 XCoin demo data created successfully!"
            )
        )


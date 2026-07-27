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

    help = "Seed XCoin demo data."

    @transaction.atomic
    def handle(self, *args, **kwargs):

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("SEEDING XCOIN DATABASE"))
        self.stdout.write("=" * 60)

        self.seed_assets()

        self.seed_investment_plans()

        self.seed_deposit_wallets()

        self.seed_site_settings()

        self.seed_email_templates()

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "✓ XCoin database seeded successfully."
            )
        )
        self.stdout.write("=" * 60)

    def seed_assets(self):

        self.stdout.write("")
        self.stdout.write("Seeding Assets...")

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

            ("SPDR S&P 500 ETF", "SPY", "etf", 645, 0.61),
            ("Invesco QQQ Trust", "QQQ", "etf", 572, 0.74),
            ("SPDR Dow Jones ETF", "DIA", "etf", 451, 0.42),
            ("Vanguard S&P 500 ETF", "VOO", "etf", 593, 0.55),
            ("iShares Core S&P 500 ETF", "IVV", "etf", 596, 0.57),
            ("ARK Innovation ETF", "ARKK", "etf", 78, 1.62),

            ("S&P 500", "SPX", "index", 6490, 0.48),
            ("NASDAQ 100", "NDX", "index", 23800, 0.74),
            ("Dow Jones", "DJI", "index", 45200, 0.41),
            ("FTSE 100", "FTSE", "index", 9140, 0.22),
            ("Nikkei 225", "N225", "index", 42200, 0.61),

        ]

        for rank, (name, symbol, asset_type, price, change) in enumerate(assets, start=1):

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
                    "ath": Decimal(str(price * 1.50)),
                    "atl": Decimal("0.01"),
                    "change": Decimal(str(change)),
                    "featured": rank <= 10,
                    "rank": rank,
                    "active": True,

                }

            )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ {len(assets)} Assets Seeded"
            )
        )

    def seed_investment_plans(self):

        self.stdout.write("")
        self.stdout.write("Seeding Investment Plans...")

        plans = [

            ("Starter", "Perfect for beginners.", 100, 999, 8, 1),
            ("Bronze", "Short-term investment plan.", 1000, 4999, 12, 7),
            ("Silver", "Medium-term investment plan.", 5000, 19999, 18, 14),
            ("Gold", "High-return investment plan.", 20000, 49999, 24, 21),
            ("Platinum", "Premium investment plan.", 50000, 99999, 32, 30),
            ("Diamond", "Elite investment plan.", 100000, 10000000, 45, 60),

        ]

        for order, (
            name,
            description,
            minimum,
            maximum,
            roi,
            duration,
        ) in enumerate(plans, start=1):

            InvestmentPlan.objects.update_or_create(

                name=name,

                defaults={

                    "description": description,
                    "plan_type": "fixed",
                    "minimum_amount": Decimal(str(minimum)),
                    "maximum_amount": Decimal(str(maximum)),
                    "roi_percent": Decimal(str(roi)),
                    "duration_days": duration,
                    "featured": order >= 4,
                    "active": True,

                }

            )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ {len(plans)} Investment Plans Seeded"
            )
        )

    def seed_deposit_wallets(self):

        self.stdout.write("")
        self.stdout.write("Seeding Deposit Wallets...")

        wallets = [

            ("BTC", "BTC", ""),
            ("ETH", "ETH", ""),
            ("USDT_TRC20", "ETH", ""),
            ("USDT_ERC20", "ETH", ""),
            ("USDT_BEP20", "BNB", ""),
            ("BNB", "BNB", ""),
            ("SOL", "SOL", ""),
            ("LTC", "LTC", ""),
            ("DOGE", "DOGE", ""),

        ]

        for network, symbol, address in wallets:

            asset = Asset.objects.get(symbol=symbol)

            DepositWallet.objects.update_or_create(

                network=network,

                defaults={

                    "asset": asset,
                    "wallet_address": address,
                    "active": True,

                }

            )

        self.stdout.write(
        self.style.SUCCESS(
            "✓ Deposit Wallets Seeded"
        )    )

    def seed_site_settings(self):

        self.stdout.write("")
        self.stdout.write("Seeding Site Settings...")

        SiteSettings.objects.update_or_create(

            pk=1,

            defaults={

                "site_name": "XCoin",
                "support_email": "support@xcoin.com",
                "support_phone": "+1 (800) 555-1000",
                "minimum_deposit": Decimal("50"),
                "minimum_withdrawal": Decimal("100"),
                "maintenance_mode": False,

            }

        )

        self.stdout.write(
        self.style.SUCCESS(
            "✓ Site Settings Seeded"
        )
    )

    def seed_email_templates(self):

        self.stdout.write("")
        self.stdout.write("Seeding Email Templates...")

        templates = [

            ("welcome", "Welcome to XCoin"),
            ("deposit", "Deposit Received"),
            ("withdrawal", "Withdrawal Processed"),
            ("investment", "Investment Activated"),
            ("kyc", "KYC Verification"),
            ("password_reset", "Password Reset"),
            ("email_verification", "Verify Your Email"),

        ]

        for name, subject in templates:

            EmailTemplate.objects.update_or_create(

            name=name,

            defaults={

                "subject": subject,
                "html_body": f"<h2>{subject}</h2>",
                "text_body": subject,
                "active": True,

            }

        )

        self.stdout.write(
        self.style.SUCCESS(
            f"✓ {len(templates)} Email Templates Seeded"
        )
    )
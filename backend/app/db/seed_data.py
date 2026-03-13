"""Seed data for the database. Randomly generated for scalability."""

import logging
import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.core.config import get_settings
from app.core.security import hash_password
from app.models import (
    Company,
    ExchangeListing,
    Industry,
    QuarterlyResult,
    Sector,
    User,
    UserRole,
    UserStatus,
)

logger = logging.getLogger(__name__)

SECTORS_DATA = [
    {"sector_id": 1, "sector_name": "GENERAL INDUSTRIALS"},
    {"sector_id": 2, "sector_name": "CEMENT AND CONSTRUCTION"},
    {"sector_id": 3, "sector_name": "METALS & MINING"},
    {"sector_id": 4, "sector_name": "BANKING AND FINANCE"},
    {"sector_id": 5, "sector_name": "TRANSPORTATION"},
    {"sector_id": 6, "sector_name": "UTILITIES"},
    {"sector_id": 7, "sector_name": "RETAILING"},
    {"sector_id": 8, "sector_name": "OIL & GAS"},
    {"sector_id": 9, "sector_name": "PHARMACEUTICALS & BIOTECHNOLOGY"},
    {"sector_id": 10, "sector_name": "AUTOMOBILES & AUTO COMPONENTS"},
    {"sector_id": 11, "sector_name": "DIVERSIFIED CONSUMER SERVICES"},
    {"sector_id": 12, "sector_name": "CHEMICALS & PETROCHEMICALS"},
    {"sector_id": 13, "sector_name": "FOOD BEVERAGES & TOBACCO"},
    {"sector_id": 14, "sector_name": "DIVERSIFIED"},
    {"sector_id": 15, "sector_name": "TELECOM SERVICES"},
    {"sector_id": 16, "sector_name": "CONSUMER DURABLES"},
    {"sector_id": 17, "sector_name": "REALTY"},
    {"sector_id": 18, "sector_name": "FMCG"},
    {"sector_id": 19, "sector_name": "FOREST MATERIALS"},
    {"sector_id": 20, "sector_name": "FERTILIZERS"},
    {"sector_id": 21, "sector_name": "COMMERCIAL SERVICES & SUPPLIES"},
    {"sector_id": 22, "sector_name": "SOFTWARE & SERVICES"},
    {"sector_id": 23, "sector_name": "TELECOMMUNICATIONS EQUIPMENT"},
    {"sector_id": 24, "sector_name": "HOTELS RESTAURANTS & TOURISM"},
    {"sector_id": 25, "sector_name": "TEXTILES APPARELS & ACCESSORIES"},
    {"sector_id": 26, "sector_name": "MEDIA"},
    {"sector_id": 27, "sector_name": "OTHERS"},
    {"sector_id": 28, "sector_name": "HEALTHCARE EQUIPMENT & SUPPLIES"},
]

INDUSTRIES_DATA = [
    {"industry_id": 1, "industry_name": "INDUSTRIAL MACHINERY", "sector_id": 1},
    {"industry_id": 2, "industry_name": "CEMENT & CEMENT PRODUCTS", "sector_id": 2},
    {"industry_id": 3, "industry_name": "OTHER INDUSTRIAL GOODS", "sector_id": 1},
    {"industry_id": 4, "industry_name": "IRON & STEEL PRODUCTS", "sector_id": 3},
    {"industry_id": 5, "industry_name": "BANKS", "sector_id": 4},
    {"industry_id": 6, "industry_name": "MARINE PORT & SERVICES", "sector_id": 5},
    {"industry_id": 7, "industry_name": "ELECTRIC UTILITIES", "sector_id": 6},
    {"industry_id": 8, "industry_name": "DEPARTMENT STORES", "sector_id": 7},
    {"industry_id": 9, "industry_name": "OIL MARKETING & DISTRIBUTION", "sector_id": 8},
    {"industry_id": 10, "industry_name": "PHARMACEUTICALS", "sector_id": 9},
    {"industry_id": 11, "industry_name": "AUTO PARTS & EQUIPMENT", "sector_id": 10},
    {"industry_id": 12, "industry_name": "HEALTHCARE FACILITIES", "sector_id": 11},
    {"industry_id": 13, "industry_name": "AUTO TYRES & RUBBER PRODUCTS", "sector_id": 10},
    {"industry_id": 14, "industry_name": "COMMERCIAL VEHICLES", "sector_id": 10},
    {"industry_id": 15, "industry_name": "FURNITURE-FURNISHING-PAINTS", "sector_id": 11},
    {"industry_id": 16, "industry_name": "PLASTIC PRODUCTS", "sector_id": 1},
    {"industry_id": 17, "industry_name": "SPECIALTY CHEMICALS", "sector_id": 12},
    {"industry_id": 18, "industry_name": "OTHER FOOD PRODUCTS", "sector_id": 13},
    {"industry_id": 19, "industry_name": "2/3 WHEELERS", "sector_id": 10},
    {"industry_id": 20, "industry_name": "FINANCE (INCLUDING NBFCS)", "sector_id": 4},
    {"industry_id": 21, "industry_name": "HOLDING COMPANIES", "sector_id": 14},
    {"industry_id": 22, "industry_name": "SUGAR", "sector_id": 13},
    {"industry_id": 23, "industry_name": "FOOTWEAR", "sector_id": 7},
    {"industry_id": 24, "industry_name": "DEFENCE", "sector_id": 1},
    {"industry_id": 25, "industry_name": "OTHER INDUSTRIAL PRODUCTS", "sector_id": 1},
    {"industry_id": 26, "industry_name": "HEAVY ELECTRICAL EQUIPMENT", "sector_id": 1},
    {"industry_id": 27, "industry_name": "REFINERIES/PETRO-PRODUCTS", "sector_id": 8},
    {"industry_id": 28, "industry_name": "TELECOM SERVICES", "sector_id": 15},
    {"industry_id": 29, "industry_name": "OTHER TELECOM SERVICES", "sector_id": 15},
    {"industry_id": 30, "industry_name": "BIOTECHNOLOGY", "sector_id": 9},
    {"industry_id": 31, "industry_name": "TRANSPORTATION - LOGISTICS", "sector_id": 5},
    {"industry_id": 32, "industry_name": "CONSUMER ELECTRONICS", "sector_id": 16},
    {"industry_id": 33, "industry_name": "TEA & COFFEE", "sector_id": 13},
    {"industry_id": 34, "industry_name": "REALTY", "sector_id": 17},
    {"industry_id": 35, "industry_name": "PACKAGED FOODS", "sector_id": 18},
    {"industry_id": 36, "industry_name": "OTHER FINANCIAL SERVICES", "sector_id": 4},
    {"industry_id": 37, "industry_name": "HOUSING FINANCE", "sector_id": 4},
    {"industry_id": 38, "industry_name": "FOREST PRODUCTS", "sector_id": 19},
    {"industry_id": 39, "industry_name": "FERTILIZERS", "sector_id": 20},
    {"industry_id": 40, "industry_name": "COAL", "sector_id": 3},
    {"industry_id": 41, "industry_name": "PERSONAL PRODUCTS", "sector_id": 18},
    {"industry_id": 42, "industry_name": "WAREHOUSING AND LOGISTICS", "sector_id": 21},
    {"industry_id": 43, "industry_name": "HOUSEHOLD APPLIANCES", "sector_id": 16},
    {"industry_id": 44, "industry_name": "IT CONSULTING & SOFTWARE", "sector_id": 22},
    {"industry_id": 45, "industry_name": "MISC. COMMERCIAL SERVICES", "sector_id": 21},
    {"industry_id": 46, "industry_name": "HEALTHCARE SERVICES", "sector_id": 11},
    {"industry_id": 47, "industry_name": "CONSULTING SERVICES", "sector_id": 21},
    {"industry_id": 48, "industry_name": "OTHER ELECTRICAL EQUIPMENT/PRODUCTS", "sector_id": 16},
    {"industry_id": 49, "industry_name": "BPO/KPO", "sector_id": 22},
    {"industry_id": 50, "industry_name": "UTILITIES", "sector_id": 6},
    {"industry_id": 51, "industry_name": "DIVERSIFIED", "sector_id": 14},
    {"industry_id": 52, "industry_name": "SHIPPING", "sector_id": 5},
    {"industry_id": 53, "industry_name": "COMMODITY CHEMICALS", "sector_id": 12},
    {"industry_id": 54, "industry_name": "TELECOM CABLES", "sector_id": 23},
    {"industry_id": 55, "industry_name": "ALUMINIUM AND ALUMINIUM PRODUCTS", "sector_id": 3},
    {"industry_id": 56, "industry_name": "COPPER", "sector_id": 3},
    {"industry_id": 57, "industry_name": "ZINC", "sector_id": 3},
    {"industry_id": 58, "industry_name": "CIGARETTES-TOBACCO PRODUCTS", "sector_id": 13},
    {"industry_id": 59, "industry_name": "LIFE INSURANCE", "sector_id": 4},
    {"industry_id": 60, "industry_name": "ROADS & HIGHWAYS", "sector_id": 2},
    {"industry_id": 61, "industry_name": "TELECOM EQUIPMENT", "sector_id": 23},
    {"industry_id": 62, "industry_name": "HOTELS", "sector_id": 24},
    {"industry_id": 63, "industry_name": "INTERNET SOFTWARE & SERVICES", "sector_id": 22},
    {"industry_id": 64, "industry_name": "AIRLINES", "sector_id": 5},
    {"industry_id": 65, "industry_name": "IRON & STEEL/INTERM.PRODUCTS", "sector_id": 3},
    {"industry_id": 66, "industry_name": "RESTAURANTS", "sector_id": 24},
    {"industry_id": 67, "industry_name": "COMMODITY TRADING & DISTRIBUTION", "sector_id": 21},
    {"industry_id": 68, "industry_name": "CARS & UTILITY VEHICLES", "sector_id": 10},
    {"industry_id": 69, "industry_name": "CONSTRUCTION & ENGINEERING", "sector_id": 2},
    {"industry_id": 70, "industry_name": "EXPLORATION & PRODUCTION", "sector_id": 8},
    {"industry_id": 71, "industry_name": "AGROCHEMICALS", "sector_id": 12},
    {"industry_id": 72, "industry_name": "SPECIALTY RETAIL", "sector_id": 7},
    {"industry_id": 73, "industry_name": "OTHER APPARELS & ACCESSORIES", "sector_id": 25},
    {"industry_id": 74, "industry_name": "BREWERIES & DISTILLERIES", "sector_id": 13},
    {"industry_id": 75, "industry_name": "PETROCHEMICALS", "sector_id": 12},
    {"industry_id": 76, "industry_name": "GEMS & JEWELLERY", "sector_id": 25},
    {"industry_id": 77, "industry_name": "BROADCASTING & CABLE TV", "sector_id": 26},
    {"industry_id": 78, "industry_name": "HOUSEWARE", "sector_id": 16},
    {"industry_id": 79, "industry_name": "TEXTILES", "sector_id": 25},
    {"industry_id": 80, "industry_name": "NON-ALCOHOLIC BEVERAGES", "sector_id": 13},
    {"industry_id": 81, "industry_name": "GENERAL INSURANCE", "sector_id": 4},
    {"industry_id": 82, "industry_name": "EXCHANGE", "sector_id": 4},
    {"industry_id": 83, "industry_name": "INVESTMENT COMPANIES", "sector_id": 27},
    {"industry_id": 84, "industry_name": "CARBON BLACK", "sector_id": 12},
    {"industry_id": 85, "industry_name": "INDUSTRIAL GASES", "sector_id": 1},
    {"industry_id": 86, "industry_name": "CAPITAL MARKETS", "sector_id": 4},
    {"industry_id": 87, "industry_name": "ASSET MANAGEMENT COS.", "sector_id": 4},
    {"industry_id": 88, "industry_name": "PAPER & PAPER PRODUCTS", "sector_id": 21},
    {"industry_id": 89, "industry_name": "HEALTHCARE SUPPLIES", "sector_id": 28},
    {"industry_id": 90, "industry_name": "TRAVEL SUPPORT SERVICES", "sector_id": 11},
    {"industry_id": 91, "industry_name": "EDIBLE OILS", "sector_id": 18},
    {"industry_id": 92, "industry_name": "CONTAINERS & PACKAGING", "sector_id": 21},
    {"industry_id": 93, "industry_name": "IT SOFTWARE PRODUCTS", "sector_id": 22},
    {"industry_id": 94, "industry_name": "INTERNET & CATALOGUE RETAIL", "sector_id": 22},
    {"industry_id": 95, "industry_name": "DATA PROCESSING SERVICES", "sector_id": 22},
    {"industry_id": 96, "industry_name": "MINING", "sector_id": 3},
    {"industry_id": 97, "industry_name": "MOVIES & ENTERTAINMENT", "sector_id": 26},
]

# Random generation helpers
COMPANY_PREFIXES = ["Global", "Modern", "Advanced", "Elite", "Prime", "Royal", "Apex", "Zenith", "Horizon", "Pioneer", "United", "Universal", "First", "National", "Imperial", "Stellar", "Quantum", "Nexus", "Titan", "Velocity"]
COMPANY_SUFFIXES = ["Solutions", "Tech", "Systems", "Enterprises", "Industries", "Holdings", "Group", "Dynamics", "Innovation", "Global", "Logistics", "Services", "Ventures", "Capital", "Partners"]
COMPANY_TYPES = ["Ltd.", "Inc.", "Corporation", "Private Ltd."]

def generate_random_company_name():
    prefix = random.choice(COMPANY_PREFIXES)
    suffix = random.choice(COMPANY_SUFFIXES)
    comp_type = random.choice(COMPANY_TYPES)
    return f"{prefix} {suffix} {comp_type}"

def generate_random_code(name):
    clean_name = "".join(filter(str.isalnum, name)).upper()
    # Add a random suffix to ensure uniqueness
    suffix = "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2))
    return f"{clean_name[:4]}{suffix}"

async def seed_database(engine: AsyncEngine) -> None:
    """Check if companies data exists in DB. If not, generate and insert seed data via SQLAlchemy."""
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_maker() as session:
        # Check if companies table already has data
        result = await session.execute(
            select(func.count()).select_from(Company)
        )
        count = result.scalar()

        if count and count > 0:
            msg = f"Database already seeded ({count} companies found). Skipping."
            logger.info(msg)
            print(msg)
            return

        logger.info("No companies found in DB. Seeding database with random data...")
        print("No companies found in DB. Seeding database with random data...")

        try:
            # 0. Super Admin
            settings = get_settings()
            if settings.SUPER_ADMIN_EMAIL and settings.SUPER_ADMIN_PASSWORD:
                result = await session.execute(
                    select(User).where(User.email == settings.SUPER_ADMIN_EMAIL)
                )
                admin_exists = result.scalar_one_or_none()
                if not admin_exists:
                    super_admin = User(
                        email=settings.SUPER_ADMIN_EMAIL,
                        password_hash=hash_password(
                            settings.SUPER_ADMIN_PASSWORD
                        ),
                        role=UserRole.SUPERADMIN,
                        status=UserStatus.ACTIVE,
                    )
                    session.add(super_admin)
                    await session.flush()
                    logger.info(f"Super Admin created: {settings.SUPER_ADMIN_EMAIL}")

            # 1. Sectors
            sector_objects = [Sector(**s) for s in SECTORS_DATA]
            session.add_all(sector_objects)
            await session.flush()
            logger.info(f"Inserted {len(SECTORS_DATA)} sectors.")

            # 2. Industries
            industry_objects = [Industry(**i) for i in INDUSTRIES_DATA]
            session.add_all(industry_objects)
            await session.flush()
            logger.info(f"Inserted {len(INDUSTRIES_DATA)} industries.")

            # 3. Companies (Generate 500)
            num_companies = 500
            companies = []
            for _ in range(num_companies):
                industry = random.choice(INDUSTRIES_DATA)
                company = Company(
                    company_name=generate_random_company_name(),
                    industry_id=industry["industry_id"]
                )
                session.add(company)
                companies.append(company)
            
            await session.flush() # Flush to get company_ids
            logger.info(f"Generated and inserted {num_companies} random companies.")

            # 4. Exchange Listings (Generate 1-2 per company)
            exchanges = ["NSE", "BSE"]
            for company in companies:
                num_listings = random.randint(1, 2)
                selected_exchanges = random.sample(exchanges, num_listings)
                for ex in selected_exchanges:
                    listing = ExchangeListing(
                        company_id=company.company_id,
                        exchange=ex,
                        code=generate_random_code(company.company_name) if ex == "NSE" else str(random.randint(500000, 599999))
                    )
                    session.add(listing)
            
            await session.flush()
            logger.info("Generated and inserted exchange listings.")

            # 5. Quarterly Results (Generate 4 quarters per company)
            quarters = ["Q1 FY2025", "Q2 FY2025", "Q3 FY2025", "Q4 FY2025"]
            end_dates = [date(2024, 6, 30), date(2024, 9, 30), date(2024, 12, 31), date(2025, 3, 31)]
            
            for company in companies:
                # Basic financial profile for the company to keep numbers somewhat consistent
                base_revenue = Decimal(random.uniform(100, 10000))
                for i, quarter in enumerate(quarters):
                    # Add some variation per quarter
                    rev = base_revenue * Decimal(random.uniform(0.8, 1.2))
                    exp = rev * Decimal(random.uniform(0.6, 0.95))
                    op_profit = rev - exp
                    depr = rev * Decimal(random.uniform(0.01, 0.05))
                    intr = rev * Decimal(random.uniform(0.001, 0.02))
                    pbt = op_profit - depr - intr
                    tax = pbt * Decimal(0.25) if pbt > 0 else Decimal(0)
                    net_profit = pbt - tax
                    eps = net_profit / Decimal(random.randint(10, 100))

                    result = QuarterlyResult(
                        company_id=company.company_id,
                        quarter=quarter,
                        period_end_date=end_dates[i],
                        revenue=rev.quantize(Decimal("0.01")),
                        operating_expenses=exp.quantize(Decimal("0.01")),
                        operating_profit=op_profit.quantize(Decimal("0.01")),
                        depreciation=depr.quantize(Decimal("0.01")),
                        interest=intr.quantize(Decimal("0.01")),
                        profit_before_tax=pbt.quantize(Decimal("0.01")),
                        tax=tax.quantize(Decimal("0.01")),
                        net_profit=net_profit.quantize(Decimal("0.01")),
                        eps=eps.quantize(Decimal("0.01"))
                    )
                    session.add(result)

            await session.commit()
            logger.info("Generated and inserted quarterly results. Seeding complete.")
            print("Seeding complete.")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error seeding database: {e}")
            print(f"Error seeding database: {e}")
            raise e

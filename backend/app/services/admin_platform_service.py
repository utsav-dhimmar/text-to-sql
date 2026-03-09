from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.industry import Industry
from app.models.sector import Sector
from app.models.user import ChatHistory, User, UserRole, UserStatus


class AdminPlatformService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_analytics(self) -> dict:
        total_users = await self._count_users()
        active_users = await self._count_users(status=UserStatus.ACTIVE)
        banned_users = await self._count_users(status=UserStatus.BANNED)
        total_admins = await self._count_admins()
        total_queries = await self._count_queries()

        return {
            "total_users": total_users,
            "active_users": active_users,
            "banned_users": banned_users,
            "total_admins": total_admins,
            "total_queries": total_queries,
        }

    async def create_sector(self, sector_name: str) -> Sector:
        normalized = sector_name.strip()
        if not normalized:
            raise ValueError("Sector name is required.")

        existing = await self.db.execute(
            select(Sector).where(func.lower(Sector.sector_name) == normalized.lower())
        )
        if existing.scalar_one_or_none():
            raise ValueError("Sector already exists.")

        sector = Sector(sector_name=normalized)
        self.db.add(sector)
        await self.db.commit()
        await self.db.refresh(sector)
        return sector

    async def create_company(self, company_name: str, industry_id: int) -> Company:
        normalized = company_name.strip()
        if not normalized:
            raise ValueError("Company name is required.")

        industry_result = await self.db.execute(
            select(Industry).where(Industry.industry_id == industry_id)
        )
        industry = industry_result.scalar_one_or_none()
        if not industry:
            raise ValueError("Industry not found.")

        company = Company(company_name=normalized, industry_id=industry_id)
        self.db.add(company)
        await self.db.commit()
        await self.db.refresh(company)
        return company

    async def _count_users(self, status: UserStatus | None = None) -> int:
        stmt = select(func.count()).select_from(User)
        if status is not None:
            stmt = stmt.where(User.status == status)
        result = await self.db.execute(stmt)
        return int(result.scalar() or 0)

    async def _count_admins(self) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(User).where(User.role == UserRole.ADMIN)
        )
        return int(result.scalar() or 0)

    async def _count_queries(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(ChatHistory))
        return int(result.scalar() or 0)

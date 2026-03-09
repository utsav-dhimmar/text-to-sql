from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole, UserStatus


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, email: str, password: str, role: str = "user") -> User:
        password_hash = hash_password(password)
        user = User(
            email=email,
            password_hash=password_hash,
            role=UserRole(role),
            status=UserStatus.ACTIVE,
        )
        self.db.add(user)
        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            raise ValueError(f"Email already exists: {email}")
        except Exception as e:
            await self.db.rollback()
            raise e

    async def login_user(self, email: str, password: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return None

        if user.status == UserStatus.BANNED:
            raise PermissionError("Your account has been banned.")

        if user.status == UserStatus.DELETED:
            raise PermissionError("Your account has been deleted.")

        if not user.password_hash or not verify_password(password, user.password_hash):
            return None

        return user

    async def get_or_create_google_user(self, google_id: str, email: str) -> User:
        result = await self.db.execute(
            select(User).where((User.google_id == google_id) | (User.email == email))
        )
        user = result.scalar_one_or_none()

        if user:
            # Update google_id if it's missing (e.g., user originally registered via email)
            if not user.google_id:
                user.google_id = google_id
                await self.db.commit()
                await self.db.refresh(user)

            if user.status == UserStatus.BANNED:
                raise PermissionError("Your account has been banned.")
            if user.status == UserStatus.DELETED:
                raise PermissionError("Your account has been deleted.")

            return user

        # Create new user if not found
        user = User(
            email=email,
            google_id=google_id,
            password_hash=None,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
        )
        self.db.add(user)
        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            # If somehow email was taken between check and create
            result = await self.db.execute(select(User).where(User.email == email))
            return result.scalar_one()
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_user_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_all_users(self) -> list[User]:
        result = await self.db.execute(select(User).order_by(User.created_at.desc()))
        return list(result.scalars().all())

    async def update_role(self, user_id: str, new_role: str) -> bool:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False
        target_role = UserRole(new_role)
        if target_role == UserRole.SUPERADMIN:
            existing = await self.get_superadmin()
            if existing and existing.id != user.id:
                raise ValueError("Super admin already exists.")
        user.role = target_role
        await self.db.commit()
        return True

    async def update_status(self, user_id: str, new_status: str) -> bool:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False
        user.status = UserStatus(new_status)
        await self.db.commit()
        return True

    async def delete_user(self, user_id: str) -> bool:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False
        if user.role == UserRole.SUPERADMIN:
            raise PermissionError("Cannot delete super admin.")
        await self.db.delete(user)
        await self.db.commit()
        return True

    async def get_admins(self) -> list[User]:
        result = await self.db.execute(
            select(User)
            .where(User.role == UserRole.ADMIN)
            .order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_superadmin(self) -> User | None:
        result = await self.db.execute(
            select(User).where(User.role == UserRole.SUPERADMIN)
        )
        return result.scalar_one_or_none()

    async def count_superadmins(self) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(User).where(User.role == UserRole.SUPERADMIN)
        )
        return int(result.scalar() or 0)

    async def ensure_superadmin(
        self, email: str | None, password: str | None
    ) -> User | None:
        if not email or not password:
            return None

        existing_superadmin = await self.get_superadmin()
        if existing_superadmin:
            return existing_superadmin

        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            user.role = UserRole.SUPERADMIN
            user.status = UserStatus.ACTIVE
            if not user.password_hash:
                user.password_hash = hash_password(password)
            await self.db.commit()
            await self.db.refresh(user)
            return user

        super_admin = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.SUPERADMIN,
            status=UserStatus.ACTIVE,
        )
        self.db.add(super_admin)
        await self.db.commit()
        await self.db.refresh(super_admin)
        return super_admin

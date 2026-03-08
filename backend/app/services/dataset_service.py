from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset


class DatasetService:
    STATUS_PROCESSING = "processing"
    STATUS_READY = "ready"
    STATUS_ERROR = "error"

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_datasets(self) -> list[Dataset]:
        result = await self.db.execute(
            select(Dataset).order_by(Dataset.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_dataset_by_id(self, dataset_id: str) -> Dataset | None:
        result = await self.db.execute(select(Dataset).where(Dataset.id == dataset_id))
        return result.scalar_one_or_none()

    async def create_dataset(
        self,
        name: str,
        table_name: str,
        source: str = "manual upload",
        uploaded_by: Optional[str] = None,
        row_count: int = 0,
    ) -> Dataset:
        dataset = Dataset(
            name=name,
            source=source,
            uploaded_by=uploaded_by,
            table_name=table_name,
            row_count=row_count,
            status=self.STATUS_PROCESSING,
        )
        self.db.add(dataset)
        await self.db.commit()
        await self.db.refresh(dataset)
        return dataset

    async def update_status(
        self, dataset_id: str, status: str, row_count: Optional[int] = None
    ) -> bool:
        result = await self.db.execute(select(Dataset).where(Dataset.id == dataset_id))
        dataset = result.scalar_one_or_none()
        if not dataset:
            return False
        dataset.status = status
        if row_count is not None:
            dataset.row_count = row_count
        await self.db.commit()
        return True

    async def delete_dataset(self, dataset_id: str) -> bool:
        result = await self.db.execute(select(Dataset).where(Dataset.id == dataset_id))
        dataset = result.scalar_one_or_none()
        if not dataset:
            return False
        await self.db.delete(dataset)
        await self.db.commit()
        return True

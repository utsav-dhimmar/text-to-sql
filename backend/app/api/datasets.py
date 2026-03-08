from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.dependencies import CurrentUser, DBSession
from app.schemas.api import DatasetResponse
from app.services.dataset_service import DatasetService

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.get("/", response_model=List[DatasetResponse])
async def get_datasets(
    db: DBSession,
    current_user: CurrentUser
):
    dataset_service = DatasetService(db)
    datasets = await dataset_service.get_all_datasets()
    return datasets

@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):
    dataset_service = DatasetService(db)
    dataset = await dataset_service.get_dataset_by_id(str(dataset_id))
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.delete("/{dataset_id}", response_model=bool)
async def delete_dataset(
    dataset_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):
    # Only admins should probably delete datasets, but for now let's allow it or check role
    if current_user.role not in ("admin", "superadmin"):
         raise HTTPException(status_code=403, detail="Insufficient permissions")
         
    dataset_service = DatasetService(db)
    success = await dataset_service.delete_dataset(str(dataset_id))
    return success

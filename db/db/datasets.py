# ============================================================
# db/datasets.py
# All database operations for the datasets table
# Uses SQLAlchemy ORM
#
# Table:
#   datasets (id, name, source, uploaded_by, table_name,
#             row_count, status, created_at)
# ============================================================

from sqlalchemy.orm import Session
from db.models import Dataset


# ── Status Constants ─────────────────────────────────────────
STATUS_PROCESSING = "processing"
STATUS_READY      = "ready"
STATUS_ERROR      = "error"


def get_all_datasets(db: Session) -> list[Dataset]:
    """Fetch all datasets ordered by creation date."""
    return db.query(Dataset).order_by(Dataset.created_at.desc()).all()


def get_dataset_by_id(db: Session, dataset_id: str) -> Dataset | None:
    """Fetch a single dataset by UUID. Returns None if not found."""
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()


def create_dataset(
    db:          Session,
    name:        str,
    table_name:  str,
    source:      str = "manual upload",
    uploaded_by: str = None,
    row_count:   int = 0,
) -> Dataset:
    """
    Register a new dataset.
    Status starts as 'processing' automatically.
    """
    dataset = Dataset(
        name=name,
        source=source,
        uploaded_by=uploaded_by,
        table_name=table_name,
        row_count=row_count,
        status=STATUS_PROCESSING,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def update_status(
    db:         Session,
    dataset_id: str,
    status:     str,
    row_count:  int = None,
) -> bool:
    """
    Update dataset status.
    Allowed values: 'processing', 'ready', 'error'
    Optionally update row_count when marking as ready.
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        return False
    dataset.status = status
    if row_count is not None:
        dataset.row_count = row_count
    db.commit()
    return True


def delete_dataset(db: Session, dataset_id: str) -> bool:
    """
    Delete a dataset record.
    Note: this does NOT drop the actual SQL table — handle that separately.
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        return False
    db.delete(dataset)
    db.commit()
    return True
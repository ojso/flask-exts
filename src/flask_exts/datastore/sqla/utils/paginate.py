from math import ceil
from typing import Any, Optional, Generic, TypeVar, Iterator
from sqlalchemy.sql import Select
from sqlalchemy.sql import select,func
from sqlalchemy.orm import Session

T = TypeVar("T")

class Pagination(Generic[T]):
    def __init__(
        self,
        items: list[T],
        total: int,
        page: int,
        per_page: int,
    ):
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.pages = ceil(total / per_page) if per_page > 0 else 0
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1 if self.has_prev else None
        self.next_num = page + 1 if self.has_next else None

    def iter_pages(self) -> Iterator[int]:
        """Iterate over page numbers for pagination controls."""
        return iter(range(1, self.pages + 1))

    def __repr__(self):
        return f"<Pagination page={self.page} of {self.pages}>"

def paginate(
    session: Session,
    stmt: Select,
    *,
    page: int = 1,
    per_page: int = 20,
) -> Pagination:
    """
    Paginate a SQLAlchemy 2.0 select statement.

    Args:
        session: SQLAlchemy Session instance
        stmt: A SQLAlchemy Select statement (e.g., select(User))
        page: Current page number (1-indexed)
        per_page: Number of items per page

    Returns:
        Pagination object with .items, .total, .has_next, etc.
    """

    # Count total rows
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = session.execute(count_stmt).scalar_one()

    if total == 0:
        return Pagination(items=[], total=0, page=page, per_page=per_page)

    if page < 1:
        # raise ValueError("Page must be >= 1")
        page = 1        
    
    pages = ceil(total / per_page)
    if page > pages:
        # raise ValueError(f"Page {page} is out of range (total pages: {pages})")
        page = pages

    # Apply limit/offset
    paginated_stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    items = session.execute(paginated_stmt).scalars().all()

    return Pagination(items=items, total=total, page=page, per_page=per_page)
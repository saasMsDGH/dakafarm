"""
Reusable pagination utilities shared across all modules.

PaginationParams holds parsed query parameters for list endpoints.
It is instantiated in each router rather than used as a FastAPI Depends,
keeping each router's Query declarations explicit and self-documenting.
"""

import math
from typing import TypeVar, Generic, List

from pydantic import BaseModel


T = TypeVar("T")


class PaginationParams:
    """
    Holds pagination, search, and sorting parameters for list queries.

    Attributes:
        page:     Current page number (1-based).
        limit:    Maximum items per page.
        search:   Optional free-text search term.
        sort_by:  Column name to sort by.
        order:    Sort direction — "asc" or "desc".
        offset:   Computed row offset for SQL queries.
    """

    def __init__(
        self,
        page: int = 1,
        limit: int = 20,
        search: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> None:
        self.page = page
        self.limit = limit
        self.search = search
        self.sort_by = sort_by
        self.order = order.lower()
        self.offset = (page - 1) * limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper — used by schemas that need it."""

    items: List[T]
    total: int
    page: int
    limit: int
    pages: int

    model_config = {"from_attributes": True}


def compute_pages(total: int, limit: int) -> int:
    """Return total number of pages given total records and page size."""
    if limit <= 0:
        return 1
    return math.ceil(total / limit) if total > 0 else 1

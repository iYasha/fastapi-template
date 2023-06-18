from typing import Optional

from fastapi import Query

from sdk.exceptions.exceptions import make_error
from sdk.responses import ResponseStatus


class PaginationManager:
    """
    Simple pagination manager.
    """

    def __init__(
        self,
        page: int = Query(1),
        page_size: int = Query(25, description='Available only 10, 25, 50, 100'),
    ) -> None:
        if page_size not in [10, 25, 50, 100, None]:
            raise make_error(
                custom_code=ResponseStatus.PAGINATION_PAGE_ERROR,
                message='Available only 10, 25, 50, 100',
            )
        if page < 1:
            raise make_error(
                custom_code=ResponseStatus.PAGINATION_PAGE_ERROR,
                message='Page number must be greater than 0',
            )
        self.page = page - 1
        self.page_size = page_size

    def get_page_count(self, count: int) -> int:
        return count // self.page_size + count % self.page_size if self.page_size else None  # noqa: S001

    def get_next_page(self, count: int) -> Optional[int]:
        return (self.page + 2 if count > (self.page + 1) * self.page_size else None) if self.page_size else None

    def get_prev_page(self) -> Optional[int]:
        return self.page if self.page > 0 else None

    def check_page(self, count: int) -> None:
        if self.page == 0 or self.page_size is None:
            return
        if self.page * self.page_size >= count:
            raise make_error(
                custom_code=ResponseStatus.PAGINATION_PAGE_ERROR,
                message='Page does not exists',
            )

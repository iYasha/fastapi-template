from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

import sqlalchemy as sa
from database import Base  # type: ignore[attr-defined]
from fastapi import Query
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import UnaryExpression

from sdk.exceptions.exceptions import make_error
from sdk.responses import ResponseStatus

AdditionalFields = Dict[str, Any]


class OrderingManager:
    """
    Simple manager class for request, that handles the ordering of a query.

    _available_columns is a list of columns that can be used for ordering.
    _alias is the alias of the query that is used for ordering, default is 'ordering'.
    """

    _available_columns: Optional[tuple] = None
    _alias: str = 'ordering'

    def __init__(
        self,
        params: Iterable[str] = Query(None, alias=_alias, description='Example: field_1, -field_2'),
    ) -> None:
        """
        :param params: string of comma separated field names
        Example: 'name, -age, -id'
        field = ascending
        -field = descending
        """
        self.ordering_fields = []

        if params is not None:
            self.ordering_fields = params

    def is_available(self, field: str) -> str:
        if self._available_columns is None:
            return field

        if not isinstance(self._available_columns, tuple):
            raise NotImplementedError('available_columns must be tuple')

        if field.lstrip('-') not in self._available_columns:
            raise make_error(
                custom_code=ResponseStatus.ORDERING_FIELD_NOT_AVAILABLE,
                message='Ordering field not available',
                **{self._alias: f'{field} are not available for ordering'},
            )

        return field

    @staticmethod
    def _get_ordering_direction(field: str) -> Callable:
        if field.startswith('-'):
            return sa.desc
        return sa.asc

    def _get_model_attribute(
        self,
        model: Base,
        field: str,
        additional_fields: AdditionalFields,
    ) -> InstrumentedAttribute:
        striped_field = field.lstrip('-')
        if hasattr(model, striped_field):
            return getattr(model, striped_field)
        elif striped_field in additional_fields:
            return additional_fields[striped_field]

        raise make_error(
            custom_code=ResponseStatus.ORDERING_FIELD_NOT_AVAILABLE,
            message='Ordering field not available',
            **{self._alias: f'{field} are not available for ordering'},
        )

    def _get_ordering(
        self,
        model: Base,
        field: str,
        additional_fields: AdditionalFields,
    ) -> UnaryExpression:
        field = self.is_available(field.strip())
        attribute = self._get_model_attribute(model, field, additional_fields)
        return self._get_ordering_direction(field)(attribute)

    def get_fields(
        self,
        model: Base,
        additional_fields: Optional[AdditionalFields] = None,
    ) -> List[UnaryExpression]:
        if additional_fields is None:
            additional_fields = {}
        return [self._get_ordering(model, field, additional_fields) for field in self.ordering_fields]


def get_ordering(
    params: str = Query(
        None,
        alias=OrderingManager._alias,
        description='Example: field_1, -field_2',
    ),
) -> OrderingManager:
    return OrderingManager(params.split(','))

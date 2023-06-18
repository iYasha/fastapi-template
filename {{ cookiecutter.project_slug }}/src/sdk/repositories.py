import copy
import operator
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

import sqlalchemy as sa
from asyncpg import Record
from database import ModelType  # type: ignore[attr-defined]
from database import database  # type: ignore[attr-defined]
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BinaryExpression

from sdk.models import ExpireMixin as ExpireModelMixin
from sdk.ordering import OrderingManager
from sdk.pagination import PaginationManager
from sdk.schemas import BaseSchema
from sdk.schemas import PaginatedSchema

base_operations = {
    'not': operator.ne,
    'exact': operator.eq,
    'gt': operator.gt,
    'gte': operator.ge,
    'lt': operator.lt,
    'lte': operator.le,
}


def is_iterable(x: Any) -> bool:  # noqa: ANN401
    """An implementation independent way of checking for iterables"""
    try:
        iter(x)
    except TypeError:
        return False
    else:
        return True


def make_hashable(value: Any) -> Any:  # noqa: ANN401
    """
    Attempt to make value hashable or raise a TypeError if it fails.

    The returned value should generate the same hash for equal values.
    """
    if isinstance(value, dict):
        return tuple(
            [(key, make_hashable(nested_value)) for key, nested_value in sorted(value.items())],
        )
    # Try hash to avoid converting a hashable iterable (e.g. string, frozenset)
    # to a tuple.
    try:
        hash(value)
    except TypeError:
        if is_iterable(value):
            return tuple(map(make_hashable, value))
        # Non-hashable, non-iterable.
        raise
    return value


class Node:
    """
    A single internal node in the tree graph. A Node should be viewed as a
    connection (the root) with the children being either leaf nodes or other
    Node instances.
    """

    # Standard connector type. Clients usually won't use this at all and
    # subclasses will usually override the value.
    default = 'DEFAULT'

    def __init__(
        self,
        children: Optional['Node'] = None,
        connector: Optional[str] = None,
        negated: bool = False,
    ) -> None:
        """Construct a new Node. If no connector is given, use the default."""
        self.children = children[:] if children else []
        self.connector = connector or self.default
        self.negated = negated

    @classmethod
    def create(
        cls,
        children: Optional['Node'] = None,
        connector: Optional[str] = None,
        negated: bool = False,
    ) -> 'Node':
        """
        Create a new instance using Node() instead of __init__() as some
        subclasses, e.g. django.db.models.query_utils.Q, may implement a custom
        __init__() with a signature that conflicts with the one defined in
        Node.__init__().
        """
        obj = Node(children, connector or cls.default, negated)
        obj.__class__ = cls
        return obj

    def __str__(self) -> str:
        template = '(NOT (%s: %s))' if self.negated else '(%s: %s)'
        return template % (self.connector, ', '.join(str(c) for c in self.children))  # noqa: S001

    def __repr__(self) -> str:
        return '<%s: %s>' % (self.__class__.__name__, self)  # noqa: S001

    def __copy__(self) -> 'Node':
        obj = self.create(connector=self.connector, negated=self.negated)
        obj.children = self.children  # Don't [:] as .__init__() via .create() does.
        return obj

    copy = __copy__

    def __deepcopy__(self, memodict: Dict[int, Any] = None) -> 'Node':
        obj = self.create(connector=self.connector, negated=self.negated)
        obj.children = copy.deepcopy(self.children, memodict)
        return obj

    def __len__(self) -> int:
        """Return the number of children this node has."""
        return len(self.children)

    def __bool__(self) -> bool:
        """Return whether or not this node has children."""
        return bool(self.children)

    def __contains__(self, other: 'Node') -> bool:
        """Return True if 'other' is a direct child of this instance."""
        return other in self.children

    def __eq__(self, other: 'Node') -> bool:
        return (
            self.__class__ == other.__class__
            and self.connector == other.connector
            and self.negated == other.negated
            and self.children == other.children
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.__class__,
                self.connector,
                self.negated,
                *make_hashable(self.children),
            ),
        )

    def add(self, data: 'Node', conn_type: Optional[str]) -> 'Node':
        """
        Combine this tree and the data represented by data using the
        connector conn_type. The combine is done by squashing the node other
        away if possible.

        This tree (self) will never be pushed to a child node of the
        combined tree, nor will the connector or negated properties change.

        Return a node which can be used in place of data regardless if the
        node other got squashed or not.
        """
        if self.connector != conn_type:
            obj = self.copy()
            self.connector = conn_type
            self.children = [obj, data]
            return data
        elif isinstance(data, Node) and not data.negated and (data.connector == conn_type or len(data) == 1):
            # We can squash the other node's children directly into this node.
            # We are just doing (AB)(CD) == (ABCD) here, with the addition that
            # if the length of the other node is 1 the connector doesn't
            # matter. However, for the len(self) == 1 case we don't want to do
            # the squashing, as it would alter self.connector.
            self.children.extend(data.children)
            return self
        else:
            # We could use perhaps additional logic here to see if some
            # children could be used for pushdown here.
            self.children.append(data)
            return data

    def negate(self) -> None:
        """Negate the sense of the root connector."""
        self.negated = not self.negated


class Q(Node):
    """
    Inspired by Django's Q object.
    https://github.com/django/django/tree/main/django/db/models/query_utils.py
    """

    AND = 'AND'
    OR = 'OR'
    XOR = 'XOR'
    default = AND
    conditional = True

    def __init__(
        self,
        *args,
        _connector: Optional[str] = None,
        _negated: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(
            children=[*args, *sorted(kwargs.items())],
            connector=_connector,
            negated=_negated,
        )

    def _combine(self, other: 'Q', conn: str) -> 'Q':
        if getattr(other, 'conditional', False) is False:
            raise TypeError(other)
        if not self:
            return other.copy()
        if not other and isinstance(other, Q):
            return self.copy()

        obj = self.create(connector=conn)
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def __or__(self, other: 'Q') -> 'Q':
        return self._combine(other, self.OR)

    def __and__(self, other: 'Q') -> 'Q':
        return self._combine(other, self.AND)

    def __xor__(self, other: 'Q') -> 'Q':
        return self._combine(other, self.XOR)

    def __invert__(self) -> 'Q':
        obj = self.copy()
        obj.negate()
        return obj

    def get_connector(self) -> Union[Type[sa.and_], Type[sa.or_], Type[sa.not_]]:
        return getattr(sa, self.connector.lower() + '_')

    @staticmethod
    def get_operation(  # noqa: C901, CCR001
        model: Type[ModelType],
        field: str,
        value: Any,  # noqa: ANN401
        operation: str,
    ) -> Any:  # noqa: ANN401
        model_field = getattr(model, field)
        # TODO: Add support for more operations and refactor this method.

        if operation in base_operations:
            return base_operations[operation](model_field, value)

        if operation == 'in':
            return model_field.in_(value)
        elif operation == 'iexact':
            return model_field.ilike(value)
        elif operation == 'contains':
            return model_field.contains(value)
        elif operation == 'icontains':
            return model_field.ilike(f'%{value}%')
        elif operation == 'startswith':
            return model_field.startswith(value)
        elif operation == 'istartswith':
            return model_field.ilike(f'{value}%')
        elif operation == 'endswith':
            return model_field.endswith(value)
        elif operation == 'iendswith':
            return model_field.ilike(f'%{value}')
        elif operation == 'range':
            return model_field.between(value[0], value[1])
        elif operation == 'date':
            if isinstance(value, str):
                value = datetime.strptime(value, '%Y-%m-%d')
            return sa.func.date(model_field) == value

        raise ValueError(f'Unknown operation {operation} in lookup')

    def get_lookup(
        self,
        model: Type[ModelType],
        lookup: str,
        value: Any,  # noqa: ANN401
    ) -> BinaryExpression:  # noqa: ANN401
        field, *operations = lookup.split('__')
        operation = operator.eq
        operation_count = len(operations)
        if operation_count > 1:
            raise ValueError(f'Only one operation is allowed in lookup, got {lookup}')

        if operation_count == 1:
            return self.get_operation(model, field, value, operations[0])

        return operation(getattr(model, field), value)

    def get_where_clause(self, model: Type[ModelType]) -> BinaryExpression:
        connector = self.get_connector()
        return connector(
            *[
                child.get_where_clause(model) if isinstance(child, Q) else self.get_lookup(model, *child)
                for child in self.children
            ],
        )


class WhereMixin:
    def where(self, *args, **fields) -> 'WhereMixin':
        where_clause = []
        for arg in args:
            if not isinstance(arg, Q):
                raise TypeError(arg)

            where_clause.append(arg.get_where_clause(self.model))

        where_clause.append(Q(**fields).get_where_clause(self.model))
        self.query = self.query.where(
            sa.and_(*where_clause),
        )

        return self


class PaginateMixin:
    async def get_paginated_response(
        self,
        model_schemer: Type[BaseSchema],
        manager: PaginationManager,
    ) -> PaginatedSchema:
        if manager.page_size is not None:
            paginated_query = self.query.limit(manager.page_size).offset(
                manager.page * manager.page_size,
            )
        else:
            paginated_query = self.query
        count = await database.fetch_val(
            sa.select([sa.func.count()]).select_from(self.query.alias('original_query')),
        )
        manager.check_page(count)

        raw_results = await database.fetch_all(paginated_query)
        _next = manager.get_next_page(count)
        _prev = manager.get_prev_page()
        _page_count = manager.get_page_count(count)
        results = [model_schemer(**dict(obj)) for obj in raw_results]
        return PaginatedSchema(
            total_count=count,
            page_count=_page_count,
            next=_next,
            previous=_prev,
            results=results,
        )


class ExpireMixin:
    def expire(self, expired: bool = False, utc_now: Optional[datetime] = None) -> 'ExpireMixin':
        if not issubclass(self.model, ExpireModelMixin):
            raise TypeError(f'{self.model} is not subclass of ExpireMixin')

        utc_now = utc_now or datetime.utcnow()
        if expired:
            self.query = self.query.where(
                sa.or_(
                    self.model.end_at < utc_now,
                    self.model.start_at > utc_now,
                ),
            )
        else:
            self.query = self.query.where(
                sa.and_(
                    self.model.end_at >= utc_now,
                    self.model.start_at <= utc_now,
                ),
            )

        return self


class OrderMixin:
    def order_by(self, *args, manager: Optional[OrderingManager] = None) -> 'OrderMixin':
        if manager is None:
            manager = OrderingManager(args)

        self.query = self.query.order_by(*manager.get_fields(self.model))
        return self


class ReturnMixin:
    def returning(self, *args) -> 'ReturnMixin':
        self.query = self.query.returning(*[getattr(self.model, field) for field in args])
        return self


class BaseOperation:
    @classmethod
    def get_base_query(
        cls,
        model: Type[ModelType],
        fields: Tuple[str] = None,
        select: Optional[Union[list, tuple]] = None,
    ) -> Select:
        if select is None:
            select = (model,)
        if fields:
            select = tuple(getattr(model, field) for field in fields)
        return sa.select(select)


class GetOperation(BaseOperation, ExpireMixin, OrderMixin, WhereMixin, PaginateMixin):
    def __init__(
        self,
        model: Type[ModelType],
        fields: Tuple[str] = None,
        get_all: bool = False,
    ) -> None:
        self.model = model
        self.query = self.get_base_query(model, fields)
        if not get_all:
            self.query = self.query.limit(1)
        self.all = get_all

    async def execute(self) -> Union[List[Record], Optional[Record]]:
        if self.all:
            return await database.fetch_all(self.query)
        return await database.fetch_one(self.query)


class CreateOperation(BaseOperation, ReturnMixin, ExpireMixin, WhereMixin):
    def __init__(
        self,
        model: Type[ModelType],
        items: List[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        self.model = model
        self.query = sa.insert(model).values(**kwargs if kwargs else items)

    async def execute(self) -> Optional[Record]:
        return await database.execute(self.query)


class UpdateOperation(BaseOperation, ReturnMixin, ExpireMixin, WhereMixin):
    def __init__(self, model: Type[ModelType], **kwargs) -> None:
        self.model = model
        self.query = sa.update(model).values(**kwargs)

    async def execute(self) -> Optional[Record]:
        return await database.execute(self.query)


class DeleteOperation(BaseOperation, ExpireMixin, WhereMixin):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model
        self.query = sa.delete(model)

    async def execute(self) -> Optional[Record]:
        return await database.execute(self.query)


class CountOperation(BaseOperation, ExpireMixin, WhereMixin):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model
        self.query = sa.select([sa.func.count()]).select_from(model)

    async def execute(self) -> Optional[Record]:
        return await database.execute(self.query)


class BaseRepository(BaseOperation):
    model: Type[ModelType]

    @classmethod
    def get(
        cls,
        *args: str,
    ) -> GetOperation:
        return GetOperation(cls.model, args)

    @classmethod
    def create(
        cls,
        **kwargs,
    ) -> CreateOperation:
        return CreateOperation(cls.model, **kwargs)

    @classmethod
    def update(
        cls,
        **kwargs,
    ) -> UpdateOperation:
        return UpdateOperation(cls.model, **kwargs)

    @classmethod
    def delete(
        cls,
    ) -> DeleteOperation:
        return DeleteOperation(cls.model)

    @classmethod
    def all(
        cls,
        *args: str,
    ) -> GetOperation:
        return GetOperation(cls.model, args, get_all=True)

    @classmethod
    def count(cls) -> CountOperation:
        return CountOperation(cls.model)

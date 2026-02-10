import json
from enum import Enum
from typing import Optional, List, Tuple

from fastapi import Query


class SortDirection(str, Enum):
    """Enumeration for sort direction."""
    ASC = 'asc'
    DESC = 'desc'

    @classmethod
    def from_str(cls, value: str) -> 'SortDirection':
        if value.lower() == 'asc':
            return cls.ASC
        elif value.lower() == 'desc':
            return cls.DESC
        else:
            raise ValueError(f"Invalid sort direction: {value}")


class CommonQueryParams:
    """Class to handle common query parameters for filtering, sorting, and pagination."""
    def __init__(
        self,
        filter_param: Optional[str] = Query('{}', alias='filter'),
        range_param: Optional[str] = Query('[0, 24]', alias='range'),
        sort_param: Optional[str] = Query(None, alias='sort'),
    ):
        self.filter = json.loads(filter_param or 'null')
        self.range = json.loads(range_param or 'null')
        self.sort = json.loads(sort_param or 'null')

    @property
    def order_by(self) -> List[Tuple[str, str]]:
        return [(self.sort[0], self.sort[1])] if self.sort and len(self.sort) == 2 else []

    @property
    def filter_by(self) -> List[Tuple[str, Tuple] | Tuple[str, str]]:
        if not self.filter:
            return []
        filter_list = []
        for key, value in self.filter.items():
            if isinstance(value, list):
                filter_list.append((key, tuple(value)))
            else:
                filter_list.append((key, value))
        return filter_list

    @property
    def limit(self) -> int | None:
        return (self.range[1] - self.range[0] + 1) if self.range else None

    @property
    def offset(self) -> int:
        return self.range[0] if self.range else 0

    def as_dict(self):
        return {
            'filter': self.filter,
            'range': self.range,
            'sort': self.sort,
        }

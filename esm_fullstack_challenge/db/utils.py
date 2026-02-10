from typing import List, Tuple, Any


def query_builder(
        table: str | None = None,
        columns: List[str] | None = None,
        custom_select: str | None = None,
        where: str | None = None,
        group_by: List[str] | None = None,
        order_by: List[str | Tuple[str, str]] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        filter_by: List[Tuple[str, Any] | Tuple[str, str, Any]] | None = None,
        count_only: bool | None = False,
) -> str:
    """Builds a SQL query string based on the provided parameters.

    Args:
        table (str | None, optional): Name of table. Defaults to None.
        columns (list | None, optional): Name of columns to select. Defaults to None.
        custom_select (str | None, optional): Custom select statement that can be
                                              used instead of table and columns
                                              params. Defaults to None.
        where (str | None, optional): Where statement. Defaults to None.
        group_by (List[str] | None, optional): List of columns to group by. Defaults to None.
        order_by (List[str  |  Tuple[str, str]] | None, optional): List of column names
                                                                   or list of (column, direction)
                                                                   to order by. Defaults to None.
        limit (int | None, optional): Number of rows to return. Defaults to None.
        offset (int | None, optional): Number of rows to offset. Defaults to None.
        filter_by (List[Tuple[str, Any]  |  Tuple[str, str, Any]] | None, optional): List of tuples
                                                                                     to filter by. Defaults to None.
        count_only (bool | None, optional): If True, query will return full count of query ignoring
                                            any limit or offset. Defaults to False.

    Returns:
        str: SQL query string.
    """
    select_str = ''
    if custom_select:
        select_str = custom_select
    else:
        select_str = 'select {columns} from {table}'.format(
            columns=' ,'.join(columns) if columns else '*',
            table=table,
        )

    order_by_str = ''
    if order_by:
        for col in order_by:
            if isinstance(col, str):
                order_by_str += f'{col}, '
            elif isinstance(col, tuple) and len(col) == 2:
                col, direction = col
                if direction.lower() in ['asc', 'desc']:
                    order_by_str += f'{col} {direction}, '
                else:
                    raise ValueError(f'Invalid order direction: {direction}')
            else:
                raise ValueError(f'Invalid order_by format: {col}')

        order_by_str = ' order by ' + order_by_str.rstrip(', ')

    assert not where.strip().startswith('where') if where else True, \
        "Where clause should not start with 'where' keyword"

    where_str = f' where {where}' if where else ''
    if filter_by:
        filter_str_list = []
        for col_tuple in filter_by:
            if isinstance(col_tuple, tuple):
                if len(col_tuple) == 2:
                    column, value = col_tuple
                    if isinstance(value, (list, tuple)):
                        value = ', '.join(f'"{v}"' if isinstance(v, str) else str(v) for v in value)
                        filter_str_list.append(f'{column} in ({value})')
                    else:
                        filter_str_list.append(
                            f'{column}="{value}"' if isinstance(value, str) else
                            f'{column}={value}'
                        )
                elif len(col_tuple) == 3:
                    column, operator, value = col_tuple
                    if operator.lower() in ['=', '!=', '<', '>', '<=', '>=']:
                        filter_str_list.append(
                            f'{column} {operator} "{value}"' if isinstance(value, str) else
                            f'{column} {operator} {value}'
                        )
                    else:
                        raise ValueError(f'Invalid operator: {operator}')
                else:
                    raise ValueError(f'Invalid filter_by tuple length: {len(col_tuple)}')
            else:
                raise ValueError(f'Invalid filter_by format: {tuple}')
        where_str += (' and ' if where_str else ' where ') + ' and '.join(filter_str_list)

    group_by_str = ''
    if group_by:
        group_by_str = ' group by ' + ', '.join(group_by)

    if not count_only:
        query = (
            '{select}'
            '{where}'
            '{group_by}'
            '{order_by}'
            '{limit}'
            '{offset}'
            ';'

        ).format(
            select=select_str,
            where=where_str,
            group_by=group_by_str,
            order_by=order_by_str,
            limit=f' limit {limit}' if limit is not None else '',
            offset=f' offset {offset}' if offset is not None else '',
        )
        return query
    else:
        query = (
            'select count(*) from {table}'
            '{where}'
            ';'

        ).format(
            table=table,
            where=where_str,
        )
        return query

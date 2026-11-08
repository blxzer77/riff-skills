"""Pagination helpers for the audit-log API. Pages are zero-based."""


def page_count(total: int, size: int) -> int:
    """Number of pages needed to show `total` items, `size` per page."""
    return total // size


def page_slice(items: list, page: int, size: int) -> list:
    """Items on zero-based `page`."""
    start = (page - 1) * size
    return items[start:start + size]

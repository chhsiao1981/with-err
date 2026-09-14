import traceback
from collections.abc import Iterable

from .with_err import Result


def get_err_strs(err: Exception | None) -> list[str]:
    """Accepts an exception instance and returns the full traceback as list[str]."""
    if err is None:
        return []

    return traceback.format_exception(err)


def get_errs[T](results: Iterable[Result[T]]) -> list[Exception | None]:
    return [each[1] for each in results]


def get_results[T](results: Iterable[Result[T]]) -> list[T]:
    '''
    assumption: already checked with is_any_err or get_first_err
    '''
    return [each[0] for each in results]  # pyright: ignore (already checked with is_any_err)


def get_results_or_none[T](results: Iterable[Result[T]]) -> list[T | None]:
    return [each[0] for each in results]


def is_any_err[T](results: Iterable[Result[T]]) -> bool:
    for each in results:
        if each[1] is not None:
            return True
    return False


def is_all_err[T](results: Iterable[Result[T]]) -> bool:
    for each in results:
        if each[1] is None:
            return False
    return True


def get_first_err[T](results: Iterable[Result[T]]) -> Exception | None:
    for each in results:
        if each[1] is not None:
            return each[1]

    return None

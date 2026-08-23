# https://share.gemini.google/BDvazjX2RWsE

import sys
import types
from collections.abc import Callable
from functools import wraps
from typing import Protocol, overload


# @type_check_only
class CallableWithErr[**P, R](Protocol):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> tuple[R | None, Exception | None]:
        ...


@overload
def with_err[**P, R](
    func: Callable[P, R], /
) -> CallableWithErr[P, R]:
    # Overload 1: Called directly with a function -> with_err(func)
    ...


@overload
def with_err[**P, R](
    *exceptions: type[Exception],
) -> Callable[[Callable[P, R]], CallableWithErr[P, R]]:
    # Overload 2: Called with exception types or no args -> with_err(*exceptions)
    ...


def with_err(*args):
    """
    Wraps a function to return (result, Exception) instead of raising.
    """
    is_func = len(args) == 1 and callable(args[0]) and not (
        isinstance(args[0], type) and issubclass(args[0], Exception))

    # Case 1: Called directly with a target function (e.g., with_err(json.loads))
    if is_func:
        func = args[0]
        return _make_wrapper(func, (Exception,))

    # Case 2: Called with exception types or no args (e.g., with_err(ValueError) or with_err())
    exceptions = args
    if not exceptions:
        exceptions = (Exception,)

    def decorator(func):
        return _make_wrapper(func, exceptions)
    return decorator


def _make_wrapper[**P, R](func: Callable[P, R], exceptions: tuple[type[Exception], ...]):
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[R | None, Exception | None]:
        try:
            return func(*args, **kwargs), None
        except exceptions as e:
            # 1. Fetch exception's original internal traceback.
            tb = sys.exc_info()[2]

            # 2. Capture the caller frame executing func.
            caller_frame = sys._getframe(1)

            # 3. Create a parent traceback frame and link it above 'tb'.
            combined_tb = types.TracebackType(
                tb_next=tb,
                tb_frame=caller_frame,
                tb_lasti=caller_frame.f_lasti,
                tb_lineno=caller_frame.f_lineno
            )

            # 4. Attach the combined traceback back to the error instance
            return None, e.with_traceback(combined_tb)
    return wrapper

# https://share.gemini.google/BDvazjX2RWsE

import sys
import types
from collections.abc import Callable
from functools import wraps

type ReturnWithErr[**P, R] = Callable[
    Callable[P, R],  # pyright: ignore[reportInvalidTypeForm] # parse error
    Callable[P, tuple[R | None, Exception | None]]]


def with_err[**P, R](*exceptions: type[Exception]) -> ReturnWithErr[P, R]:
    """
    Wraps a function to return (result, Exception) instead of raising.

    XXX Reason repeating exceptions and Exception:
        We don't want to create another layer of function tracestack.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, tuple[R | None, Exception | None]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[R | None, Exception | None]:
            try:
                result = func(*args, **kwargs)
                return result, None
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
            except Exception as e:  # ruff: ignore[blind-except]
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
    return decorator

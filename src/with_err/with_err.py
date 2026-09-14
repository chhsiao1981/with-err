import inspect
from collections.abc import AsyncGenerator, Callable, Coroutine, Generator
from functools import wraps
from typing import Any, Protocol

type Result[R] = tuple[R, None] | tuple[None, Exception]


# @type_check_only
class Decorator(Protocol):
    '''
    helper protocol for indirect decorators
    '''

    def __call__[**P, R](
        self, func: Callable[P, R], /
    ) -> Callable[P, Result[R]]:
        ...


# @type_check_only
class AsyncDecorator(Protocol):
    '''
    helper protocol for indirect async decorators
    '''

    def __call__[**P, R](
        self, async_func: Callable[P, Coroutine[Any, Any, R]], /
    ) -> Callable[P, Coroutine[Any, Any, Result[R]]]: ...


# @type_check_only
class GenDecorator(Protocol):
    '''
    helper protocol for indirect decorators
    '''

    def __call__[**P, R](
        self, gen: Callable[P, Generator[R, Any, Any]], /
    ) -> Callable[P, Generator[Result[R], None, None]]: ...


# @type_check_only
class AsyncGenDecorator(Protocol):
    '''
    helper protocol for indirect decorators
    '''

    def __call__[**P, R](
        self, async_gen: Callable[P, AsyncGenerator[R, Any]], /
    ) -> Callable[P, AsyncGenerator[Result[R], Any]]: ...


def with_err[**P, R](
        func: Callable[P, R], /
) -> Callable[P, Result[R]]:
    """
    Wraps a sync function to return `(result, Exception)` instead of raising.

    * use `with_err` for sync function.
    * use `with_exc` for sync function with exceptions.
    * use `with_async_err` for async function.
    * use `with_async_exc` for async function with exceptions.
    * use `with_gen_err` for generator.
    * use `with_gen_exc` for generator with exceptions.
    * use `with_async_gen_err` for async generator.
    * use `with_async_gen_exc` for async generator with exceptions.
    """
    return _with_err(func)  # pyright: ignore (_with_err accepts all with-err funcs)


def with_exc(
        *exceptions: type[Exception],
) -> Decorator:
    """
    Wraps a sync function to return `(result, exception)` instead of raising.

    Other kinds of Exceptions will still be raised.

    * use `with_err` for sync function.
    * use `with_exc` for sync function with exceptions.
    * use `with_async_err` for async function.
    * use `with_async_exc` for async function with exceptions.
    * use `with_gen_err` for generator.
    * use `with_gen_exc` for generator with exceptions.
    * use `with_async_gen_err` for async generator.
    * use `with_async_gen_exc` for async generator with exceptions.

    """

    return _with_err(*exceptions)  # pyright: ignore (_with_err accepts all with-err funcs)


def with_async_err[**P, R](
        async_func: Callable[P, Coroutine[Any, Any, R]], /
) -> Callable[P, Coroutine[Any, Any, Result[R]]]:
    """
    Wraps an async-function to return `(result, Exception)` instead of raising.

    * use `with_err` for sync function.
    * use `with_exc` for sync function with exceptions.
    * use `with_async_err` for async function.
    * use `with_async_exc` for async function with exceptions.
    * use `with_gen_err` for generator.
    * use `with_gen_exc` for generator with exceptions.
    * use `with_async_gen_err` for async generator.
    * use `with_async_gen_exc` for async generator with exceptions.
    """
    return _with_err(async_func)  # pyright: ignore (_with_err accepts all with-err funcs)


def with_async_exc(
        *exceptions: type[Exception],
) -> AsyncDecorator:
    """
    Wraps an async-function to return `(result, exception)` instead of raising.

    Other kinds of Exceptions will still be raised.

    * use `with_err` for sync function.
    * use `with_exc` for sync function with exceptions.
    * use `with_async_err` for async function.
    * use `with_async_exc` for async function with exceptions.
    * use `with_gen_err` for generator.
    * use `with_gen_exc` for generator with exceptions.
    * use `with_async_gen_err` for async generator.
    * use `with_async_gen_exc` for async generator with exceptions.
    """
    return _with_err(*exceptions)  # pyright: ignore (_with_err accepts all with-err funcs)


def with_gen_err[**P, R](
    gen: Callable[P, Generator[R, Any, Any]], /
) -> Callable[P, Generator[Result[R], None, None]]:
    """
    Wraps a generator to return `(result, Exception)` instead of raising.

    * use `with_err` for sync function.
    * use `with_exc` for sync function with exceptions.
    * use `with_async_err` for async function.
    * use `with_async_exc` for async function with exceptions.
    * use `with_gen_err` for generator.
    * use `with_gen_exc` for generator with exceptions.
    * use `with_async_gen_err` for async generator.
    * use `with_async_gen_exc` for async generator with exceptions.
    """
    return _with_err(gen)  # pyright: ignore (_with_err accepts all with-err funcs)


def with_gen_exc(
        *exceptions: type[Exception],
) -> GenDecorator:  # pyright: ignore[reportInvalidTypeVarUse]
    """
    Wraps a generator to return `(result, Exception)` instead of raising.

    Other kinds of Exceptions will still be raised.

    * use `with_err` for sync function.
    * use `with_exc` for sync function with exceptions.
    * use `with_async_err` for async function.
    * use `with_async_exc` for async function with exceptions.
    * use `with_gen_err` for generator.
    * use `with_gen_exc` for generator with exceptions.
    * use `with_async_gen_err` for async generator.
    * use `with_async_gen_exc` for async generator with exceptions.
    """
    return _with_err(*exceptions)  # pyright: ignore (_with_err accepts all with-err funcs)


def with_async_gen_err[**P, R](
        async_gen: Callable[P, AsyncGenerator[R, Any]], /
) -> Callable[P, AsyncGenerator[Result[R], Any]]:
    """
    Wraps an async-generator to return `(result, Exception)` instead of raising.

    * use `with_err` for sync function.
    * use `with_exc` for sync function with exceptions.
    * use `with_async_err` for async function.
    * use `with_async_exc` for async function with exceptions.
    * use `with_gen_err` for generator.
    * use `with_gen_exc` for generator with exceptions.
    * use `with_async_gen_err` for async generator.
    * use `with_async_gen_exc` for async generator with exceptions.

    """
    return _with_err(async_gen)   # pyright: ignore reason: false alarm


def with_async_gen_exc(
        *exceptions: type[Exception],
) -> AsyncGenDecorator:
    """
    Wraps an async-generator to return `(result, exception)` instead of raising.

    Other kinds of Exceptions will still be raised.

    * use `with_err` for sync function.
    * use `with_exc` for sync function with exceptions.
    * use `with_async_err` for async function.
    * use `with_async_exc` for async function with exceptions.
    * use `with_gen_err` for generator.
    * use `with_gen_exc` for generator with exceptions.
    * use `with_async_gen_err` for async generator.
    * use `with_async_gen_exc` for async generator with exceptions.

    """
    return _with_err(*exceptions)  # pyright: ignore (_with_err accepts all with-err funcs)


def _with_err(*args):  # pyright: ignore reason: false alarm
    """
    Wraps a sync-function to return (result, Exception) instead of raising.

    Use with_async_err for async function.
    Use with_gen_err for generator.
    Use with_async_gen_err for async generator.
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


def _make_wrapper(func, exceptions):
    if inspect.iscoroutinefunction(func):
        return _make_async_wrapper(func, exceptions)
    elif inspect.isasyncgenfunction(func):
        return _make_async_gen_wrapper(func, exceptions)
    elif inspect.isgeneratorfunction(func):
        return _make_gen_wrapper(func, exceptions)
    else:
        return _make_sync_wrapper(func, exceptions)


def _make_sync_wrapper[**P, R](
        func: Callable[P, R],
        exceptions: tuple[type[Exception], ...],
) -> Callable[P, Result[R]]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[R]:
        try:
            return func(*args, **kwargs), None
        except exceptions as e:
            return None, e
    return wrapper


def _make_async_wrapper[**P, R](
        func: Callable[P, Coroutine[Any, Any, R]],
        exceptions: tuple[type[Exception], ...]
) -> Callable[P, Coroutine[Any, Any, Result[R]]]:
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result, None
        except exceptions as e:
            return None, e
    return async_wrapper


def _make_gen_wrapper[**P, R](
        func: Callable[P, Generator[R, Any, Any]],
        exceptions: tuple[type[Exception], ...],
) -> Callable[P, Generator[Result[R], None, None]]:
    @wraps(func)
    def gen_wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        while True:
            try:
                item = next(gen)
                yield item, None
            except StopIteration:
                return
            except exceptions as err:
                yield None, err
                return
    return gen_wrapper


def _make_async_gen_wrapper[**P, R](
        func: Callable[P, AsyncGenerator[R, Any]],
        exceptions: tuple[type[Exception], ...],
) -> Callable[P, AsyncGenerator[Result[R], Any]]:
    @wraps(func)
    async def async_gen_wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        while True:
            try:
                item = await anext(gen)
                yield item, None
            except StopAsyncIteration:
                return
            except exceptions as err:
                yield None, err
                return
    return async_gen_wrapper

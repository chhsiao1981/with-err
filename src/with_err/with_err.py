import inspect
from collections.abc import AsyncGenerator, Callable, Coroutine, Generator
from functools import wraps
from typing import Any, Protocol, overload

type Result[R] = tuple[R, None] | tuple[None, Exception]


# @type_check_only
class Decorator(Protocol):
    '''
    helper protocol for indirect decorators
    XXX currently CallableWithErr is misclassfied as CoroutineWithErr
        if Callable returns Any.
    '''
    @overload
    def __call__[**P, R](
        self, func: Callable[P, R], /
    ) -> Callable[P, Result[R]]:
        # XXX currently CallableWithErr is misclassfied as CoroutineWithErr
        #     if Callable returns Any.
        ...


@overload
def with_err[**P, R](
        func: Callable[P, R], /
) -> Callable[P, Result[R]]:
    # Overload 5: Called directly with a function -> with_err(func)
    # XXX currently CallableWithErr is misclassfied as CoroutineWithErr
    #     if Callable returns Any.
    ...


@overload
def with_err[**P, R](
        *exceptions: type[Exception],
) -> Decorator:
    # Overload 1: called with exception types or no args -> with_err(*exceptions)(func)
    ...


# @type_check_only
class AsyncDecorator(Protocol):
    '''
    helper protocol for indirect decorators
    XXX currently CallableWithErr is misclassfied as CoroutineWithErr
        if Callable returns Any.
    '''
    @overload
    def __call__[**P, R](
        self, func: Callable[P, Coroutine[Any, Any, R]], /
    ) -> Callable[P, Coroutine[Any, Any, Result[R]]]: ...


@overload
def with_async_err[**P, R](
        func: Callable[P, Coroutine[Any, Any, R]], /
) -> Callable[P, Coroutine[Any, Any, Result[R]]]:
    # Overload 4: Async call with a function -> with_err(func)
    # XXX currently CallableWithErr is misclassfied as CoroutineWithErr
    #     if Callable returns Any.
    ...


@overload
def with_async_err[**P, R](
        *exceptions: type[Exception],
) -> AsyncDecorator:
    # Overload 1: called with exception types or no args -> with_err(*exceptions)(func)
    ...


# @type_check_only
class GenDecorator(Protocol):
    '''
    helper protocol for indirect decorators
    XXX currently CallableWithErr is misclassfied as CoroutineWithErr
        if Callable returns Any.
    '''
    @overload
    def __call__[**P, R](
        self, func: Callable[P, Generator[R, Any, Any]], /
    ) -> Callable[P, Generator[Result[R], None, None]]: ...


@overload
def with_gen_err[**P, R](
        func: Callable[P, Generator[R, Any, Any]], /
) -> Callable[P, Generator[Result[R], None, None]]:
    # Overload 3: generator directly with a function -> with_err(func)
    ...


@overload
def with_gen_err[**P, R](
        *exceptions: type[Exception],
) -> GenDecorator:
    # Overload 1: called with exception types or no args -> with_err(*exceptions)(func)
    ...


# @type_check_only
class AsyncGenDecorator(Protocol):
    '''
    helper protocol for indirect decorators
    XXX currently CallableWithErr is misclassfied as CoroutineWithErr
        if Callable returns Any.
    '''
    @overload
    def __call__[**P, R](
        self, func: Callable[P, AsyncGenerator[R, Any]], /
    ) -> Callable[P, AsyncGenerator[Result[R], Any]]: ...


@overload
def with_async_gen_err[**P, R](
        func: Callable[P, AsyncGenerator[R, Any]], /
) -> Callable[P, AsyncGenerator[Result[R], Any]]:
    # Overload 2: async generator directly with a function -> with_err(func)
    ...


@overload
def with_async_gen_err[**P, R](
        *exceptions: type[Exception],
) -> AsyncGenDecorator:
    # Overload 1: called with exception types or no args -> with_err(*exceptions)(func)
    ...


def with_err(*args):
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


def with_async_err(*args):
    """
    Wraps an async-function to return (result, Exception) instead of raising.

    Use with_err for sync-function.
    Use with_gen_err for generator.
    Use with_async_gen_err for async generator.
    """
    return with_err(*args)


def with_gen_err(*args):
    """
    Wraps a generator to return (result, Exception) instead of raising.

    Use with_err for sync-function.
    Use with_async_err for async function.
    Use with_async_gen_err for async generator.
    """
    return with_err(*args)


def with_async_gen_err(*args):
    """
    Wraps an async-generator to return (result, Exception) instead of raising.

    Use with_err for sync-function.
    Use with_async_err for async function.
    Use with_gen_err for generator.
    """
    return with_err(*args)


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

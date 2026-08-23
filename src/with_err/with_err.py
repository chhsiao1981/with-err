import inspect
from collections.abc import AsyncGenerator, Callable, Coroutine, Generator
from functools import wraps
from typing import Any, Protocol, overload

type Result[R] = tuple[R, None] | tuple[None, Exception]


# @type_check_only
class CallableWithErr[**P, R](Protocol):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Result[R]:
        ...


# @type_check_only
class CoroutineWithErr[**P, R](Protocol):
    def __call__(
            self, *args: P.args, **kwargs: P.kwargs,
    ) -> Coroutine[Any, Any, Result[R]]:
        ...


# @type_check_only
class GeneratorWithErr[**P, R](Protocol):
    def __call__(
            self, *args: P.args, **kwargs: P.kwargs,
    ) -> Generator[Result[R], None, None]:
        ...


# @type_check_only
class AsyncGeneratorWithErr[**P, R](Protocol):
    def __call__(
            self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncGenerator[Result[R], None]:
        ...


# @type_check_only


class Decorator(Protocol):
    '''
    helper protocol for indirect decorators
    XXX currently CallableWithErr is misclassfied as CoroutineWithErr
        if Callable returns Any.
    '''
    @overload
    def __call__[**P, R](
        self, func: Callable[P, Coroutine[Any, Any, R]], /
    ) -> CoroutineWithErr[P, R]: ...

    @overload
    def __call__[**P, R](
        self, func: Callable[P, AsyncGenerator[R, Any]], /
    ) -> AsyncGeneratorWithErr[P, R]: ...

    @overload
    def __call__[**P, R](
        self, func: Callable[P, Generator[R, Any, Any]], /
    ) -> GeneratorWithErr[P, R]: ...

    @overload
    def __call__[**P, R](
        self, func: Callable[P, R], /
    ) -> CallableWithErr[P, R]:
        # XXX currently CallableWithErr is misclassfied as CoroutineWithErr
        #     if Callable returns Any.
        ...


@overload
def with_err[**P, R](
        *exceptions: type[Exception],
) -> Decorator:
    # Overload 1: called with exception types or no args -> with_err(*exceptions)(func)
    ...


@overload
def with_err[**P, R](
        func: Callable[P, Coroutine[Any, Any, R]], /
) -> CoroutineWithErr[P, R]:
    # Overload 4: Async call with a function -> with_err(func)
    # XXX currently CallableWithErr is misclassfied as CoroutineWithErr
    #     if Callable returns Any.
    ...


@overload
def with_err[**P, R](
        func: Callable[P, AsyncGenerator[R, Any]], /
) -> AsyncGeneratorWithErr[P, R]:
    # Overload 2: async generator directly with a function -> with_err(func)
    ...


@overload
def with_err[**P, R](
        func: Callable[P, Generator[R, Any, Any]], /
) -> GeneratorWithErr[P, R]:
    # Overload 3: generator directly with a function -> with_err(func)
    ...


@overload
def with_err[**P, R](
        func: Callable[P, R], /
) -> CallableWithErr[P, R]:
    # Overload 5: Called directly with a function -> with_err(func)
    # XXX currently CallableWithErr is misclassfied as CoroutineWithErr
    #     if Callable returns Any.
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


def _make_wrapper(func, exceptions):
    if inspect.iscoroutinefunction(func):
        return _make_async_wrapper(func, exceptions)
    elif inspect.isasyncgenfunction(func):
        return _make_async_gen_wrapper(func, exceptions)
    elif inspect.isgeneratorfunction(func):
        return _make_sync_gen_wrapper(func, exceptions)
    else:
        return _make_sync_wrapper(func, exceptions)


def _make_sync_wrapper[**P, R](
        func: Callable[P, R],
        exceptions: tuple[type[Exception], ...],
) -> CallableWithErr[P, R]:
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
) -> CoroutineWithErr[P, R]:
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result, None
        except exceptions as e:
            return None, e
    return async_wrapper


def _make_sync_gen_wrapper[**P, R](
        func: Callable[P, Generator[R, Any, Any]],
        exceptions: tuple[type[Exception], ...],
) -> GeneratorWithErr[P, R]:
    @wraps(func)
    def sync_gen_wrapper(*args, **kwargs):
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
    return sync_gen_wrapper


def _make_async_gen_wrapper[**P, R](
        func: Callable[P, AsyncGenerator[R, Any]],
        exceptions: tuple[type[Exception], ...],
) -> AsyncGeneratorWithErr[P, R]:
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

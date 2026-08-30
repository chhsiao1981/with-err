import inspect
import json
import re
from typing import Self

import pytest

from with_err import (
    Result,
    get_err_strs,
    with_async_err,
    with_async_gen_err,
    with_err,
    with_gen_err,
)


def test_with_err_success():
    '''
    success.
    '''
    json_loads_e = with_err()(json.loads)
    signature = inspect.signature(json_loads_e)
    sig_dict = {
        name: {
            'obj': obj,
            'type': obj.kind,
            'default': obj.default,
            'annotation': obj.annotation,
            'name': obj.name,
        }
        for name, obj in signature.parameters.items()}

    print(f'sig_dict: {sig_dict}')

    # json.loads parameters
    # very primitive info from inspect.signature.
    # requiring typeshed_client to obtained python stdlib types.
    assert 's' in sig_dict
    assert sig_dict['s']['type'] == inspect._ParameterKind.POSITIONAL_OR_KEYWORD
    assert sig_dict['s']['default'] is inspect._empty
    assert sig_dict['s']['annotation'] is inspect._empty
    assert 'cls' in sig_dict
    assert sig_dict['cls']['type'] == inspect._ParameterKind.KEYWORD_ONLY
    assert sig_dict['cls']['default'] is None
    assert sig_dict['cls']['annotation'] is inspect._empty
    assert 'object_hook' in sig_dict
    assert sig_dict['object_hook']['type'] == inspect._ParameterKind.KEYWORD_ONLY
    assert sig_dict['object_hook']['default'] is None
    assert sig_dict['cls']['annotation'] is inspect._empty
    assert 'parse_float' in sig_dict
    assert sig_dict['parse_float']['type'] == inspect._ParameterKind.KEYWORD_ONLY
    assert sig_dict['parse_float']['default'] is None
    assert sig_dict['parse_float']['annotation'] is inspect._empty
    assert 'parse_int' in sig_dict
    assert sig_dict['parse_int']['type'] == inspect._ParameterKind.KEYWORD_ONLY
    assert sig_dict['parse_int']['default'] is None
    assert sig_dict['parse_int']['annotation'] is inspect._empty
    assert 'parse_constant' in sig_dict
    assert sig_dict['parse_constant']['type'] == inspect._ParameterKind.KEYWORD_ONLY
    assert sig_dict['parse_constant']['default'] is None
    assert sig_dict['parse_constant']['annotation'] is inspect._empty
    assert 'object_pairs_hook' in sig_dict
    assert sig_dict['object_pairs_hook']['type'] == inspect._ParameterKind.KEYWORD_ONLY
    assert sig_dict['object_pairs_hook']['default'] is None
    assert sig_dict['object_pairs_hook']['annotation'] is inspect._empty
    assert 'kw' in sig_dict
    assert sig_dict['kw']['type'] == inspect._ParameterKind.VAR_KEYWORD
    assert sig_dict['kw']['default'] is inspect._empty
    assert sig_dict['kw']['annotation'] is inspect._empty

    a = '{"test": 1}'
    the_struct, err = json_loads_e(a)
    assert err is None
    assert the_struct == {'test': 1}


def test_with_err_exception():
    '''
    Exception.
    '''
    json_loads_e = with_err()(json.loads)

    a = '{"test": }'
    the_struct, err = json_loads_e(a)

    assert the_struct is None
    assert err is not None
    assert isinstance(err, json.decoder.JSONDecodeError)
    err_str = "\n".join(get_err_strs(err))
    print(f'test_with_err: exception: err_str: {err_str}')

    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
    assert 'json.decoder.JSONDecodeError: Expecting value: line 1 column 10 (char 9)' in err_str


def test_with_err_re_pattern_error_on_json():
    '''
    Exception.
    '''
    with pytest.raises(json.decoder.JSONDecodeError):
        json_loads_e = with_err(re.PatternError)(json.loads)

        a = '{"test": }'
        json_loads_e(a)


@with_err
def my_json_loads(a: str):
    return json.loads(a)


def test_with_err_decorator():
    '''
    decorator.
    '''
    a = '{"test": }'
    the_struct, err = my_json_loads(a)

    assert the_struct is None
    assert err is not None
    err_str = "\n".join(get_err_strs(err))
    print(f'test_with_err: my_json_loads: err_str: {err_str}')

    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'test_with_err.py", line \d+, in my_json_loads', err_str)
    assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
    assert 'json.decoder.JSONDecodeError: Expecting value: line 1 column 10 (char 9)' in err_str


def my_json_loads2(a: str):
    return my_json_loads3(a)


def my_json_loads3(a: str):
    return json.loads(a)


def test_with_err_multilayer_function():
    '''
    multi-layer functions.
    '''
    json_loads_e = with_err(my_json_loads2)

    a = '{"test": }'
    the_struct, err = json_loads_e(a)

    assert the_struct is None
    assert err is not None
    assert isinstance(err, json.decoder.JSONDecodeError)
    err_str = "\n".join(get_err_strs(err))
    print(f'test_with_err: my_json_loads2: err_str: {err_str}')

    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'test_with_err.py", line \d+, in my_json_loads2', err_str)
    assert re.search(r'test_with_err.py", line \d+, in my_json_loads3', err_str)
    assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
    assert 'json.decoder.JSONDecodeError: Expecting value: line 1 column 10 (char 9)' in err_str


def test_with_err_typed_output():
    '''
    success.
    '''
    re_search_e = with_err()(re.search)

    a = '{"test": 1}'
    match, err = re_search_e(r'test', a)
    assert err is None
    assert match is not None


def test_with_err_direct_wrapper():
    '''
    re: success.
    '''
    re_search_e = with_err(re.search)

    a = '{"test": 1}'
    match, err = re_search_e(r'test', a)
    assert err is None
    assert match is not None


def test_with_err_direct_wrapper_err():
    '''
    re: pattern error.
    '''
    re_search_e = with_err(re.search)

    a = '{"test": 1}'
    match, err = re_search_e(r'[test', a)
    assert isinstance(err, re.PatternError)
    assert match is None


# async test
async def async_fetch_data(endpoint: str) -> dict[str, str]:
    if endpoint == "bad":
        raise ValueError("Failed to reach endpoint")
    return {"status": "ok"}


@pytest.mark.asyncio
async def test_with_err_async_err():
    '''
    test async err
    '''
    async_fetch_data_e = with_async_err(async_fetch_data)
    res, err = await async_fetch_data_e("bad")
    err_stack = get_err_strs(err)
    err_str = '\n'.join(err_stack)
    print(f'err_str: {err_str}')
    assert isinstance(err, ValueError)
    assert res is None
    assert re.search(r'with_err.py", line \d+, in async_wrapper', err_str)
    assert re.search(r'test_with_err.py", line \d+, in async_fetch_data', err_str)
    assert re.search(r'ValueError: Failed to reach endpoint', err_str)


@pytest.mark.asyncio
async def test_with_err_async_success():
    '''
    test async err
    '''
    async_fetch_data_e = with_async_err(async_fetch_data)
    res, err = await async_fetch_data_e("good")

    assert err is None
    assert res == {'status': 'ok'}


@pytest.mark.asyncio
async def test_with_err_async_err_specified_error():
    '''
    test async err (ValueError)
    '''
    async_fetch_data_e = with_async_err(ValueError)(async_fetch_data)
    res, err = await async_fetch_data_e("bad")
    err_stack = get_err_strs(err)
    err_str = '\n'.join(err_stack)
    print(f'err_str: {err_str}')
    assert isinstance(err, ValueError)
    assert res is None
    assert re.search(r'with_err.py", line \d+, in async_wrapper', err_str)
    assert re.search(r'test_with_err.py", line \d+, in async_fetch_data', err_str)
    assert re.search(r'ValueError: Failed to reach endpoint', err_str)


# async test
@with_async_err
async def async_fetch_data2_e(endpoint: str) -> dict[str, str]:
    if endpoint == "bad":
        raise ValueError("Failed to reach endpoint")
    return {"status": "ok"}


@pytest.mark.asyncio
async def test_with_err_async_err_decorator():
    '''
    test async err (ValueError)
    '''
    res, err = await async_fetch_data2_e("bad")
    err_stack = get_err_strs(err)
    err_str = '\n'.join(err_stack)
    print(f'err_str: {err_str}')
    assert isinstance(err, ValueError)
    assert res is None
    assert re.search(r'with_err.py", line \d+, in async_wrapper', err_str)
    assert re.search(r'test_with_err.py", line \d+, in async_fetch_data', err_str)
    assert re.search(r'ValueError: Failed to reach endpoint', err_str)


@with_gen_err
def my_stream():
    yield 1
    raise ValueError('invalid')


def test_with_err_yield():
    for idx, (each, err) in enumerate(my_stream()):
        if idx == 0:
            assert each == 1
            assert err is None
        else:
            assert each is None
            assert isinstance(err, ValueError)


@with_gen_err
def my_stream2():
    idx = 0

    idx += 1
    yield idx

    idx += 1
    yield idx

    idx += 1
    yield idx


def test_with_err_yield_success():
    end_idx = None
    for idx, (each, err) in enumerate(my_stream2()):
        end_idx = idx
        assert each == idx + 1
        assert err is None

    assert end_idx == 2


@with_async_gen_err
async def my_async_stream():
    yield 1
    raise ValueError('invalid')


@pytest.mark.asyncio
async def test_with_err_async_yield():
    async for each, err in my_async_stream():
        if each == 1:
            assert each == 1
            assert err is None
        else:
            assert each is None
            assert isinstance(err, ValueError)


@with_async_gen_err
async def my_async_stream2():
    idx = 0

    idx += 1
    yield idx

    idx += 1
    yield idx

    idx += 1
    yield idx


@pytest.mark.asyncio
async def test_with_err_async_yield_success():
    async for each, err in my_async_stream2():
        assert each in [1, 2, 3]
        assert err is None


@pytest.mark.asyncio
async def test_with_err_async_yield_success2():
    gen = my_async_stream2()

    ret, err = await anext(gen)
    assert ret == 1
    assert err is None

    ret, err = await anext(gen)
    assert ret == 2
    assert err is None

    ret, err = await anext(gen)
    assert ret == 3
    assert err is None

    with pytest.raises(StopAsyncIteration):
        await anext(gen)


@with_async_gen_err
async def my_async_stream3():
    idx = 0

    idx += 1
    yield idx

    idx += 1
    yield idx

    raise ValueError('invalid value')

    # not reaching the following code block.
    idx += 1
    yield idx


@pytest.mark.asyncio
async def test_with_err_async_yield3_for_loop():
    async for each, err in my_async_stream3():
        print(f'test_with_err_async_yield3_for_loop: each: {each} err: {err}')
        assert each != 3

        if each in [1, 2]:
            assert each in [1, 2]
            assert err is None
        else:
            assert each is None
            assert isinstance(err, ValueError)


@pytest.mark.asyncio
async def test_with_err_async_yield3_anext():
    gen = my_async_stream3()

    ret, err = await anext(gen)
    assert ret == 1
    assert err is None

    ret, err = await anext(gen)
    assert ret == 2
    assert err is None

    ret, err = await anext(gen)
    assert ret is None
    assert isinstance(err, ValueError)

    with pytest.raises(StopAsyncIteration):
        await anext(gen)


@with_err
def my_re4(a: str):
    data, err = my_re5(a)
    if err is not None:
        raise err

    return data


@with_err
def my_re5(a: str):
    return re.search(r'[asdas', a)


def test_with_err_continuous_with_err():
    '''
    multi-layer @with_err functions with.
    '''
    a = '{"test": }'
    the_struct, err = my_re4(a)

    assert the_struct is None
    assert err is not None
    err_str = "\n".join(get_err_strs(err))
    print(f'test_with_err: my_json_loads4: err_str: {err_str}')

    assert isinstance(err, re.PatternError)

    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'test_with_err.py", line \d+, in my_re4', err_str)
    assert re.search(r'test_with_err.py", line \d+, in my_re5', err_str)
    assert re.search(r're/__init__.py", line \d+, in search', err_str)
    assert 're.PatternError: unterminated character set at position 0' in err_str


@with_err
def my_list_func(is_good=False):
    if not is_good:
        raise ValueError('not good')
    return [1, 2]


def test_with_err_list_func():
    data, err = my_list_func()
    assert data is None
    assert isinstance(err, ValueError)

    data, err = my_list_func(True)
    assert data is not None
    assert err is None
    item1, item2 = data
    assert item1 == 1
    assert item2 == 2


@with_err
def my_str():
    return 'temp'


def test_result():
    ret = my_str()
    temp_str, err = ret
    assert err is None
    assert temp_str == 'temp'

    ret2: Result[str] = 'temp', None
    assert ret == ret2


class Temp2:
    my_str = 'Temp2'

    def __init__(self: Self):
        pass


class Temp:
    @with_err
    def my_str(self: Self):
        return 'Temp'

    @with_err()
    def my_model2[T](self, model: type[T]) -> T:
        ret = model()
        return ret

    def my_model3[T](self, model: type[T]) -> T:
        ret = model()
        return ret

    @with_async_err
    async def my_model4[T](self: Self, model: type[T]):
        ret = model()
        return ret

    @with_gen_err
    def my_model5[T](self: Self, model: type[T]):
        ret = model()
        yield ret

    @with_async_gen_err
    async def my_model6[T](self: Self, model: type[T]):
        ret = model()
        yield ret

    @with_async_gen_err
    async def my_model7[T](self: Self, model: type[T]):
        ret = await self.temp(model)
        yield ret

    async def temp[T](self: Self, model: type[T]):
        ret = model()
        return ret

    def __init__(self: Self):
        pass


@pytest.mark.asyncio
async def test_class_func():
    temp = Temp()

    ret = temp.my_str()
    temp_str, err = ret
    assert err is None
    assert temp_str == 'Temp'

    # sync-function
    ret2 = temp.my_model2(Temp2)
    temp2, err = ret2
    assert err is None
    assert temp2 is not None
    assert isinstance(temp2, Temp2)
    assert temp2.my_str == 'Temp2'

    # with_err as function
    ret3 = with_err(temp.my_model3)(Temp2)
    temp3, err = ret3
    assert err is None
    assert temp3 is not None
    assert isinstance(temp3, Temp2)
    assert temp3.my_str == 'Temp2'

    # async function
    ret4 = await temp.my_model4(Temp2)
    temp4, err = ret4
    assert err is None
    assert temp4 is not None
    assert isinstance(temp4, Temp2)
    assert temp4.my_str == 'Temp2'

    # generator
    for each_ret, err in temp.my_model5(Temp2):
        assert err is None
        assert isinstance(each_ret, Temp2)

    # async generator
    async for each_ret6, err in temp.my_model6(Temp2):
        assert err is None
        assert isinstance(each_ret6, Temp2)

    # async generator
    async for each_ret7, err in temp.my_model7(Temp2):
        assert err is None
        assert isinstance(each_ret7, Temp2)

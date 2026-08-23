import inspect
import json
import re

import pytest

from with_err import get_err_strs, with_err


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


def test_with_err_my_json_loads():
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


def test_with_err_my_json_loads2():
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


def test_with_err_re_search():
    '''
    success.
    '''
    re_search_e = with_err(re.search)

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
    async_fetch_data_e = with_err(async_fetch_data)
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
    async_fetch_data_e = with_err(async_fetch_data)
    res, err = await async_fetch_data_e("good")

    assert err is None
    assert res == {'status': 'ok'}


@pytest.mark.asyncio
async def test_with_err_async_err2():
    '''
    test async err (ValueError)
    '''
    async_fetch_data_e = with_err(ValueError)(async_fetch_data)
    res, err = await async_fetch_data_e("bad")
    err_stack = get_err_strs(err)
    err_str = '\n'.join(err_stack)
    print(f'err_str: {err_str}')
    assert isinstance(err, ValueError)
    assert res is None
    assert re.search(r'with_err.py", line \d+, in async_wrapper', err_str)
    assert re.search(r'test_with_err.py", line \d+, in async_fetch_data', err_str)
    assert re.search(r'ValueError: Failed to reach endpoint', err_str)


@with_err
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


@with_err
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


@with_err
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


@with_err
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


@with_err
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

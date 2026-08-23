# with-err

`with-err` is a python library that converts `try-except` pattern into Go-like `result, err` pattern. I feel `result, err` pattern easier to maintain in large projects.

## Getting Started

### Install

```sh
pip install with-err
```

(with [`uv`](https://docs.astral.sh/uv/))
```sh
uv pip install with-err
```

### Use as Function

```python
import json
from with_err import with_err

json_loads_e = with_err(json.loads)

data, err = json_loads_e('{"a": 1}')
assert err is None
assert data == {"a": 1}

data, err = json_loads_e('{"a": }')
assert isinstance(err, json.decoder.JSONDecodeError)
assert data is None
```

### Use as Decorator

```python
import json
from with_err import with_err

@with_err
def json_loads_e(a: str):
    return json.loads(a)

data, err = json_loads_e('{"a": 1}')
assert err is None
assert data == {"a": 1}

data, err = json_loads_e('{"a": }')
assert isinstance(err, json.decoder.JSONDecodeError)
assert data is None
```

### `with_err` with Specified Exceptions

Return err only with specified exceptions and raise other exceptions.

```python
import json
from with_err import with_err

@with_err(json.decoder.JSONDecodeError)
def json_loads_e(a: str):
    return json.loads(a)

data, err = json_loads_e('{"a": 1}')
assert err is None
assert data == {"a": 1}

data, err = json_loads_e('{"a": }')
assert isinstance(err, json.decoder.JSONDecodeError)
assert data is None
```

```python
# raise json.decoder.JSONDecodeError

import json
import re
from with_err import with_err

@with_err(re.PatternError)
def json_loads_e(a: str):
    return json.loads(a)

data, err = json_loads_e('{"a": }')
```

```python
# function

import json
from with_err import with_err

json_loads_e = with_err(json.decoder.JSONDecodeError)(json.loads)

data, err = json_loads_e('{"a": 1}')
assert err is None
assert data == {"a": 1}

data, err = json_loads_e('{"a": }')
assert isinstance(err, json.decoder.JSONDecodeError)
assert data is None
```

```python
# empty: return all Exceptions

import json
from with_err import with_err

json_loads_e = with_err()(json.loads)

data, err = json_loads_e('{"a": 1}')
assert err is None
assert data == {"a": 1}

data, err = json_loads_e('{"a": }')
assert isinstance(err, json.decoder.JSONDecodeError)
assert data is None
```

### Async Functions

```python
from with_err import with_err

async def async_fetch_data(endpoint: str) -> dict[str, str]:
    if endpoint == "bad":
        raise ValueError("Failed to reach endpoint")
    return {"status": "ok"}

async_fetch_data_e = with_err(async_fetch_data)
res, err = await async_fetch_data_e("bad")
assert isinstance(err, ValueError)
assert res is None
```

### Generators

```python
from with_err import with_err


@with_err
def my_stream():
    yield 1
    raise ValueError('invalid')

for idx, (each, err) in enumerate(my_stream()):
    if idx == 0:
        assert each == 1
        assert err is None
    else:
        assert each is None
        assert isinstance(err, ValueError)
```

### Async Generators

```python
from with_err import with_err


@with_err
async def my_async_stream():
    yield 1
    raise ValueError('invalid')

async for each, err in my_async_stream():
    if each == 1:
        assert each == 1
        assert err is None
    else:
        assert each is None
        assert isinstance(err, ValueError)
```

### Functions Returning `list` or `tuple`

```python
@with_err
def my_list_func(is_good=False):
    if not is_good:
        raise ValueError('not good')
    return [1, 2]

data, err = my_list_func()
assert data is None
assert isinstance(err, ValueError)

data, err = my_list_func(True)
assert data is not None
assert err is None
item1, item2 = data
assert item1 == 1
assert item2 == 2
```

### Get `err` Traceback Stack

```python
import json
from with_err import with_err, get_err_strs


@with_err
def json_loads_e(a: str):
    return json.loads(a)

_data, err = json_loads_e('{"a": 1}')
err_stack = get_err_strs(err)
assert err is None
assert err_stack == []
```

```python
import json
import re
from with_err import with_err, get_err_strs


@with_err
def json_loads_e(a: str):
    return json.loads(a)

_data, err = json_loads_e('{"a": }')
err_stack = get_err_strs(err)
err_str = '\n'.join(err_stack)
assert isinstance(err, json.decoder.JSONDecodeError)
assert len(err_stack) > 0
assert re.search(r', line \d+, in json_loads_e', err_str)
assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
assert 'json.decoder.JSONDecodeError: Expecting value:' in err_str
```

### Raise `err`

```python
import json
import re
from with_err import with_err, get_err_strs, raise_err


@with_err
def json_loads_e(a: str):
    return json.loads(a)

def gen_err():
    data, err = json_loads_e('{"a": }')
    return data, raise_err(err)

data, err = gen_err()
err_stack = get_err_strs(err)
err_str = '\n'.join(err_stack)
assert isinstance(err, json.decoder.JSONDecodeError)
assert len(err_stack) > 0
assert re.search(r', line \d+, in gen_err', err_str)
assert re.search(r', line \d+, in json_loads_e', err_str)
assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
assert 'json.decoder.JSONDecodeError: Expecting value:' in err_str
```

### Raise `err` with Continuous `@with_err`

```python
import json
import re
from with_err import with_err, get_err_strs, raise_err


@with_err
def json_loads_e(a: str):
    return json.loads(a)


@with_err
def gen_err():
    data, err = json_loads_e('{"a": }')
    if err is not None:
        raise err
    return data

data, err = gen_err()
err_stack = get_err_strs(err)
err_str = '\n'.join(err_stack)
assert isinstance(err, json.decoder.JSONDecodeError)
assert len(err_stack) > 0
assert re.search(r', line \d+, in gen_err', err_str)
assert re.search(r', line \d+, in json_loads_e', err_str)
assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
assert 'json.decoder.JSONDecodeError: Expecting value:' in err_str
```

## Acknowledgement

The implementation is based on the following Gemini / ChatGPT suggestions:

[https://share.gemini.google/BDvazjX2RWsE](https://share.gemini.google/BDvazjX2RWsE)
[https://chatgpt.com/share/6a8b20b2-4ad4-83ea-9926-4f204ebc4e65](https://chatgpt.com/share/6a8b20b2-4ad4-83ea-9926-4f204ebc4e65)
[https://chatgpt.com/share/6a8b209f-a6f4-83ea-a7da-5d4bf54e4ecd](https://chatgpt.com/share/6a8b209f-a6f4-83ea-a7da-5d4bf54e4ecd)
[https://chatgpt.com/share/6a8b53e2-570c-83ea-94e4-b312d8048059](https://chatgpt.com/share/6a8b53e2-570c-83ea-94e4-b312d8048059)

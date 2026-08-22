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
assert data = {"a": 1}

data, err = json_loads_e('{"a": }')
assert isinstance(err, json.decoder.JSONDecodeError)
assert data is None
```

### Use as Decorator

```python
import json
from with_err import with_err

@with_err
def json_loads_e(a: str | bytes | bytearray):
    return json.loads(a)

data, err = json_loads_e('{"a": 1}')
assert err is None
assert data = {"a": 1}

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
def json_loads_e(a: str | bytes | bytearray):
    return json.loads(a)

data, err = json_loads_e('{"a": 1}')
assert err is None
assert data = {"a": 1}

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
def json_loads_e(a: str | bytes | bytearray):
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
assert data = {"a": 1}

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
assert data = {"a": 1}

data, err = json_loads_e('{"a": }')
assert isinstance(err, json.decoder.JSONDecodeError)
assert data is None
```

### Get `err` Traceback Stack

```python
import json
from with_err import with_err, get_err_strs

def json_loads_e(a: str | bytes | bytearray):
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

def json_loads_e(a: str | bytes | bytearray):
    return json.loads(a)

_data, err = json_loads_e('{"a": }')
err_stack = get_err_strs(err)
err_str = '\n'.join(err_stack)
assert isinstance(err, json.decoder.JSONDecodeError)
assert len(err_stack) > 0
assert 'json.decoder.JSONDecodeError: Expecting value:' in err_str
assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
assert re.search(r', line \d+, in json_loads_e', err_str)
```

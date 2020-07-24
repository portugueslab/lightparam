# Lightparam
[![PyPI version](https://badge.fury.io/py/lightparam.svg)](https://pypi.org/project/lightparam)
[![build](https://travis-ci.com/portugueslab/lightparam.svg?branch=master)](https://travis-ci.com/github/portugueslab/lightparam?branch=master)

Another attempt at parameters in Python, built to satisfy requirements of Stytra:

- Automatic GUI building
- Global parameter tree structure
- Parametrized functions
- Saving and restoring

## Basic classes

### Param
The basic parameter object. The value can be of any python type,
 although automatic GUI generation is supported for some:
 ```
 int
 float
 lists
 str
 range (a tuple of floats)
 folder
 ```

### Parametrized
Class where some parameters are attributes. Their values are acessible
with the dot syntax, and the parameter objects themselves thorugh the params
attribute:
```python
class MyParametrized(Parametrized):
    def __init__(self):
        super().__init__()
        self.x = Param(1.0, (0.0, 2.0))
        
>>> o = MyParametrized()
>>> o.x
1.0
>>> o.params.x.limits
(0.0, 2.0)

```

### ParameterTree

## GUI building
Currently, automatic GUI generation is supported for PyQt5 and for ipywidget support.


## Parametrizing functions
Arguments of functions can be parametrized by annotaning their arguments using the Python 3 function annotation syntax.
For example:
```python
def func(x : Param(1.0)):
    print(x)
```

one can easily make parametrized objects out of it

```python
p = Parametrized(params=func)
```

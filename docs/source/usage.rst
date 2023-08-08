usage
-----

register functions with stack
===============================

Using the register decorator `@stack.register` on your functions will register it with stack `meta_handler`. Stored functions are available across tools.

.. code-block:: python

   import stack

   @stack.register
   def add(x : int, y : int):
       '''add two integers'''
       return x + y

You can also register async functions, these will be executed using `asyncio.run()` given a valid coroutine function

.. code-block:: python

   import stack
   import asyncio

   @stack.register
   async def delay_add(x : int, y : int):
       '''add two integers after 1 sec'''
       await asyncio.sleep(1)
       return x + y

**NOTE:** Adding type hinting to your functions enforces types in the cli and adds positional arg class identifiers in the help docs for the command.

cli - initialization standard
=============================

It is suggested to define the command line interface after `if __name__ == '__main__'`. Any code before the cli will run even if a cli command is used; code after the cli definition will not run when passing a cli command.

.. code-block:: python

    import stack

    # registered functions...

    # module level function calls...

    if __name__ == '__main__':
        # main code (will run even when using cli commands)...
        stack.cli(*args, **kwargs)
        # main code (will NOT run when using cli commands)...

cli - usage example
===================

.. code-block:: python

    """This module does random stuff."""
    import stack

    @stack.register
    def meet(name : str, greeting : str = 'hello', farewell : str = 'goodbye') -> str:
        '''meet a person'''
        return f'\n{greeting} {name}\n{farewell} {name}'

    # module level function calls...

    if __name__ == '__main__':
        # main code (will run even when using cli commands)...
        stack.cli(desc = __doc__)
        # main code (will NOT run when using cli commands)...

**NOTE:** Adding type hinting to your functions enforces types in the cli and adds positional arg class identifiers in the help docs for the command.

**command usage:**

.. code-block:: console

    python module.py meet foo

**output:**

.. code-block:: console

    hello foo
    goodbye foo

**module help output:**

.. code-block:: console

    usage: module [-h] {meet} ...

    This module does random stuff.

    options:
    -h, --help  show this help message and exit

    commands:
    {meet}
        meet      meet a person

**command help output:**

.. code-block:: console

    usage: module meet [-gr <class 'str'>] [-fa <class 'str'>] [-h] name

    meet(name: str, greeting: str = 'hello', farewell: str = 'goodbye') -> str

    positional arguments:
    name                  <class 'str'>

    options:
    -gr <class 'str'>, --greeting <class 'str'>
                            default: hello
    -fa <class 'str'>, --farewell <class 'str'>
                            default: goodbye
    -h, --help            Show this help message and exit.

cli - using variadic functions
==============================

Variadic functions are compatible with stack cli utility. When calling kwargs from the cli; `key=value` should be used instead of `--` and `-`, these are reserved for default arguments.

**NOTE:** since input is from `stdin` it will always be of type `<string>`, stack will not infer the data type you must infer your needed type within the function.

.. code-block:: python

    """This module does random stuff."""
    import stack

    @stack.register
    def variadic(*args, **kwargs):
        
        print("Positional arguments:")
        for arg in args:
            print(arg)

        print("Keyword arguments:")
        for key, value in kwargs.items():
            print(f"{key} = {value}")

    # module level function calls...

    if __name__ == '__main__':
        # main code (will run even when using cli commands)...
        stack.cli(desc = __doc__)
        # main code (will NOT run when using cli commands)...

**command usage:**

.. code-block:: console

    python module.py variadic 1 2 3 foo=1 bar=2

**output:**

.. code-block:: console

    Positional arguments:
    1
    2
    3
    Keyword arguments:
    foo = 1
    bar = 2

benchy - usage example
======================

The `benchy` decorator is designed to collect performance timing and call info for selected functions. This can be used in combination with `@stack.register`, the decorators are order independent.

.. code-block:: python

    import stack

    @stack.benchy
    @stack.register
    def add(x : int, y : int):
        '''add two integers'''
        return x + y

    @stack.register
    @stack.benchy
    def subtract(x : int, y : int):
        '''subtract two integers'''
        return x - y

    @stack.benchy
    @stack.register
    def calc(x : int, y : int, atype : str = '+') -> int:
        '''caclulates a thing'''
        if atype == '+':
            res = add(x, y)
        elif atype == '-':
            res = subtract(x, y)
        return res

    add(1,2)
    add(2,2)
    subtract(1,2)
    calc(2,3, atype='-')


After the functions have been executed, the benchmark report can be accessed with `stack.benchy.report`.

.. code-block:: python

    # print the benchmark report
    print(stack.benchy.report)

example output

.. code-block:: bash

    {'add': [{'args': [{'type': 'int', 'value': 1}, {'type': 'int', 'value': 2}],
            'benchmark': 0.00015466799959540367,
            'kwargs': None,
            'result': {'type': 'int', 'value': 3}},
            {'args': [{'type': 'int', 'value': 2}, {'type': 'int', 'value': 2}],
            'benchmark': 6.068096263334155e-05,
            'kwargs': None,
            'result': {'type': 'int', 'value': 4}}],
    'calc': [{'args': [{'type': 'int', 'value': 2}, {'type': 'int', 'value': 3}],
            'benchmark': 4.855601582676172e-05,
            'kwargs': {'atype': {'length': 1, 'type': 'str'}},
            'result': {'type': 'int', 'value': 5}}],
    'subtract': [{'args': [{'type': 'int', 'value': 1}, {'type': 'int', 'value': 2}],
            'benchmark': 5.205394700169563e-05,
            'kwargs': None,
            'result': {'type': 'int', 'value': -1}}]}

The output of the benchmark report will adhere to the following format. `function > call records`. Call records consist of `{args, kwargs, result, benchmark}` there will be a record for each call of a given function.

**NOTE:** given an iterable for `arg`, `kwarg`, or `result` the object will be summarized in terms of vector length.

.. code-block:: bash

    {'function_name': [{'args': [{'type': 'arg_type', 'value': int}]
                        'benchmark': float,
                        'kwargs': {'kwarg_name': {'type': 'arg_type', 'length': int, }}
                        'result': {'type': 'arg_type', 'value': float}}]}
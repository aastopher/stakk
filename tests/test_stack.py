from unittest.mock import patch
import inspect, sys, argparse
import stack

##### Methods

# Test 1: this should test the register decorator from stack
# the result should be that the stack.store contains a dictionary for the functions meta info
def test_register():
    def _get_defaults(func):
        """helper function to collect default func args"""

        # get the signature of the function
        sig = inspect.signature(func)

        # collect a dictionary of default argument values
        defaults = {}
        for param in sig.parameters.values():
            if param.default is not inspect.Parameter.empty:
                defaults[param.name] = param.default

        return defaults

    @stack.register
    def func_test(x: int, y: int) -> int:
        """this is a test function"""
        return x + y

    names = inspect.getfullargspec(func_test).args  # collect arg names
    types = inspect.getfullargspec(func_test).annotations  # collect types of args
    defaults = _get_defaults(func_test)
    desc = func_test.__doc__

    expected_dict = {func_test.__name__: {'func':func_test, 
                                        'names':names, 
                                        'types':types, 
                                        'defaults':defaults, 
                                        'desc':desc, 
                                        'variadic':False}}

    assert expected_dict == stack.store.funcs


# Test 2: this should test the register decorator from stack
# the result should be that the su.store contains a proper function dict for variadic functions
def test_register_variadic():
    def _get_meta(func):
        '''helper function to collect default func args'''

        # get the signature of the function
        sig = inspect.signature(func)

        # collect a dictionary of default argument values
        defaults = {}
        names = []
        types = {}
        variadic = False
        for name, param in sig.parameters.items():
            param_kind = param.kind
            variadic = param_kind in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD]

            if param.default is not inspect.Parameter.empty:
                defaults[name] = param.default

            if variadic:
                names.append(str(param))
                types = {}

        desc = func.__doc__

        return names, types, defaults, desc, variadic

    @stack.register
    def func_test(*args, **kwargs):
        """this is a test function"""
        return args, kwargs

    names, types, defaults, desc, variadic = _get_meta(func_test)

    expected_dict = {func_test.__name__: {'func':func_test, 
                                        'names':names, 
                                        'types':types, 
                                        'defaults':defaults, 
                                        'desc':desc, 
                                        'variadic':variadic}}

    assert expected_dict == stack.store.funcs


# Test 3: this should test the cli from stack
# the result should be that the cli property is not None in stack.store
# the cli object should contain commands for any registered functions
def test_cli(monkeypatch):
    # patch the input namespace with the desired command
    namespace = argparse.Namespace(command="", help=True)

    with patch(
        "stack.cli_handler.argparse.ArgumentParser.parse_args", return_value=namespace
    ):
        # patch the sys.exit function so it doesn't exit the interpreter during the test
        monkeypatch.setattr(sys, "exit", lambda *args: None)

        stack.cli()

    assert stack.store.cli is not None
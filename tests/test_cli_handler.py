from unittest.mock import patch, Mock
import pytest
import sys, argparse, asyncio
from stack import cli_handler, meta_handler

#### FIXTURES

@pytest.fixture
def mock_os(monkeypatch):
    mock_os = Mock()
    monkeypatch.setattr(cli_handler,"os",mock_os)  # Assuming the module you're testing is named cli_handler
    return mock_os

#### Tests

def test_cli_desc(capsys, monkeypatch):
    def func_test(
        test, test2: str, test3: str = "test", test4="test2", teest4: str = "test"
    ) -> str:
        pass # pass since we are only testing the function description
    
    stack = meta_handler.Stack()
    stack_id = 'test'
    stack.add_func(stack_id, func_test)

    expected = "Test CLI"
    cli_obj = cli_handler.CLI(expected)
    cli_obj.add_funcs(stack.get_stack(stack_id))

    monkeypatch.setattr(sys, "exit", lambda x: None)

    cli_obj.input = cli_obj.parser.parse_args(["-h"])
    assert cli_obj.parser.description == expected

    cli_obj.parse()
    captured = capsys.readouterr()

    assert expected in captured.out


def test_cli_add_funcs(monkeypatch):
    def func_test(x: int, y: int, c: str = "-") -> int:
        pass # pass since we are only testing the function is added to stack

    expected = func_test.__name__

    namespace = argparse.Namespace(command="func_test", help=True, x=1, y=2, c="+")

    with patch(
        "stack.cli_handler.argparse.ArgumentParser.parse_args", return_value=namespace
    ):
        cli_obj = cli_handler.CLI("description")
        stack = meta_handler.Stack()
        stack_id = 'test'
        stack.add_func(stack_id, func_test)
        cli_obj.add_funcs(stack.get_stack(stack_id))

        monkeypatch.setattr(sys, "exit", lambda *args: None)

        cli_obj.parse()

    assert expected in cli_obj.parser.format_help()

def test_async_func(capsys, monkeypatch):
    async def func_test():
        await asyncio.sleep(0.1)
        print('pass')

    stack = meta_handler.Stack()
    stack_id = 'test'
    stack.add_func(stack_id, func_test)

    cli_obj = cli_handler.CLI("description")
    cli_obj.add_funcs(stack.get_stack(stack_id))

    monkeypatch.setattr(sys, "exit", lambda *args: None)

    namespace = argparse.Namespace(command="func_test")

    monkeypatch.setattr(
        cli_handler.argparse.ArgumentParser, "parse_args", lambda self: namespace
    )

    cli_obj.parse()

    captured = capsys.readouterr()

    assert "pass" in captured.out

def test_variadic_func(capsys, monkeypatch):
    def func_test(*args, **kwargs):
        return 'pass'

    stack = meta_handler.Stack()
    stack_id = 'test'
    stack.add_func(stack_id, func_test)

    cli_obj = cli_handler.CLI("description")
    cli_obj.add_funcs(stack.get_stack(stack_id))

    monkeypatch.setattr(sys, "exit", lambda *args: None)

    def run_cli_parse(namespace_dict):
        namespace = argparse.Namespace(**namespace_dict)

        monkeypatch.setattr(
            cli_handler.argparse.ArgumentParser, "parse_args", lambda self: namespace
        )

        cli_obj.parse()

        captured = capsys.readouterr()

        assert "pass" in captured.out

    # test variadic with args
    run_cli_parse({'command': 'func_test', '*args': ['1', '2', '3', 'foo=1', 'bar=2']})

    # test variadic without args
    run_cli_parse({'command': 'func_test'})

def test_choice_func(capsys, monkeypatch):
    def choice_test(choice: [1,2,3]):
        '''this is a test choice function'''
        print(choice)
        print("pass")

    def choice_none_test(choice: []):
        '''this is a test choice function'''
        print(choice)
        print("pass")

    expected1 = 1
    expected2 = None
    stack = meta_handler.Stack()
    stack_id = 'test'
    stack.add_func(stack_id, choice_test)
    stack.add_func(stack_id, choice_none_test)

    cli_obj = cli_handler.CLI("description")
    cli_obj.add_funcs(stack.get_stack(stack_id))

    monkeypatch.setattr(sys, "exit", lambda *args: None)

    def run_cli_parse(namespace_dict, expected):
        namespace = argparse.Namespace(**namespace_dict)

        monkeypatch.setattr(
            cli_handler.argparse.ArgumentParser, "parse_args", lambda self: namespace
        )

        cli_obj.parse()

        captured = capsys.readouterr()

        assert "pass" in captured.out
        assert str(expected) in captured.out

    # test choice
    run_cli_parse({'command': 'choice_test', 'choice': [expected1]}, expected1)

    # test none list choice
    run_cli_parse({'command': 'choice_none_test', 'choice': [expected2]}, expected2)

def test_bad_choice_func():
    def choice_bad_test(choice: [1,'2',3]):
        '''this is a test choice function'''
        print(choice)
        print("pass")

    stack = meta_handler.Stack()
    stack_id = 'test'
    stack.add_func(stack_id, choice_bad_test)

    cli_obj = cli_handler.CLI("description")

    with pytest.raises(ValueError, match="all types in the choice list must match."):
        cli_obj.add_funcs(stack.get_stack(stack_id))


def test_list_func(capsys, monkeypatch):
    def list_test(test_list: list):
        '''this is a test choice function'''
        print(test_list)
        print("pass")

    input = 'test,list,input'
    expected = "['test,list,input']"
    stack = meta_handler.Stack()
    stack_id = 'test'
    stack.add_func(stack_id, list_test)

    cli_obj = cli_handler.CLI("description")
    cli_obj.add_funcs(stack.get_stack(stack_id))

    monkeypatch.setattr(sys, "exit", lambda *args: None)

    def run_cli_parse(namespace_dict, expected):
        namespace = argparse.Namespace(**namespace_dict)

        monkeypatch.setattr(
            cli_handler.argparse.ArgumentParser, "parse_args", lambda self: namespace
        )

        cli_obj.parse()

        captured = capsys.readouterr()

        assert "pass" in captured.out
        assert expected in captured.out

    # test list
    run_cli_parse({'command': 'list_test', 'test_list': [input]}, expected)

def test_type_list():
    cli_instance = cli_handler.CLI("description")
    
    test_cases = [
        ("test1,test2;test3|test4 test5", ["test1", "test2", "test3", "test4", "test5"]),
        ("test1", ["test1"]),
        ("", [""]),
        ("test1;test2", ["test1", "test2"]),
        ("test1|test2", ["test1", "test2"]),
        ("test1 test2", ["test1", "test2"]),
    ]

    for input_str, expected_output in test_cases:
        result = cli_instance.type_list(input_str)
        assert result == expected_output, f"For input '{input_str}', expected {expected_output} but got {result}"


def test_cli_as_module(mock_os):
    # mock the values of os.path.basename, os.path.dirname, and os.path.split
    module = '__main__.py'
    mock_os.path.basename.return_value = module
    mock_os.path.dirname.return_value = "/path/to/module_directory"
    mock_os.path.split.return_value = ("/path/to", module)
    
    cli_instance = cli_handler.CLI("description")
    
    assert cli_instance.name == module


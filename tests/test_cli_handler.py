from unittest.mock import patch
import sys, argparse, asyncio
from stack import cli_handler, meta_handler

#### Tests

def test_cli_desc(capsys, monkeypatch):
    def func_test(
        test, test2: str, test3: str = "test", test4="test2", teest4: str = "test"
    ) -> str:
        pass # pass since we are only testing the function description
    
    store = meta_handler.Store()
    store.add_func(func_test)

    expected = "Test CLI"
    cli_obj = cli_handler.CLI(expected)
    cli_obj.add_funcs(store.funcs)

    monkeypatch.setattr(sys, "exit", lambda x: None)

    cli_obj.input = cli_obj.parser.parse_args(["-h"])
    assert cli_obj.parser.description == expected

    cli_obj.parse()
    captured = capsys.readouterr()

    assert expected in captured.out


def test_cli_add_funcs(monkeypatch):
    def func_test(x: int, y: int, c: str = "-") -> int:
        pass # pass since we are only testing the function is added to store

    expected = func_test.__name__

    namespace = argparse.Namespace(command="func_test", help=True, x=1, y=2, c="+")

    with patch(
        "stack.cli_handler.argparse.ArgumentParser.parse_args", return_value=namespace
    ):
        cli_obj = cli_handler.CLI("description")
        store = meta_handler.Store()
        store.add_func(func_test)
        cli_obj.add_funcs(store.funcs)

        monkeypatch.setattr(sys, "exit", lambda *args: None)

        cli_obj.parse()

    assert expected in cli_obj.parser.format_help()

def test_async_func(capsys, monkeypatch):
    async def func_test():
        await asyncio.sleep(0.1)
        print('pass')

    store = meta_handler.Store()
    store.add_func(func_test)

    cli_obj = cli_handler.CLI("description")
    cli_obj.add_funcs(store.funcs)

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
        print('pass')

    store = meta_handler.Store()
    store.add_func(func_test)

    cli_obj = cli_handler.CLI("description")
    cli_obj.add_funcs(store.funcs)

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

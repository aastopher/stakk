from stack import meta_handler, cli_handler

### Tests


# Define a test function for the add_func method of the meta_handler.Store class
def test_add_func():
    def func_test1():
        '''
        null function, testing function storage
        '''

    def func_test2():
        '''
        null function, testing function storage
        '''

    expected = ["func_test1", "func_test2"]
    # Create a new meta_handler.Store object
    store = meta_handler.Store()

    # Add test functions to the store
    store.add_func(func_test1)
    store.add_func(func_test2)

    # Assert that the function was added correctly
    assert all(item in store.funcs for item in expected)


# Define a test function for the add_cli method of the meta_handler.Store class
def test_add_cli():
    # Create a new meta_handler.Store object
    store = meta_handler.Store()

    # Create a new cli_handler.CLI object
    cli_obj = cli_handler.CLI("desc")

    # Add the cli_handler.CLI object to the store
    store.add_cli(cli_obj)

    # Assert that the CLI object was added correctly
    assert isinstance(store.cli, cli_handler.CLI)

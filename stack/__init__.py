from stack import cli_handler, meta_handler, bench_handler

# init store
store = meta_handler.Store()
benchy = bench_handler.Benchy()


def register(func):
    '''register a function to the store
    
    :param func: the function to register
    '''
    original_func = getattr(func, "__wrapped__", func)
    store.add_func(original_func)
    return func


def cli(desc = None):
    '''init cli and register to store
    
    :param desc: description of the CLI
    '''

    cli_obj = cli_handler.CLI(desc)

    cli_obj.add_funcs(store.funcs)
    cli_obj.parse()
    store.add_cli(cli_obj)
    return cli_obj

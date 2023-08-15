from stakk import cli_handler, meta_handler, bench_handler

# init stack
stack = meta_handler.Stack()
benchy = bench_handler.Benchy()


def register(stack_id: str):
    '''register a function to a stack with a stack name
    
    :param stack_id: stack identifier to register function with
    '''
    def decorator(func):
        original_func = getattr(func, "__wrapped__", func)
        stack.add_func(stack_id, original_func)
        return func
    return decorator


def cli(stack_id: str, desc : str = None):
    '''init cli and register to a stack
    
    :param stack_id: stack identifier to register to CLI
    :param desc: description of the CLI
    '''

    cli_obj = cli_handler.CLI(desc)

    cli_obj.add_funcs(stack.get_stack(stack_id))
    cli_obj.parse()
    stack.add_cli(cli_obj)
    return cli_obj

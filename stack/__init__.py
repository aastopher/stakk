from stack import cli_handler, meta_handler, bench_handler

# init stack
stack = meta_handler.Stack()
benchy = bench_handler.Benchy()


def register(stack_name: str):
    '''register a function to the stack with a stack name
    
    :param stack_name: name of stack to register function
    '''
    def decorator(func):
        original_func = getattr(func, "__wrapped__", func)
        stack.add_func(stack_name, original_func)
        return func
    return decorator


def cli(stack_name: str, desc : str = None):
    '''init cli and register to stack
    
    :param stack_name: name of stack to register CLI
    :param desc: description of the CLI
    '''

    cli_obj = cli_handler.CLI(desc)

    cli_obj.add_funcs(stack.get_stack(stack_name))
    cli_obj.parse()
    stack.add_cli(cli_obj)
    return cli_obj

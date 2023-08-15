import inspect, os, argparse, sys, asyncio, re

class CLI:
    """object designed for swift module CLI configuration"""

    def __init__(self, desc: str):
        """init top-level parser"""

        # split call source into dir and file name
        dir_name, file_name = os.path.split(sys.argv[0])

        # define cli application name
        if file_name == '__main__.py':
            self.name = os.path.basename(dir_name) # case module
        else:
            self.name = file_name[:-3] # case script

        # define root parser
        self.parser = argparse.ArgumentParser(prog=self.name, description=desc)
        # add commands subparser
        self.subparsers = self.parser.add_subparsers(title="commands", dest="command")
        self.func_dict = {}  # init empty func dict
        self.input = None

    @staticmethod
    def type_list(value):
            '''custom type for list annotation'''
            return re.split(r'[;,| ]', value)

    @staticmethod
    def choice_type(value, choices):
        """custom type for checking types on provided choices."""
        for choice in choices:
            if choice == value or str(choice) == str(value):
                return type(choice)(value)
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid choice.")
    
    @staticmethod
    def custom_partial(func, **partial_kwargs):
        """
        partial function wrapper which retains the original 
        function's name and doc string.
        """
        def partial(*args, **kwargs):
            all_kwargs = {**partial_kwargs, **kwargs}
            return func(*args, **all_kwargs)

        partial.__name__ = func.__name__
        partial.__doc__ = func.__doc__
        return partial


    def add_funcs(self, func_dict):
        """add registered functions to the cli"""

        def is_iterable(obj):
            """check if the object is an iterable."""
            try:
                iter(obj)
                return True
            except TypeError:
                return False
            
        self.func_dict = func_dict  # assign function dictionary property

        # iterate through registered functions
        for func_name, items in func_dict.items():
            names = items['names']  # collect arg names
            types = items['types']  # collect types of arg
            arg_types = [types.get(name, None) for name in names]
            defaults = items['defaults']  # collect default args

            # init arg help and arg description
            help_description = f"execute {func_name} function"

            # collect command description
            signature = inspect.signature(func_dict[func_name]['func'])
            if not signature.parameters:
                description = f"{func_dict[func_name]['func'].__name__}()"

            # collect names and params for a given function
            params = []
            for name, param in signature.parameters.items():
                
                # init choices
                choices = None

                # check if the annotation is an iterable
                if is_iterable(param.annotation) and not isinstance(param.annotation, str):
                    choices = param.annotation
                    arg_type = self.custom_partial(self.choice_type, choices=choices)
                elif param.annotation == list:
                    arg_type = self.type_list
                else:
                    arg_type = param.annotation

                # check if function contains annotations
                if param.annotation != inspect.Parameter.empty:
                    # if default arg exists display in docs
                    if param.default != inspect.Parameter.empty:
                        params.append(
                            f"{name}: {arg_type.__name__ if hasattr(arg_type, '__name__') else arg_type} = {param.default!r}"
                        )
                    else:
                        params.append(f"{name}: {arg_type.__name__ if hasattr(arg_type, '__name__') else arg_type}")
                else:
                    if param.default != inspect.Parameter.empty:
                        params.append(f"{name} = {param.default!r}")
                    else:
                        params.append(f"{name}")

                # define return type if exists for docs
                if "return" in types:
                    description = f"{func_dict[func_name]['func'].__name__}({', '.join(params)}) -> {str(types['return'].__name__)}"
                else:
                    description = f"{func_dict[func_name]['func'].__name__}({', '.join(params)})"

                # define help string
                if items['desc'] is not None:
                    help_description = items['desc']

            # after gathering all the information about the parameters, add the command
            subp = self.subparsers.add_parser(
                func_name,
                help=help_description,
                description=description,
                argument_default=argparse.SUPPRESS,
                add_help=False,
            )

            # create abbreviations for named short name
            abbrevs = set()
            for name, arg_type in zip(names, arg_types):
                choices = None  # reset choices at the beginning of each iteration
                if is_iterable(types.get(name, None)) and not isinstance(types.get(name, None), str):
                    choices = types[name]
                    arg_type = self.custom_partial(self.choice_type, choices=types[name])
                elif types.get(name, None) == list:
                    arg_type = self.type_list

                help_string = ""
                if choices:
                    help_string += f"choices: ({', '.join(map(str, choices))})"
                else:
                    if arg_type is self.type_list:
                        help_string += "type: list"
                    elif arg_type is not None:
                        help_string += f"type: {arg_type.__name__ if hasattr(arg_type, '__name__') else arg_type}"
                if name in defaults:
                    if help_string:
                        help_string += ", "
                    help_string += f"default: {defaults[name]}"

                if name in defaults:
                    # default abbreviation is the first 2 characters
                    short_name = name[:2]
                    # if space is taken define short name as just the list character
                    if short_name in abbrevs:
                        short_name = name[-1]
                    abbrevs.add(short_name)

                    try:
                        subp.add_argument(
                            f"-{short_name}",
                            f"--{name}",
                            metavar=name.upper(),
                            type=arg_type,
                            default=defaults[name],
                            help=help_string,
                            choices=choices if choices else None,
                        )
                    except argparse.ArgumentError:
                        subp.add_argument(
                            f"--{name}",
                            metavar=name.upper(),
                            type=arg_type,
                            default=defaults[name],
                            help=help_string,
                            choices=choices if choices else None,
                        )
                else:
                    # if variadic allow any number of args
                    if items['variadic']:
                        if name == '*args':
                            help_string = '       ex: command arg1 arg2'
                        elif name == '**kwargs':
                            help_string = '    ex: command key=value'
                        subp.add_argument(
                            name, nargs='*', 
                            type=arg_type, 
                            help=help_string
                        )
                    else:
                        subp.add_argument(
                            name, 
                            metavar=name,
                            type=arg_type, 
                            help=help_string,
                            choices=choices if choices else None
                        )

            # override help & place at end of options
            subp.add_argument(
                "-h", "--help", action="help", help="Show this help message and exit."
            )



    def parse(self):
        """initialize parsing args"""

        self.input = self.parser.parse_args()

        # if command in input namespace
        if self.input.command:
            # retrieve function and arg names for given command
            func_meta = self.func_dict[self.input.command]
            args = []
            kwargs = {}

            # if variadic define args and kwargs
            if func_meta['variadic']:
                func = func_meta['func']
                try:
                    for arg in vars(self.input)['*args']:
                        if '=' in arg:
                            k,v = arg.split('=')
                            kwargs[k] = v
                        else:
                            args.append(arg)
                except KeyError:
                    # pass because args & kwargs are already defined empty
                    pass
            else:

                # unpack just the args and function
                func, arg_names = (
                    func_meta['func'],
                    func_meta['names'],
                )
            
                # collect args from input namespace
                args = [getattr(self.input, arg) for arg in arg_names]
            
            # run function with given args and collect any returns
            if asyncio.iscoroutinefunction(func):
                returned = asyncio.run(func(*args, **kwargs))
            else:
                returned = func(*args, **kwargs)

            # print return if not None
            if returned:
                print(returned)

            # exit the interpreter so the entire script is not run
            sys.exit() 

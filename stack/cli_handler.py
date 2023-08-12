import inspect, os, argparse, sys, asyncio


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
    
    def add_funcs(self, func_dict):
        """add registered functions to the cli"""

        def is_iterable_of_strings(obj):
            """Check if the object is an iterable containing only strings."""
            try:
                iter(obj)
                return all(isinstance(item, str) for item in obj)
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

            # collect names and params for a given function
            params = []
            for name, param in signature.parameters.items():
                
                # Check if the annotation is a list (for choices or type hint)
                choices = None
                if is_iterable_of_strings(param.annotation):
                    # This is a list used for choices
                    choices = param.annotation
                    arg_type = str 
                    annotation_name = next(key for key, value in func_dict[func_name]['func'].__annotations__.items() if value == choices)
                else:
                    arg_type = param.annotation
                    annotation_name = arg_type.__name__

                # check if function contains annotations
                if param.annotation != inspect.Parameter.empty:
                    # if default arg exists display in docs
                    if param.default != inspect.Parameter.empty:
                        params.append(
                            f"{name}: {annotation_name} = {param.default!r}"
                        )
                    else:
                        params.append(f"{name}: {annotation_name}")
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

            # After gathering all the information about the parameters, add the command
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
                choices = None  # Reset choices at the beginning of each iteration
                if name in types and is_iterable_of_strings(types[name]):
                    choices = types[name]
                    arg_type = str

                if name in defaults:
                    # default abbreviation is the first 2 characters
                    short_name = name[:2]
                    # if space is taken define short name as just the list character
                    if short_name in abbrevs:
                        short_name = name[-1]
                    abbrevs.add(short_name)

                    help_string = f"default: {defaults[name]}"
                    if choices:
                        help_string += f", choices: ({', '.join(choices)})"

                    try:
                        subp.add_argument(
                            f"-{short_name}",
                            f"--{name}",
                            metavar=str(arg_type) if arg_type is not None else None,
                            type=arg_type,
                            default=defaults[name],
                            help=help_string,
                            choices=choices if choices else None
                        )
                    except argparse.ArgumentError:
                        subp.add_argument(
                            f"--{name}",
                            metavar=str(arg_type) if arg_type is not None else None,
                            type=arg_type,
                            default=defaults[name],
                            help=help_string,
                            choices=choices if choices else None
                        )
                else:
                    help_string = str(arg_type) if arg_type is not None else None
                    if choices:
                        help_string += f", choices: ({', '.join(choices)})"

                    # if variadic allow any number of args
                    if items['variadic']:
                        subp.add_argument(
                            name, nargs='*', 
                            type=arg_type, 
                            help=help_string
                        )
                    else:
                        subp.add_argument(
                            name, 
                            metavar=annotation_name if choices else None, 
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

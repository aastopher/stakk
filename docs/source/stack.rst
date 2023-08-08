stack
-------

**Stack Info**

Stack is designed to stack functions into a register, this registered stack is designed to be consumed by a stack of modular utilities. This pattern is intended to facilitate a lower barrier for entry to configuring command line interfaces, benchmarking tasks, and managing threaded agents.

.. automodule:: sutools
   :members:

store
^^^^^

stack ``store`` instance is a global instance of the ``meta_handler.Bucket`` class. This instance is used to store functions and utility objects, for access across utilities.

benchy
^^^^^^^

stack ``benchy`` instance is a global instance of the ``bench_handler.Benchy`` class. This instance is used as a decorator to collect benchmarking stats for selected functions.
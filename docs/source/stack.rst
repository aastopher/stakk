stack
-------

**Description**

Stack is designed to stack functions into a register, the registered stack is designed to be consumed by a stack of modular utilities. This pattern is intended to facilitate a lower barrier for entry to configure command line interfaces, benchmark tasks, and manage threaded agents.

.. automodule:: sutools
   :members:

store
^^^^^

stack ``store`` instance is a global instance of the ``meta_handler.Bucket`` class. This instance is used to store functions and utility objects, for access across utilities.

benchy
^^^^^^^

stack ``benchy`` instance is a global instance of the ``bench_handler.Benchy`` class. This instance is used as a decorator to collect benchmarking stats for selected functions.
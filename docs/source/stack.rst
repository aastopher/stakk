stakk
-------

**Description**

Register functions to a stack, each stack can be linked to modular utilities. The stack pattern is intended to facilitate a lower barrier for entry to configure command line interfaces, benchmark tasks, and interact with threaded agents.

.. automodule:: stakk
   :members:

stakk
^^^^^

The ``stack`` instance is a global instance of the ``meta_handler.Stack`` class. This instance is used to create stacks for functions and utilities to link.

benchy
^^^^^^^

The ``benchy`` instance is a global instance of the ``bench_handler.Benchy`` class. This instance is used as a decorator to collect benchmarking stats for decorated functions.
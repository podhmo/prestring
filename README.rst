prestring
========================================

.. image:: https://travis-ci.org/podhmo/prestring.svg?branch=master
    :target: https://travis-ci.org/podhmo/prestring


this package is heavily inspired by `srcgen <https://github.com/tomerfiliba/srcgen>`_ .

(todo: gentle introduction)

features
----------------------------------------

- generating code with with-syntax
- string injection after writing string

generating code with with-syntax
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  from prestring.python import PythonModule

  m = PythonModule()

  with m.class_("Point", metaclass="InterfaceMeta"):
      with m.def_("__init__", "self", "value"):
          m.stmt("self.value = value")

      with m.def_("__str__", "self"):
          m.return_("self.value")

output is.

.. code-block:: python

  class Point(object, metaclass=InterfaceMeta)
      def __init__(self, value):
          self.value = value

      def __str__(self):
          return self.value

string injection after writing string
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  from prestring.python import PythonModule

  m = PythonModule()

  with m.def_("setup", "config"):
      import_area = m.submodule()
      m.sep()
      for k in ["a", "b", "c", "d", "e"]:
          import_area.stmt("from .plugins import {k}_plugin", k=k)
          m.stmt("config.activate({}_plugin)", k)

  print(m)


.. code-block:: python

  def setup(config):
      from .plugins import(
          a_plugin,
          b_plugin,
          c_plugin,
          d_plugin,
          e_plugin
      )

      config.activate(a_plugin)
      config.activate(b_plugin)
      config.activate(c_plugin)
      config.activate(d_plugin)
      config.activate(e_plugin)

sub modules
----------------------------------------

- prestring.output
- prestring.python.transform, prestring.text.transform

prestring.output
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

prestring.output can write multiple files.

.. code-block:: python

   import sys
   from prestring.python import Module
   from prestring.output import output, cleanup_all # noqa


   dst = sys.argv[1]
   with output(root=dst) as fs:
       with fs.open("projects/x.txt", "w") as wf:
           print("hello x", file=wf)
           print("bye x", file=wf)

       with fs.open("projects/y.txt", "w") as wf:
           print("hello y", file=wf)
           print("bye y", file=wf)

       with fs.open("projects/z.py", "w", opener=Module) as m:
           with m.def_("hello"):
               m.stmt("print('hello')")

Above code will generate three files. if creating directory is needed, if will be created automatically.

.. code-block:: console

   $ python src/main.py dst
   [D]	create	dst/projects
   [F]	create	dst/projects/x.txt
   [F]	create	dst/projects/y.txt
   [F]	create	dst/projects/z.py

On rerun, no message is displayed. And rerun with `VERBOSE=1` var env to see more detailed output.

.. code-block:: console

   $ python src/main.py dst
   $ VERBOSE=1 python src/main.py dst
   [F]	no change	dst/projects/x.txt
   [F]	no change	dst/projects/y.txt
   [F]	no change	dst/projects/z.py

dry-run
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Running with `CONSOLE=1` varenv or calling with `use_console=True` option, doesn't save files.

.. code-block:: console

   $ CONSOLE=1 python src/main.py dst
   [F]	update	dst/projects/x.txt
   [F]	update	dst/projects/y.txt
   [F]	update	dst/projects/z.py

   # more verbose output
   VERBOSE=1 CONSOLE=1 python src/00/main.py dst/00/create
   # dst/00/create/projects/x.txt
   ----------------------------------------
     hello x
     bye x


   # dst/00/create/projects/y.txt
   ----------------------------------------
     hello y
     bye y


   # dst/00/create/projects/z.py
   ----------------------------------------
     def hello():
         print('hello')

prestring.python.transform, prestring.text.transform
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

the Transform function means converting raw source code (or text) to prestring's code.
And you can use `python -m prestring.python` (or running `python -m prestring.text`) as a CLI command, as follows.

.. code-block:: console

   $ cat hello.py
   def hello(name, *, message: str = "hello world"):
       """
       greeting message
       """
       print(f"{name}: {message}")


   if __name__ == "__main__":
       hello("foo")

   $ python -m prestring.python hello.py

   from prestring.python import PythonModule


   def gen(*, m=None, indent='    '):
       m = m or PythonModule(indent=indent)

       import textwrap
       with m.def_('hello', 'name', '*', 'message: str =  "hello world"'):
           m.docstring(textwrap.dedent("""
           greeting message
           """).strip())
           m.stmt('print(f"{name}: {message}")')

       with m.if_('__name__ == "__main__"'):
           m.stmt('hello("foo")')
       return m


   if __name__ == "__main__":
       m = gen(indent='    ')
       print(m)

Of course, reversible.

.. code-block:: console

   $ python -m prestring.python hello.py > /tmp/gen_hello.py
   $ python /tmp/gen_hello.py
   def hello(name, *, message: str =  "hello world"):
       """
       greeting message
       """
       print(f"{name}: {message}")


   if __name__ == "__main__":
       hello("foo")

limitation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

prestring.python does not support all python grammers (e.g. async definition is not supported, yet). If you want to prestring's expression as first step, prestring.text is probably useful.

.. code-block:: console

   $ python -m prestring.text hello.py
   from prestring.text import Module


   def gen(*, m=None, indent='    '):
       m = m or Module(indent=indent)

       m.stmt('def hello(name, *, message: str = "hello world"):')
       with m.scope():
           m.stmt('"""')
           m.stmt('greeting message')
           m.stmt('"""')
           m.stmt('print(f"{name}: {message}")')
           m.sep()
           m.sep()
       m.stmt('if __name__ == "__main__":')
       with m.scope():
           m.stmt('hello("foo")')

       return m


   if __name__ == "__main__":
       m = gen(indent='    ')
       print(m)

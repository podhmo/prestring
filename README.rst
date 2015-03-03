prestring
========================================

this is heavily inspired by `srcgen <https://github.com/tomerfiliba/srcgen>`_ .

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

  subm = m.submodule("# this is import area ######")
  m.stmt("############################")
  m.sep()
  m.stmt("do_action()")
  m.sep()
  m.stmt("use_foo_module()")
  subm.stmt("from foo import Foo")  # string injection
  m.sep()
  m.stmt("do_action()")

  print(m)

.. code-block:: python

  # this is import area ######
  from foo import Foo
  ############################

  do_action()

  use_foo_module()

  do_action()


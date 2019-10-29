from prestring.python import Module
m = Module()  # noqa
import textwrap
m.sep()


with m.def_('hello', 'name', '*', 'message: str =  "hello world"'):
    m.docstring(textwrap.dedent(
    """
        greeting message
        """
    ))
    m.stmt('print(f"{name}: {message}")')


with m.if_('__name__ == "__main__"'):
    m.stmt('hello("foo")')
print(m)

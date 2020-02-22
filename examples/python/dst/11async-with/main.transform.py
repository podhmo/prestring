from prestring.python import PythonModule


def gen(*, m=None, indent='    '):
    m = m or PythonModule(indent=indent)

    m.import_('typing as t')
    m.import_('asyncio')
    m.from_('functools', 'partial')
    with m.class_('AExecutor'):
        with m.def_('__init__', 'self'):
            m.stmt('self.q = asyncio.Queue()')

        with m.def_('__aenter__', 'self', return_type='t.Callable[..., t.Awaitable[None]]', async_=True):
            with m.def_('loop', async_=True):
                with m.while_('True'):
                    m.stmt('afn = await self.q.get()')
                    with m.if_('afn is None'):
                        m.stmt('self.q.task_done()')
                        m.stmt('break')
                    m.stmt('await afn()')
                    m.stmt('self.q.task_done()')

            m.stmt('asyncio.ensure_future(loop())')
            m.stmt('return self.q.put')

        with m.def_('__aexit__', 'self', 'exc: t.Optional[t.Type[BaseException]]', 'value: t.Optional[BaseException]', 'tb: t.Any', async_=True):
            m.stmt('await self.q.put(None)')
            m.stmt('await self.q.join()')


    with m.def_('arange', 'n: int', return_type='t.AsyncIterator[int]', async_=True):
        with m.for_('i in range(n)'):
            m.stmt('yield i')
            m.stmt('await asyncio.sleep(0.1)')

    with m.def_('run', async_=True):
        with m.with_('AExecutor() as submit', async_=True):
            with m.def_('task', 'tag: str', async_=True):
                with m.for_('i in arange(3)', async_=True):
                    m.stmt('print(tag, i)')

            m.stmt("await submit(partial(task, 'x'))")
            m.stmt("await submit(partial(task, 'y'))")

    with m.def_('main'):
        m.stmt('asyncio.get_event_loop().run_until_complete(run())')

    with m.if_("__name__ == '__main__'"):
        m.stmt('main()')
    return m


if __name__ == "__main__":
    m = gen(indent='    ')
    print(m)

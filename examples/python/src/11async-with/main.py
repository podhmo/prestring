from prestring.python import Module

m = Module()
m.import_("typing", as_="t")
m.import_("asyncio")
m.from_("functools").import_("partial")

with m.class_("AExecutor"):
    with m.def_("__init__", "self"):
        m.stmt("self.q = asyncio.Queue()")
    with m.def_(
        "__aenter__",
        "self",
        return_type="t.Callable[..., t.Awaitable[None]]",
        async_=True,
    ):
        with m.def_("loop", async_=True):
            with m.while_("True"):
                m.stmt("afn = await self.q.get()")
                with m.if_("afn is None"):
                    m.stmt("self.q.task_done()")
                    m.stmt("break")
                m.stmt("afn()", await_=True)
                m.stmt("self.q.task_done()")

        m.stmt("asyncio.ensure_future(loop())")
        m.return_("self.q.put")

    with m.def_(
        "__aexit__",
        "self",
        "exc: t.Optional[t.Type[BaseException]]",
        "value: t.Optional[BaseException]",
        "tb: t.Any",
        return_type=None,
        async_=True,
    ):
        m.stmt("self.q.put(None)", await_=True)
        m.stmt("self.q.join()", await_=True)


with m.def_("arange", "n: int", async_=True, return_type="t.AsyncIterator[int]"):
    with m.for_("i", "range(n)"):
        m.stmt("yield i")
        m.stmt("asyncio.sleep(0.1)", await_=True)


with m.def_("run", async_=True):
    with m.with_("AExecutor()", async_=True, as_="submit"):
        with m.def_("task", "tag: str", async_=True):
            with m.for_("i", "arange(3)", async_=True):
                m.stmt("print(tag, i)")

        m.stmt("submit(partial(task, 'x'))", await_=True)
        m.stmt("submit(partial(task, 'y'))", await_=True)


with m.def_("main"):
    m.stmt("asyncio.get_event_loop().run_until_complete(run())")
with m.if_("__name__ == '__main__'"):
    m.stmt("main()")
print(m)

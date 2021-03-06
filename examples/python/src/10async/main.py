from prestring.python import Module

m = Module()
m.import_("asyncio")
with m.def_("main", async_=True):
    m.stmt("print('Hello ...')")
    m.stmt("asyncio.sleep(0.1)", await_=True)
    m.stmt("print('... World!')")
m.stmt("asyncio.get_event_loop().run_until_complete(main())")
print(m)

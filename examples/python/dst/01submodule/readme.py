def setup(config):
    from .plugins import (
        a_plugin,
        b_plugin,
        c_plugin,
        d_plugin,
        e_plugin,
    )

    config.activate(a_plugin)
    config.activate(b_plugin)
    config.activate(c_plugin)
    config.activate(d_plugin)
    config.activate(e_plugin)

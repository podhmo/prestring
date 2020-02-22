from prestring import Module as _Module


class Module(_Module):
    def sep(self) -> None:
        self.stmt("")

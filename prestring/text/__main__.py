if __name__ == "__main__":
    import sys
    from prestring.python.cli import main_transform
    from prestring.python import Module as PyModule
    from prestring.text import Module
    from prestring.text.transform import transform

    main_transform(
        transform=transform,
        Module=PyModule,
        OutModule=Module,
        filename=sys.modules[transform.__module__].__file__,
    )

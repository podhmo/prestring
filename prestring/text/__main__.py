if __name__ == "__main__":
    import sys
    from prestring.cli import main_transform
    from prestring.python import Module as PyModule
    from prestring.text import Module
    from prestring.text.transform import transform

    main_transform(
        Module=PyModule,
        OutModule=Module,
        transform=transform,
        filename=sys.modules[transform.__module__].__file__,
    )

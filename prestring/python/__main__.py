if __name__ == "__main__":
    import sys
    from prestring.cli import main_transform
    from prestring.python import Module
    from prestring.python.transform import transform

    main_transform(
        transform=transform,
        Module=Module,
        OutModule=Module,
        filename=sys.modules[transform.__module__].__file__,
    )

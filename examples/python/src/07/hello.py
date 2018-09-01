def hello(name, *, message: str = "hello world"):
    """greeting message"""
    print(f"{name}: {message}")


if __name__ == "__main__":
    hello("foo")

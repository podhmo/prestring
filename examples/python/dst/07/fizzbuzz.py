def fizzbuzz(n: int) -> str:
    if n % 3 == 0 and n % 5 == 0:
        return "fizzbuzz"
    elif n % 3 == 0:
        return "fizz"
    elif n % 5 == 0:
        return "buzz"
    else:
        return str(n)


if __name__ == "__main__":
    print(", ".join(fizzbuzz(i) for i in range(1, 21)))

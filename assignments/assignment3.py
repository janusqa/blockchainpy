def transform_data(fn):
    print(fn(10))


transform_data(lambda data: data / 5)


def transform_data2(fn, *args):
    for arg in args:
        print(fn(arg))


transform_data2(lambda data: data / 5, 5, 10, 15, 22, 30)


def transform_data3(fn, *args):
    for arg in args:
        print(f"Result: {fn(arg):^20.2f}")


transform_data3(lambda data: data / 5, 5, 10, 15, 22, 30)

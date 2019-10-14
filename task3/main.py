import concurrent.futures


def function(arg):
    b = 0
    for _ in range(arg):
        b += 1
    return b


def main():
    a = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(function, 10000000) for _ in range(5)]
        for c in concurrent.futures.as_completed(results):
            a += c.result()
    print("----------------------", a)


main()

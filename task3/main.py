from threading import Thread

a = 0


def function(arg):
    b = 0
    for _ in range(arg):
        b += 1

    global a
    a += b


def main():
    threads = []
    for i in range(5):
        thread = Thread(target=function, args=(1000000,))
        thread.start()
        threads.append(thread)

    [t.join() for t in threads]
    print("----------------------", a)


if __name__ == "__main__":
    main()

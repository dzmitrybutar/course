from concurrent.futures import ThreadPoolExecutor
from threading import Lock

a = 0


def function(lock, arg):
    global a
    for _ in range(arg):
        with lock:
            a += 1


def main():
    lock = Lock()
    with ThreadPoolExecutor() as executor:
        for _ in range(5):
            executor.submit(function, lock, 1000000)
    print("----------------------", a)


if __name__ == '__main__':
    main()

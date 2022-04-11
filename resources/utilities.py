import time


def run_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        print(time.time()-start_time)
        return result
    return wrapper

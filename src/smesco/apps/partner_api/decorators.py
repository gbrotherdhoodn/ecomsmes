from multiprocessing.pool import ThreadPool
from functools import wraps


def run_async(func):
    @wraps(func)
    def async_func(*args, **kwargs):
        pool = ThreadPool(processes=1)
        func_th = pool.apply_async(func=func, args=args)
        return func_th.get()
    return async_func

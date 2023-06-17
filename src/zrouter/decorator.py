import time
from functools import wraps 


def paginate(func):
    """数组分页"""
    def wrapper(params):
        data = func(params)
        page_size = params.get('page_size')
        page_num = params.get('page_num')
        page_num = int(page_num) if page_num else 1
        page_size = int(page_size) if page_size else 10
        start = (page_num-1)*page_size
        end = start + page_size
        return {
            'total': len(data),
            'items': data[start: end]
        }
    return wrapper


def trans_type(type_map):
    """ 类型转化
    { 'a': 'int' }
    """
    def decorator(func):
        @wraps(func)
        def wrapper(params, *args, **kwargs):
            params_ = {}
            for k, v in params.items():
                if not v:
                    continue
                if type_map.get(k) == 'int':
                    params_[k] = int(v)
                else:
                    params_[k] = v
            return func(params_, *args, **kwargs)
        return wrapper
    return decorator


def truncate(keys):
    """ 类型转化
    ['task_id', 'instr_id']
    """
    def decorator(func):
        @wraps(func)
        def wrapper(params, *args, **kwargs):
            params_ = {}
            for k, v in params.items():
                if k in keys:
                    params_[k] = v
            return func(params_, *args, **kwargs)
        return wrapper
    return decorator


def validate(requires):
    """ 必填参数验证
    { 'name': '名称' }
    """
    def decorator(func):
        def wrapper(params, *args, **kwargs):
            for require, require_name in requires.items():
                require = params.get(require)
                if isinstance(require, int):
                    pass
                elif not require:
                    raise ValueError('缺少参数:' + require_name)
            return func(params, *args, **kwargs)
        return wrapper
    return decorator


def timeit(func):
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper
from flask import Blueprint, request
from zrouter.exception import MessagePrompt
from inspirare import json as json_
from json import JSONDecodeError
from functools import wraps


class RouterUtility:
    @staticmethod
    def get_params():
        """ 获取路由参数"""
        if request.method == 'GET':
            return json_.to_lowcase(request.args)
        elif request.content_type == 'application/x-www-form-urlencoded':
            return {
                'files': request.files,
                'params': request.form.to_dict()
            }
        else:
            try:
                params = request.get_json()
                return json_.to_lowcase(params)
            except JSONDecodeError:
                return {
                    'data': request.get_data()
                }

    @staticmethod
    def clean_params(params):
        """空值参数清理"""
        return {k: v for k, v in params.items() if v not in ('', 'null') and v is not None}


class Router(Blueprint, RouterUtility):
    """路由"""
    def __init__(self, *args, **kwargs):
        Blueprint.__init__(self, *args, **kwargs)

    @property
    def authorized(self):
        return True

    def add(self, rule, open=False, direct=False, **options):
        def decorator(f):
            def func_wrapper(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    params = self.clean_params(self.get_params())
                    if not self.authorized and not open:
                        return {'code': 401, 'msg': '用户无权限'}
                    try:
                        data = func(params)
                    except MessagePrompt as e:
                        return {'code': 500, 'msg': str(e)}
                    if direct:
                        return data
                    if isinstance(data, dict):
                        data = json_.iter_camel(data)
                    elif isinstance(data, list):
                        data = [json_.iter_camel(item) for item in data]
                    return {'code': 200, 'msg': '操作成功', 'data': data}
                return wrapper
            endpoint = options.pop("endpoint", None)
            self.add_url_rule(rule, endpoint, func_wrapper(f), **options)
        return decorator

from zrouter.exceptions import MessagePrompt
from zrouter.utils.json import to_lowcase, iter_lowcase, iter_camel
from flask import Blueprint, request
from jsonschema.exceptions import ValidationError
from functools import wraps
import random


class ParamMixin:
    @staticmethod
    def get_params():
        if request.method in ['GET', 'DELETE']:
            return to_lowcase({**request.args, **request.view_args})
        elif 'multipart/form-data' in request.content_type:
            return {
                'files': request.files,
                'params': to_lowcase(request.form.to_dict())
            }
        else:
            try:
                params = request.get_json()
                return iter_lowcase(params)
            except:
                return {
                    'data': request.get_data()
                }

    @staticmethod
    def clean_params(params):
        return {k: v for k, v in params.items() if v not in ('', 'null', None)}


class Router(ParamMixin, Blueprint):
    """路由"""

    def __init__(self, *args, **kwargs):
        Blueprint.__init__(self, *args, **kwargs)

    def verify_user(self):
        """用户验证，通过继承覆盖此方法实现具体逻辑"""
        return True

    def handle_error(self, e):
        """错误处理，通过继承覆盖此方法实现具体逻辑"""
        pass

    def wrap_view_func(self, func, direct=False, open=False):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = self.clean_params(self.get_params())
            if not self.verify_user() and not open:
                return {'code': 401, 'msg': '用户无权限'}
            try:
                data = func(**params)
            except MessagePrompt as e:
                return {'code': 500, 'msg': str(e)}
            except ValidationError as e:
                return {'code': 400, 'msg': str(e)}
            except Exception as e:
                self.handle_error(e)
                raise e
            if direct:
                return data
            if isinstance(data, dict):
                data = iter_camel(data)
            elif isinstance(data, list):
                data = [iter_camel(item) for item in data]
            return {'code': 200, 'msg': '操作成功', 'data': data}
        return wrapper

    def add_resource(self, rule, resource_class):
        http_methods = ['get', 'post', 'put', 'delete']

        for method_name in http_methods:
            if method_name in dir(resource_class):
                method =getattr(resource_class, method_name)
                open = getattr(method, 'open', False)
                direct = getattr(method, 'direct', False)
                endpoint = str(random.randint(10000000, 99999999))
                self.add_url_rule(rule, endpoint, self.wrap_view_func(method,
                    open=open, direct=direct), methods=[method.upper()])

    def add_resources(self, resource_map):
        for rule, resource_class in resource_map.items():
            self.add_resource(rule, resource_class)

    def add(self, rule, open=False, direct=False, **options):
        def decorator(f):
            endpoint = options.pop("endpoint", None)
            self.add_url_rule(rule, endpoint, self.wrap_view_func(
                f, open=open, direct=direct), **options)
        return decorator

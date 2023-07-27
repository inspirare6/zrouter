from flask import Blueprint, request
from zrouter.exception import MessagePrompt
from inspirare import json as json_
from jsonschema.exceptions import ValidationError
from functools import wraps
import random


class RouterMixin:
    @staticmethod
    def get_params():
        """ 获取路由参数"""
        if request.method in ['GET', 'DELETE']:
            return json_.to_lowcase(request.args)
        elif 'multipart/form-data' in request.content_type:
            return {
                'files': request.files,
                'params': json_.to_lowcase(request.form.to_dict())
            }
        else:
            try:
                params = request.get_json()
                return json_.iter_lowcase(params)
            except:
                return {
                    'data': request.get_data()
                }

    @staticmethod
    def clean_params(params):
        """空值参数清理"""
        return {k: v for k, v in params.items() if v not in ('', 'null') and v is not None}


class Router(RouterMixin, Blueprint):
    """路由"""

    def __init__(self, *args, **kwargs):
        Blueprint.__init__(self, *args, **kwargs)

    @property
    def authorized(self):
        return True

    def handle_error(self, e):
        pass

    def wrap_func(self, func, direct=False, open=False):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = self.clean_params(self.get_params())
            if not self.authorized and not open:
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
                data = json_.iter_camel(data)
            elif isinstance(data, list):
                data = [json_.iter_camel(item) for item in data]
            return {'code': 200, 'msg': '操作成功', 'data': data}
        return wrapper

    def add_resource(self, rule, resource_class):
        methods = [method for method in dir(resource_class) if callable(
            getattr(resource_class, method))]
        if 'get' in methods:
            endpoint = str(random.randint(10000000, 99999999))
            self.add_url_rule(rule, endpoint, self.wrap_func(
                getattr(resource_class, 'get')), methods=['GET'])
        if 'delete' in methods:
            endpoint = str(random.randint(10000000, 99999999))
            self.add_url_rule(rule, endpoint, self.wrap_func(
                getattr(resource_class, 'delete')), methods=['DELETE'])
        if 'post' in methods:
            endpoint = str(random.randint(10000000, 99999999))
            self.add_url_rule(rule, endpoint, self.wrap_func(
                getattr(resource_class, 'post')), methods=['POST'])

        if 'put' in methods:
            endpoint = str(random.randint(10000000, 99999999))
            self.add_url_rule(rule, endpoint, self.wrap_func(
                getattr(resource_class, 'put')), methods=['PUT'])

    def add_resources(self, resource_map):
        for rule, resource_class in resource_map.items():
            self.add_resource(rule, resource_class)

    def add(self, rule, open=False, direct=False, **options):
        def decorator(f):
            endpoint = options.pop("endpoint", None)
            self.add_url_rule(rule, endpoint, self.wrap_func(
                f, open=open, direct=direct), **options)
        return decorator

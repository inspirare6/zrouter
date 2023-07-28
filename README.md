# zrouter
基于Flask的路由工具库，集成登录验证、权限控制、日志记录、RESTful API快速构建等功能。


## 安装
```shell
pip install zrouter
```

## 基本使用
```python
# 定义路由器
router = Router('body', __name__, url_prefix='/body')


# 添加单一路由
@router.add('/article', methods=['GET'])
def get_article(article_id: int):
    return ArticleMapper.get_json(article_id)

@ router.add('/article', methods=['POST'])
def post_article(article_id: int, data: dict):
    return ArticleMapper.update(article_id, data)


# 添加REST资源
router.add_resource('/metric', MetricResource)


# 批量添加REST资源
router.add_resources({
    '/metric': MetricResource,
    '/sport':  SportResource,
    '/entry': EntryResource,
    '/entry/stat': EntryStatResource,
    '/punch': PunchResource,
    '/punch/stat': PunchStatResource
})
```

## 自定义
通过继承实现用户验证方法、错误处理方法。
```python
from zrouter import Router as Router_


class Router(Router_):
    def verify_user(self):
        # 通过继承在此添加代码，实现用户验证、日志记录
    
    def handle_error(self, e):
        # 通过继承在此添加代码，实现错误处理

```
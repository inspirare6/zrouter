# zrouter

Zen Router library. 


```python
# 定义路由
router = Router('body', __name__, url_prefix='/body')

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
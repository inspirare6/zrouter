from typing import Optional


def R(mapper_class):
    def get(id: Optional[int] = None, page_num: Optional[int] = None, page_size: Optional[int] = None, **kwargs):
        if id:
            return mapper_class.get_json(id)
        else:
            return mapper_class.get_jsons(page_num=page_num, page_size=page_size)

    def post(data: dict):
        mapper_class.add(data)

    def put(id: int, data: dict):
        mapper_class.save(id, data)

    def delete(id: int):
        mapper_class.delete(id=id)

    method_dict = {
        'get': get,
        'post': post,
        'put': put,
        'delete': delete
    }

    return type('Resource', (object,), method_dict)
    

import pydantic
from data_proxy.backend.web.errors import ResourceNotFound

__all__ = (
    "quick_get",
    "quick_create",
    "quick_update"
)


def quick_get(node, **filters):
    res = node.nodes.get(filters)
    if not res:
        raise ResourceNotFound
    return res


def quick_create(node):
    node.save()
    node.refresh()
    return node


def quick_update(node, data:pydantic.BaseModel):
    for key, value in data.dict().items():
        setattr(node, key, value)
    node.save()
    return node
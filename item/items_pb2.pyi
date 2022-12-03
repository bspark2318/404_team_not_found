from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Item(_message.Message):
    __slots__ = ["item_categories", "item_description", "item_id", "item_name", "item_price", "item_weight"]
    ITEM_CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    ITEM_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_NAME_FIELD_NUMBER: _ClassVar[int]
    ITEM_PRICE_FIELD_NUMBER: _ClassVar[int]
    ITEM_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    item_categories: str
    item_description: str
    item_id: str
    item_name: str
    item_price: str
    item_weight: str
    def __init__(self, item_id: _Optional[str] = ..., item_name: _Optional[str] = ..., item_price: _Optional[str] = ..., item_description: _Optional[str] = ..., item_weight: _Optional[str] = ..., item_categories: _Optional[str] = ...) -> None: ...

class Search_ItemID_request(_message.Message):
    __slots__ = ["item_id"]
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    def __init__(self, item_id: _Optional[str] = ...) -> None: ...

class Search_ItemID_response(_message.Message):
    __slots__ = ["item_id"]
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    item_id: Item
    def __init__(self, item_id: _Optional[_Union[Item, _Mapping]] = ...) -> None: ...

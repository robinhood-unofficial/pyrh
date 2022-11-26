"""Test base model file."""


def test_base_model_simplenamespace_simple():
    from pyrh.models.base import BaseModel, UnknownModel

    payload1 = {"a": 10, "b": 15, "c": 20}
    payload2 = {"nested": {"b": 15, "c": 20}}
    payload3 = {"list": [10, {"a": 5, "b": 10, "c": 20}]}

    bm1 = BaseModel(**payload1)
    for k, v in payload1.items():
        assert getattr(bm1, k) == v

    bm2 = BaseModel(**payload2)
    assert bm2.nested == UnknownModel(**payload2["nested"])

    bm3 = BaseModel(**payload3)
    assert bm3.list == [10, UnknownModel(**payload3["list"][1])]


def test_base_model_repr():
    from pyrh.models.base import BaseModel

    bm = BaseModel(a=10)

    assert "BaseModel(a=10)" == str(bm)


def test_base_schema():
    from pyrh.models.base import BaseSchema, UnknownModel

    bm = UnknownModel(a=10)
    load_bm = BaseSchema().load({"a": 10})
    assert bm == load_bm
    assert type(bm) == type(load_bm)

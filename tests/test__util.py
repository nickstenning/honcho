from honcho._util import (
    _get_if_empty,
    _listify
)

def test__get_if_empty():
    assert _get_if_empty("foo", "bar") == "foo"
    assert _get_if_empty(None,  "bar") == "bar"

def test__listify():
    assert _listify("foo")   == ["foo"]
    assert _listify(12345)   == [12345]
    assert _listify(["foo"]) == ["foo"]
    assert _listify([[]])    == [[]]
    assert _listify([])      == []
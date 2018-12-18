from honcho.util.type import sequencify

def test_sequencify():
    assert sequencify("foobar") == ["foobar"]
    assert sequencify([1,2,3])  == [1,2,3]
    assert sequencify([1,2,3])  != [3,2,1]
    assert sequencify([])       == []
    assert sequencify(None)     == [None]

    assert sequencify("foobar", type_ = tuple) == ("foobar",)
    assert sequencify([1,2,3],  type_ = tuple) == (1,2,3)
    assert sequencify([1,2,3],  type_ = tuple) != (3,2,1)
    assert sequencify([],       type_ = tuple) == tuple()
    assert sequencify(None,     type_ = tuple) == (None,)
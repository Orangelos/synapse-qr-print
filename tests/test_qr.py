from synapse_qr_print import render

def test_render_hello():
    res=render("Hello")
    assert isinstance(res, bytes)
    assert len(res)>0

def test_tender_emty():
    res=render("")
    assert isinstance(res, bytes)
    assert len(res)>0






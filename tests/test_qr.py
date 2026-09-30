from synapse_qr_print import render
import pytest
def test_render_hello():
    res=render("Hello")
    assert isinstance(res, bytes)
    assert len(res)>0

def test_render_emty():
    res=render("")
    assert isinstance(res, bytes)
    assert len(res)>0

def test_render_none():
   with pytest.raises(TypeError):
       render(None)

def test_render_kirilic():
    res=render("Привет, как дела?")
    assert isinstance(res, bytes)
    assert len(res)>0
def test_render_long():
    long="Что-то большое."*1000
    with pytest.raises(Exception):
        render(long)





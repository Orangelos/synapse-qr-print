import qrcode
from io import BytesIO
def render(text):
    """ bytes render(str) функция принимает сроку, возвращает картинку в виде байтов, сохранение в ОП"""
    if not isinstance(text, str):
        raise TypeError("text должна быть строкой")
    img=qrcode.make(text)
    buf=BytesIO()
    img.save(buf,format="PNG")
    return buf.getvalue()









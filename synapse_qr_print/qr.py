import qrcode
from io import BytesIO
def render(text):
    """ bytes render(str) функция принимает сроку, возвращает картинку в виде байтов, сохранение на диск отсутствует"""
    img=qrcode.make(text)
    buf=BytesIO()
    img.save(buf,format="PNG")
    return buf.getvalue()









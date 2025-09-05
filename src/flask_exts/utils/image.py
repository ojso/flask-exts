import io
import base64
import qrcode


def generate_qr_code(uri):
    img = qrcode.make(uri)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    qr_code_data_url = f"data:image/png;base64,{img_str}"
    return qr_code_data_url

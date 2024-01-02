import base64

def b64enc(string_data: str) -> str:
    data_byte = string_data.encode('UTF-8')
    return base64.b64encode(data_byte).decode('UTF-8')

def b64dec(string_data: str) -> str:
    return base64.b64decode(string_data).decode('UTF-8')

import hashlib
import socket
import ssl

import requests


def http_get(url: str, headers: dict[str, str] = None, **kwargs):
    http_session = requests.Session()
    if headers:
        http_session.headers.update(headers)
    try:
        response = http_session.get(url=url)
        if not response.status_code == 200:
            raise ValueError(f'http request error, url: {url}, code: {response.status_code}, message: {response.text}')
        return response
    except Exception as e:
        print(f'http request error, reason: {e.__str__()}')

def http_put(url: str, json_data: dict[str, str], headers: dict[str, str] = None, **kwargs):
    http_session = requests.Session()
    if headers:
        http_session.headers.update(headers)
    try:
        response = http_session.put(url=url, json=json_data)
        if not response.status_code == 200:
            raise ValueError(f'http request error, url: {url}, code: {response.status_code}, message: {response.text}')
        return response
    except Exception as e:
        print(f'http request error, reason: {e.__str__()}')

def https_der_cert_bin_retrieve(fqdn: str) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    context = ssl.create_default_context()
    wrappedSocket = context.wrap_socket(sock, server_hostname=fqdn)
    try:
        wrappedSocket.connect((fqdn, 443))
    except Exception as e:
        print(f'socket connect error: {e.__str__()}')
        return
    else:
        der_cert_bin = wrappedSocket.getpeercert(True)
    wrappedSocket.close()
    return der_cert_bin

def cert_bin_to_pem(cert_bin: bytes) -> str:
    pem_cert = ssl.DER_cert_to_PEM_cert(cert_bin)
    return pem_cert

def https_fingerprint_retrieve(der_cert_bin: bytes, hash_type: str = 'sha1') -> str:
    try:
        hash_obj = getattr(hashlib, hash_type)
        thumb = hash_obj(der_cert_bin).hexdigest()
        return thumb
    except AttributeError:
        print(f'not supported algorithms: {hash_type}')

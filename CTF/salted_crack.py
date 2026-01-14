import base64
import binascii
import sys
from getpass import getpass
from Crypto.Cipher import AES, DES, DES3, ARC4
from Crypto.Util.Padding import unpad
# Removed the initial global check for Rabbit support

def decode_base64(s):
    try:
        missing_padding = len(s) % 4
        if missing_padding != 0:
            s += '=' * (4 - missing_padding)
        return base64.b64decode(s)
    except Exception:
        return None

def is_salted(data):
    return data.startswith(b'Salted__')

def evp_bytes_to_key(password, salt, key_len, iv_len):
    from hashlib import md5
    dtot = b''
    d = b''
    while len(dtot) < (key_len + iv_len):
        d = md5(d + password + salt).digest()
        dtot += d
    return dtot[:key_len], dtot[key_len:key_len+iv_len]

def try_decrypt(cipher, ct, key, iv=None):
    try:
        if iv is not None:
            instance = cipher.new(key, cipher.MODE_CBC, iv)
        else:
            instance = cipher.new(key)
        pt = instance.decrypt(ct)
        try:
            # 尝试 unpad，如果失败，返回原始解密数据
            return unpad(pt, cipher.block_size)
        except ValueError:
            # 如果 unpad 失败，可能是 padding 不正确或数据本身就没有 padding
            return pt
    except Exception as e:
        return f'解密失败: {str(e)}'

def main():
    print('请输入密文（base64）：', end='')
    enc = input().strip()
    password = input('请输入密钥：')
    password = password.encode()
    data = decode_base64(enc)
    if not data:
        print('Base64解码失败')
        return
    if not is_salted(data):
        print('不是以"Salted__"开头的加密数据')
        return
    salt = data[8:16]
    ct = data[16:]
    print(f'Salt: {salt.hex()}')
    results = []

    # AES
    for bits in (32, 24, 16):
        key, iv = evp_bytes_to_key(password, salt, bits, 16)
        pt = try_decrypt(AES, ct, key, iv)
        results.append((f'AES-{bits*8}-CBC', pt))

    # DES
    key, iv = evp_bytes_to_key(password, salt, 8, 8)
    pt = try_decrypt(DES, ct, key, iv)
    results.append(('DES-CBC', pt))

    # 3DES
    key, iv = evp_bytes_to_key(password, salt, 24, 8)
    # DES3 key must be 16 or 24 bytes long
    if len(key) == 16 or len(key) == 24:
        pt = try_decrypt(DES3, ct, key, iv)
        results.append(('3DES-CBC', pt))
    else:
        results.append(('3DES-CBC', '密钥长度无效 (需要 16 或 24 字节)'))


    # RC4 (ARC4)
    key, _ = evp_bytes_to_key(password, salt, 16, 0) # RC4 doesn't use IV in this context
    try:
        pt = ARC4.new(key).decrypt(ct)
        results.append(('RC4', pt))
    except Exception as e:
        results.append(('RC4', f'解密失败: {str(e)}'))



    print('\n所有解密尝试结果：')
    # 动态计算列宽
    mode_width = 0
    if results:
        mode_width = max(len(mode) for mode, _ in results)

    for mode, pt in results:
        print(f'{mode:<{mode_width}} : ', end='')
        if isinstance(pt, bytes):
            try:
                # 尝试用utf-8解码，如果失败则显示hex
                print(pt.decode('utf-8', errors='strict'))
            except UnicodeDecodeError:
                print(f'(Hex): {pt.hex()}')
        else:
            # 如果不是bytes，说明是错误信息或者跳过信息
            print(pt)

if __name__ == '__main__':
    main()
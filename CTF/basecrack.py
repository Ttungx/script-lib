import base64
import argparse
import binascii
import string

# 导入第三方库，失败时设为None
try: import base58
except ImportError: base58 = None

try: import pybase62
except ImportError: pybase62 = None

try: import base91
except ImportError: base91 = None

try: import base85, base64 as b85_codec
except ImportError: b85_codec = None

try: import base36
except ImportError: base36 = None

try: import base45
except ImportError: base45 = None
# 不可打印字符比例阈值
rate = 0.1

# Base92 比较特殊，没有广泛使用的标准库，这里我们实现一个简单的版本
# 基于 https://github.com/hickeroar/base92 的 Python 实现思路
def base92_decode(encoded_str):
    base92_chars = r"""!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"""
    base92_map = {char: i for i, char in enumerate(base92_chars)}
    decoded_bytes = bytearray()
    bits = 0
    bit_count = 0

    # 处理可能的转义和特殊情况，简化处理：假设输入是纯Base92字符
    encoded_str = encoded_str.replace('\\\\', '\\').replace('\\"', '"') # 简单处理转义

    # 找到最后一个 ']' 字符，它标志着数据的结束
    end_marker_index = encoded_str.rfind('~')
    if end_marker_index != -1:
        encoded_str = encoded_str[:end_marker_index]

    value = 0
    for char in encoded_str:
        if char not in base92_map:
            # print(f"警告: Base92 解码遇到无效字符 '{char}'")
            continue # 跳过无效字符，或者可以抛出错误

        index = base92_map[char]

        if bit_count == 0:
            value = index
            bit_count = 13 if index < 88 else 6 # 检查是否是最后一个不完整的块
        else:
            value = value * 91 + index
            bit_count += 13

        while bit_count >= 8:
            decoded_bytes.append((value >> (bit_count - 8)) & 0xFF)
            bit_count -= 8
            value &= (1 << bit_count) - 1

    # 处理最后可能剩余的位 (通常在 Base92 中不应该有)
    # if bit_count > 0:
    #     decoded_bytes.append((value << (8 - bit_count)) & 0xFF)

    return bytes(decoded_bytes)


# --- 解码函数 ---
def decode_base16(s):
    try:
        # 尝试去除常见的非 hex 字符，例如空格、换行符
        s_cleaned = ''.join(c for c in s if c in string.hexdigits)
        if len(s_cleaned) % 2 != 0:
             # print("警告: Base16 输入长度为奇数，可能不正确。尝试在末尾添加 '0'。")
             # s_cleaned += '0' # 或者直接返回错误
             raise ValueError("输入长度为奇数")
        decoded = binascii.unhexlify(s_cleaned)
        return decoded
    except Exception as e:
        # print(f"Base16 解码失败: {e}")
        return None

def decode_base32(s):
    try:
        # Base32 需要 padding 到 8 的倍数
        missing_padding = len(s) % 8
        if missing_padding != 0:
            s += '=' * (8 - missing_padding)
        # 尝试大写和小写字母表
        try:
            return base64.b32decode(s, casefold=False) # 标准 Base32
        except binascii.Error:
             return base64.b32decode(s.upper(), casefold=False) # 尝试全大写
    except Exception as e:
        # print(f"Base32 解码失败: {e}")
        return None

def decode_base36(s):
    if base36:
        try:
            # base36.loads 返回整数，需要转为 bytes
            decoded_int = base36.loads(s)
            # 计算需要的字节数
            byte_len = (decoded_int.bit_length() + 7) // 8
            # 处理整数为0的特殊情况
            if byte_len == 0 and decoded_int == 0 and len(s) > 0:
                 byte_len = 1
            return decoded_int.to_bytes(byte_len, 'big')
        except Exception as e:
            # print(f"Base36 解码失败: {e}")
            return None
    return None

def decode_base45(s):
    if base45:
        try:
            return base45.b45decode(s)
        except Exception as e:
            # print(f"Base45 解码失败: {e}")
            return None
    return None

def decode_base58(s):
    if base58:
        try:
            return base58.b58decode(s)
        except Exception as e:
            # print(f"Base58 解码失败: {e}")
            return None
    return None

def decode_base62(s):
    """使用标准Base62字母表(0-9A-Za-z)进行解码，兼容CyberChef等工具"""
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    base = 62
    try:
        num = 0
        for char in s:
            idx = alphabet.find(char)
            if idx == -1:
                return None  # 非法字符
            num = num * base + idx
        # 计算需要的字节数
        byte_len = (num.bit_length() + 7) // 8
        if byte_len == 0 and len(s) > 0:
            byte_len = 1
        return num.to_bytes(byte_len, 'big')
    except Exception:
        return None

def decode_base64(s):
    try:
        # Base64 需要 padding 到 4 的倍数
        missing_padding = len(s) % 4
        if missing_padding != 0:
            s += '=' * (4 - missing_padding)
        # 尝试标准和 URL 安全的 Base64
        try:
            return base64.b64decode(s)
        except binascii.Error:
            return base64.urlsafe_b64decode(s)
    except Exception as e:
        # print(f"Base64 解码失败: {e}")
        return None

def decode_base85(s):
    if not b85_codec: return None
    try: return b85_codec.a85decode(s)
    except Exception:
        try: return b85_codec.b85decode(s)
        except Exception: return None

def decode_base91(s):
    if base91:
        try:
            return base91.decode(s)
        except Exception as e:
            # print(f"Base91 解码失败: {e}")
            return None
    return None

def decode_base92(s):
    try: return base92_decode(s)
    except Exception: return None

# --- 辅助函数 ---
def is_printable(data):
    """检查 bytes 是否主要由可打印 ASCII 字符组成"""
    if not data:
        return False
    # 允许一些非打印字符，但比例不能太高
    printable_chars = set(bytes(string.printable, 'ascii'))
    non_printable_count = sum(1 for byte in data if byte not in printable_chars)
    # 阈值可以调整，例如允许最多 10% 的非打印字符
    return non_printable_count <= len(data) * rate

# --- 主逻辑 ---
def main():
    print("Base解码工具 (支持 Base16, 32, 36, 45, 58, 62, 64, 85, 91, 92)")
    encoded = input("请输入编码字符串: ").strip()
    if not encoded:
        print("输入不能为空")
        return
    decoders = [
        ("Base16", decode_base16),
        ("Base32", decode_base32),
        ("Base36", decode_base36),
        ("Base45", decode_base45),
        ("Base58", decode_base58),
        ("Base62", decode_base62),
        ("Base64", decode_base64),
        ("Base85", decode_base85),
        ("Base91", decode_base91),
        ("Base92", decode_base92),
    ]
    print("\n--- 解码结果 ---\n" + "="*15)
    for name, func in decoders:
        print(f"[{name}]🤡🤡🤡🤡")
        try:
            decoded_bytes = func(encoded)
            if decoded_bytes is not None:
                try:
                    readable = decoded_bytes.decode('utf-8', errors='replace')
                    hexstr = decoded_bytes.hex()
                    print(f"【可读字符串】: \n{readable} \n【十六进制】: \n{hexstr}")
                except Exception as e:
                    print(f"解码错误: {e}", end=" ")
            else:
                print("未能成功解码或结果为空。")
        except Exception as e:
            print(f"解码异常: {e}")
        print("\n" + "-"*15)

if __name__ == "__main__":
    main()
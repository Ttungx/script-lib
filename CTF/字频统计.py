# -*- coding:utf-8 -*-
#Author: mochu7
import sys

alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()_+- =\\{\\}[]"

# 检查命令行参数是否足够
if len(sys.argv) < 2:
    print("请在命令行中提供文件路径，格式为：python 脚本名.py 文件名")
    sys.exit(1)

# 获取命令行传入的文件路径
file_path = sys.argv[1]

try:
    # 打开文件并读取内容
    strings = open(file_path).read()
except FileNotFoundError:
    print(f"未找到文件：{file_path}")
    sys.exit(1)

result = {}
for i in alphabet:
    counts = strings.count(i)
    i = '{0}'.format(i)
    result[i] = counts

res = sorted(result.items(), key=lambda item: item[1], reverse=True)
for data in res:
    print(data)

for i in res:
    flag = str(i[0])
    print(flag[0], end="")
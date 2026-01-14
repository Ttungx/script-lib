import base64

def main():
    string = input("输入原始文本：")
    s2 = input("输入替换后的表：")
    
    s1 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    
    string = string.swapcase()
    
    s3 = str.maketrans(s2, s1)
    
    t = string.translate(s3)
    
    flag = base64.b64decode(t)
    
    print("解码后的结果：", flag.decode('utf-8'))

if __name__ == "__main__":
    main()
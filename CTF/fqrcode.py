import sys
from PIL import Image
from pyzbar.pyzbar import decode


def print_usage():
    print("用法：python qr_decode.py [二维码图片路径]")
    print("示例：python qr_decode.py qrcode.png")


def main():
    # 检查参数数量
    if len(sys.argv) != 2:
        print("错误：缺少图片路径参数")
        print_usage()
        sys.exit(1)

    # 获取图片路径
    img_path = sys.argv[1]

    try:
        # 打开并预处理图片
        with Image.open(img_path) as img:
            # 转换为RGB模式以兼容所有格式
            rgb_img = img.convert('RGB')

            # 解码二维码
            decoded_objects = decode(rgb_img)

            if decoded_objects:
                print(f"成功识别 {len(decoded_objects)} 个二维码：")
                for i, obj in enumerate(decoded_objects, 1):
                    try:
                        content = obj.data.decode('utf-8')
                    except UnicodeDecodeError:
                        content = f"[二进制数据] {obj.data.hex()}"
                    print(f"\n二维码 {i}:")
                    print(f"类型：{obj.type}")
                    print(f"内容：{content}")
            else:
                print("未识别到二维码，请检查：")
                print("1. 图片是否包含有效二维码")
                print("2. 图片是否足够清晰")
    except FileNotFoundError:
        print(f"错误：文件 '{img_path}' 不存在")
        sys.exit(2)
    except Exception as e:
        print(f"解码失败：{str(e)}")
        sys.exit(3)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(0)
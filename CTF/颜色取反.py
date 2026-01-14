from PIL import Image
import sys

def invert_image_colors(input_path, output_path):
    try:
        # 打开图片
        image = Image.open(input_path)

        # 检查图片模式
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            r = r.point(lambda i: 255 - i)
            g = g.point(lambda i: 255 - i)
            b = b.point(lambda i: 255 - i)
            inverted_image = Image.merge('RGBA', (r, g, b, a))
        else:
            inverted_image = image.point(lambda i: 255 - i)

        # 保存处理后的图片
        inverted_image.save(output_path)
        print(f"图片颜色取反完成，已保存到 {output_path}")

    except Exception as e:
        print(f"处理图片时出现错误: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python im.py [文件.jpg/png/bmp]")
        sys.exit(1)

    input_image_path = sys.argv[1]
    # 生成输出文件名，假设输出文件名在原文件名前加 'inverted_'
    import os
    file_dir, file_name = os.path.split(input_image_path)
    output_image_path = os.path.join(file_dir, 'inverted_' + file_name)
    invert_image_colors(input_image_path, output_image_path)
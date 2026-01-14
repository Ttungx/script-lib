import os
import sys
import re
import win32com.client as win32
from pathlib import Path
from natsort import natsorted

# Word 常量定义
wdPageBreak = 7
wdStyleHeading2 = -3  # 标题 2
wdStyleHeading3 = -4  # 标题 3

def get_chapter_number(folder_name):
    """
    解析章节数字用于排序：'第一章' -> 1, '第二章' -> 2
    """
    cn_num = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
              '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    
    match_cn = re.search(r'第([一二三四五六七八九十\d]+)章', folder_name)
    if match_cn:
        num_str = match_cn.group(1)
        if num_str.isdigit():
            return int(num_str)
        elif num_str in cn_num:
            return cn_num[num_str]
    return 999

def sort_files_custom(file_list):
    """
    自定义文件排序逻辑：
    1. 优先按自然顺序排序 (1.doc, 2.doc...)
    2. 将包含 '综合' 的文件强制移动到列表最后
    """
    normal_files = []
    comprehensive_files = []

    for f in file_list:
        # 判断文件名是否包含 "综合"
        if "综合" in f.name:
            comprehensive_files.append(f)
        else:
            normal_files.append(f)

    # 分别对两组文件进行自然排序
    normal_files = natsorted(normal_files, key=lambda x: x.name)
    comprehensive_files = natsorted(comprehensive_files, key=lambda x: x.name)

    # 合并列表，普通在前，综合在后
    return normal_files + comprehensive_files

def merge_documents(root_path):
    root_path = Path(root_path).resolve()
    if not root_path.exists():
        print(f"错误: 路径不存在 - {root_path}")
        return

    output_file = root_path / "总复习资料_合并版.docx"
    
    print("正在启动 Word 进程...")
    word = None
    doc = None
    
    try:
        word = win32.Dispatch('Word.Application')
        word.Visible = False  # 后台运行
        word.DisplayAlerts = False 
        
        doc = word.Documents.Add()
        selection = word.Selection
        
        # 获取并排序章节文件夹
        dirs = [d for d in root_path.iterdir() if d.is_dir()]
        dirs.sort(key=lambda x: (get_chapter_number(x.name), x.name))

        for chapter_dir in dirs:
            print(f"正在处理章节: {chapter_dir.name}")
            
            # --- 1. 插入章节名 (二级标题) ---
            selection.TypeParagraph()
            selection.Style = wdStyleHeading2
            selection.TypeText(chapter_dir.name)
            selection.TypeParagraph()
            
            # --- 2. 获取并自定义排序文件 ---
            files = [f for f in chapter_dir.iterdir() 
                     if f.suffix.lower() in ['.doc', '.docx'] and not f.name.startswith('~$')]
            
            # 使用新的排序逻辑：综合题置后
            sorted_files = sort_files_custom(files)
            
            if not sorted_files:
                print(f"  (该章节无 Word 文件)")
                continue

            for file_path in sorted_files:
                is_comprehensive = "综合" in file_path.name
                print(f"  -> 合并文件: {file_path.name} {'[综合题-已置后]' if is_comprehensive else ''}")
                
                # --- 3. 插入文件名 (三级标题) ---
                selection.Style = wdStyleHeading3
                selection.TypeText(file_path.stem) # 去掉后缀名
                selection.TypeParagraph()
                
                # --- 4. 插入文件内容 ---
                selection.ClearFormatting() 
                try:
                    selection.InsertFile(FileName=str(file_path))
                except Exception as e:
                    print(f"    [错误] 无法插入文件 {file_path.name}: {e}")
                
                # --- 5. 插入分页符 ---
                # 每个文件结束后都另起一页
                selection.InsertBreak(Type=wdPageBreak)

        # 保存并退出
        if output_file.exists():
            try:
                os.remove(output_file)
            except:
                output_file = root_path / f"总复习资料_合并版_{int(os.times()[4])}.docx"

        doc.SaveAs(str(output_file), FileFormat=12)
        print(f"\n==========================================")
        print(f"成功！所有文件已按顺序合并。")
        print(f"综合题已自动放置在各章节末尾。")
        print(f"输出文件: {output_file}")
        print(f"==========================================")

    except Exception as e:
        print(f"\n发生严重错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if doc:
            doc.Close(SaveChanges=False)
        if word:
            word.Quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python script.py [文件夹路径]")
    else:
        target_dir = sys.argv[1]
        merge_documents(target_dir)
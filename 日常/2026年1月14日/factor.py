import os
import sys
import win32com.client as win32
from pathlib import Path

# --- Word 常量 ---
wdStyleHeading4 = -5   # 标题 4
wdStyleNormal = -1     # 正文样式
wdAlignParagraphJustify = 3 # 两端对齐
wdLineSpaceExactly = 4      # 固定值
wdFindStop = 0         # 查找结束停止
wdStory = 6            # 整个文档区域

def format_document_fast(file_path):
    file_path = Path(file_path).resolve()
    if not file_path.exists():
        print(f"错误: 文件不存在 - {file_path}")
        return

    output_file = file_path.parent / f"{file_path.stem}_最终版.docx"
    print(f"正在启动 Word (高性能模式): {file_path.name} ...")

    word = None
    doc = None
    
    try:
        word = win32.Dispatch('Word.Application')
        word.Visible = False
        word.DisplayAlerts = False

        doc = word.Documents.Open(str(file_path))
        selection = word.Selection

        # =======================================================
        # 步骤 1: 全局正文格式化 (通过修改“正文”样式实现，极快)
        # =======================================================
        print(">> 正在应用全局正文格式 (宋体/小四/18磅)...")
        
        # 获取“正文”样式对象
        try:
            normal_style = doc.Styles(wdStyleNormal)
        except:
            # 如果获取失败，尝试获取名为"Normal"或"正文"的样式
            try:
                normal_style = doc.Styles("正文")
            except:
                normal_style = doc.Styles("Normal")

        # 设置字体：宋体, 小四 (12pt)
        normal_style.Font.Name = "宋体"
        normal_style.Font.Size = 12
        normal_style.Font.Color = 0 # 自动颜色(黑色)

        # 设置段落格式
        pf = normal_style.ParagraphFormat
        pf.Alignment = wdAlignParagraphJustify  # 两端对齐
        pf.LeftIndent = 0
        pf.RightIndent = 0
        pf.FirstLineIndent = 0
        pf.SpaceBefore = 0
        pf.SpaceAfter = 0
        pf.LineSpacingRule = wdLineSpaceExactly # 行距固定值
        pf.LineSpacing = 18                     # 18磅
        pf.DisableLineHeightGrid = False        # 对齐到网格(勾选)

        # 强制更新全文档样式（防止某些段落没变）
        doc.UpdateStyles()

        # =======================================================
        # 步骤 2: 匹配关键词并设为标题 4 (使用 Find 替代循环)
        # =======================================================
        keywords = ["单选", "多选", "简答", "单项", "多项"]
        print(f">> 正在搜索关键词并设置标题: {keywords}")

        for kw in keywords:
            # 将光标移到文档开头
            selection.HomeKey(Unit=wdStory)
            
            # 设置查找参数
            find = selection.Find
            find.ClearFormatting()
            find.Text = kw
            find.Forward = True
            find.Wrap = 1 # wdFindContinue (查找到结尾继续从头查? 不，这里我们手动控制)
            find.Wrap = 0 # wdFindStop (查不到就停)
            
            # 开始循环查找
            while True:
                found = find.Execute()
                if not found:
                    break
                
                # 获取当前选中的段落
                current_para = selection.Paragraphs(1)
                
                # 只有当它还不是标题时才修改 (避免把已经是标题1/2/3的改了)
                # 一般标题的大纲级别是 1-9，正文是 10
                if current_para.Format.OutlineLevel == 10: # 10 = 正文文本
                    current_para.Style = wdStyleHeading4
                
                # 将光标折叠到当前查找内容之后，继续向后找
                selection.Collapse(Direction=0) # 0 = wdCollapseEnd

        # =======================================================
        # 保存
        # =======================================================
        doc.SaveAs(str(output_file), FileFormat=12)
        print(f"\n成功！文件已保存: {output_file}")

    except Exception as e:
        print(f"\n!!! 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if doc:
            try:
                doc.Close(SaveChanges=False)
            except:
                pass
        if word:
            try:
                word.Quit()
            except:
                pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python script.py [文档路径]")
    else:
        format_document_fast(sys.argv[1])
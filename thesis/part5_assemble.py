# -*- coding: utf-8 -*-
# 组装所有章节并保存 Word 文档

# 读取各章节模块的内容并 exec 到当前命名空间
import os
_base = os.path.dirname(os.path.abspath(__file__))

for _part in ['part2_ch1_ch3.py', 'part3_ch4_ch5.py', 'part4_ch6_ch7_refs.py']:
    with open(os.path.join(_base, _part), encoding='utf-8') as _f:
        exec(_f.read())

print("正在写入各章节正文...")

# ── 第一章 引言 ──────────────────────────────────────────────
add_chapter1(doc)
doc.add_page_break()
print("  第一章完成")

# ── 第二章 开发工具和技术介绍 ─────────────────────────────────
add_chapter2(doc)
doc.add_page_break()
print("  第二章完成")

# ── 第三章 系统分析 ───────────────────────────────────────────
add_chapter3(doc)
doc.add_page_break()
print("  第三章完成")

# ── 第四章 系统设计 ───────────────────────────────────────────
add_chapter4(doc)
doc.add_page_break()
print("  第四章完成")

# ── 第五章 系统实现 ───────────────────────────────────────────
add_chapter5(doc)
doc.add_page_break()
print("  第五章完成")

# ── 第六章 系统测试 ───────────────────────────────────────────
add_chapter6(doc)
doc.add_page_break()
print("  第六章完成")

# ── 第七章 结束语 ─────────────────────────────────────────────
add_chapter7(doc)
doc.add_page_break()
print("  第七章完成")

# ── 参考文献 ──────────────────────────────────────────────────
add_references(doc)
print("  参考文献完成")

# ── 保存文档 ──────────────────────────────────────────────────
doc.save(OUTPUT_PATH)
print(f"\n✅ Word 文档已生成：{OUTPUT_PATH}")

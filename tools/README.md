# 发布工具

`tools/` 下代码采用 MIT License。

## Word 转 Markdown

`docx_to_markdown.py` 用于把本项目的 Word 工作稿转换成便于审阅和版本管理的 Markdown。它支持标题、段落、简单列表、普通表格和样章截取，不是通用 Word 渲染器。

运行依赖：Python 3.10+、`python-docx`。

## 公开安全检查

在提交或发布前运行：

```bash
python3 tools/check_public_repo.py
```

检查会拒绝常见账户目录、Word/PDF/图片等潜在原始材料、本机绝对路径、临时下载链接和已知内部证据标记。它只能降低误发风险，不能替代人工审核。

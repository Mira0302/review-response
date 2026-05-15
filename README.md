---
title: ReviewResponse
emoji: 📝
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.14.0
app_file: app.py
pinned: false
---

# ReviewResponse - 审稿意见回复助手

粘贴论文 + 审稿意见，AI 自动生成逐条回复草稿和修改对照表。

## 使用方式

1. 上传论文文件（支持 PDF / Word / Markdown / 纯文本）或粘贴论文正文
2. 粘贴审稿意见（支持文件上传或直接粘贴）
3. 点击「生成回复信」
4. 审核生成的回复信和修改对照表，复制使用

## 本地运行

```bash
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入你的 DeepSeek API Key
python app.py
```

## 环境变量

| 变量 | 说明 |
|------|------|
| DEEPSEEK_API_KEY | DeepSeek API 密钥（必填） |

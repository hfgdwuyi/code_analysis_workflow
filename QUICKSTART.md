# 快速开始指南

## 5 分钟快速上手

### 1️⃣ 前置条件检查

确保您的系统已安装：
- Python 3.11 或更高版本
- Ollama
- Git

### 2️⃣ 本地设置 (1 分钟)

```bash
# 给脚本执行权限
chmod +x setup.sh

# 运行设置脚本（自动检查依赖和安装）
./setup.sh
```

### 3️⃣ 启动 Ollama 服务 (1 分钟)

在新的终端窗口运行：
```bash
ollama serve
```

首次运行时，系统会自动下载 deepseek-coder:6.7b 模型（约 3.8GB）。

### 4️⃣ 本地测试分析 (2 分钟)

```bash
# 测试分析脚本
python3 analyze.py

# 或使用自定义参数
python3 analyze.py --host http://localhost:11434 --model deepseek-coder:6.7b --directory .
```

输出文件：
- `analysis-results.json` - 详细的 JSON 结果
- `analysis-report.md` - 可读的 Markdown 报告

### 5️⃣ 推送到 GitHub (1 分钟)

```bash
# 初始化 git（如果未初始化）
git init

# 添加文件
git add .

# 提交
git commit -m "Add GitHub Actions code analysis workflow"

# 推送到 GitHub
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 6️⃣ 在 GitHub 上运行工作流

1. 打开 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **Code Analysis with Ollama**
4. 点击 **Run workflow** 按钮
5. 点击 **Run workflow** 确认

## 工作流触发方式

### 🚀 手动运行

```
GitHub 仓库 → Actions → Code Analysis with Ollama → Run workflow
```

可在运行时指定：
- **ollama_host**: Ollama 服务器地址（默认: http://localhost:11434）
- **model**: 使用的模型（默认: deepseek-coder:6.7b）

### ⏰ 自动定时运行

默认配置：**每天 UTC 时间 2:00 AM** 运行

修改时间表（编辑 `.github/workflows/code-analysis.yml`）：
```yaml
schedule:
  - cron: '0 9 * * *'  # 改为每天 9:00 AM UTC
```

## 查看分析结果

### 在 GitHub 上

1. 打开完成的工作流运行
2. 滚动到底部找 **Artifacts** 部分
3. 下载 **analysis-results**
4. 解压并查看：
   - `analysis-report.md` - 报告摘要
   - `analysis-results.json` - 详细数据

### 本地查看

```bash
# 查看报告
cat analysis-report.md

# 查看详细结果（使用 json 查看器）
cat analysis-results.json | python3 -m json.tool
```

## 常见问题

### Q: 如何改变分析的代码范围？

编辑 `.github/workflows/code-analysis.yml` 中的 `exclude_dirs` 部分：

```python
exclude_dirs = {'.git', '.github', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}
```

### Q: 如何使用不同的 AI 模型？

```bash
# 拉取其他模型
ollama pull llama2
ollama pull mistral
ollama pull neural-chat

# 在工作流运行时选择
GitHub Actions → Run workflow → 输入模型名称
```

### Q: 分析太慢了怎么办？

1. **使用更小的模型**：`neural-chat:7b` 或 `mistral` 更快
2. **跳过大文件**：编辑 `max_file_size` 参数
3. **并行分析**：修改工作流使用 matrix 策略

### Q: 如何连接到远程 Ollama 服务器？

1. 在远程服务器启用外部访问：
   ```bash
   OLLAMA_HOST=0.0.0.0:11434 ollama serve
   ```

2. 在工作流运行时指定地址：
   ```
   ollama_host: http://remote-server-ip:11434
   ```

## 重要注意事项

⚠️ **安全**
- 不要将敏感信息提交到仓库
- 使用 GitHub Secrets 存储敏感配置

⚠️ **对于 GitHub 托管运行器**
- GitHub 托管运行器（ubuntu-latest）无法访问本地 Ollama
- 需要使用自托管运行器或外部 Ollama 服务

⚠️ **模型大小**
- deepseek-coder:6.7b 约 3.8GB
- 确保有足够的磁盘空间

## 下一步

- 📖 详细文档：查看 [README.md](README.md)
- 🔧 自定义分析：编辑 `analyze.py` 中的 prompt
- 🚀 生产部署：设置自托管 GitHub Actions 运行器

## 获取帮助

遇到问题？

1. 检查 Ollama 是否运行：`curl http://localhost:11434/api/tags`
2. 查看工作流日志：GitHub Actions 运行详情
3. 检查模型是否安装：`ollama list`

---

**祝您使用愉快！** 🎉

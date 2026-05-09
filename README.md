# GitHub Actions Code Analysis Workflow

这是一个自动化的代码分析工作流，使用 Ollama 和 DeepSeek Coder 模型来分析仓库中的代码文件。

## 功能特性

✨ **智能代码分析**
- 自动扫描仓库中的所有代码文件
- 支持 20+ 编程语言
- 提供详细的代码分析报告

🚀 **灵活的触发方式**
- **手动触发** (Workflow Dispatch): 在 GitHub 上手动运行
- **定时触发** (Schedule): 每天自动运行 (默认 UTC 2:00 AM)
- 自定义 Ollama 服务器地址和模型

📊 **详细的分析报告**
- 生成 JSON 格式的详细分析结果
- 生成 Markdown 格式的可读性报告
- 包含统计摘要和关键洞察

🔧 **灵活配置**
- 支持自定义 Ollama 服务器地址
- 支持选择不同的模型
- 自动过滤大型文件和不相关目录

## 前置要求

### 本地部署

1. **安装 Ollama**
   ```bash
   # macOS
   brew install ollama
   ```

2. **启动 Ollama 服务**
   ```bash
   ollama serve
   ```

3. **拉取 DeepSeek Coder 模型**
   ```bash
   ollama pull deepseek-coder:6.7b
   ```

### GitHub 配置

1. 确保工作流文件已在 `.github/workflows/code-analysis.yml`
2. 将仓库推送到 GitHub
3. 启用 GitHub Actions

## 使用方法

### 方式 1: 手动触发

1. 打开你的 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **Code Analysis with Ollama** 工作流
4. 点击 **Run workflow** 按钮
5. (可选) 自定义 Ollama 服务器地址和模型
6. 点击 **Run workflow** 确认

### 方式 2: 定时触发

工作流会在每天 UTC 时间 2:00 AM 自动运行。

修改触发时间：编辑 `.github/workflows/code-analysis.yml` 中的 schedule 部分：

```yaml
schedule:
  - cron: '0 2 * * *'  # 修改时间表达式
```

Cron 表达式格式: `分钟 小时 日期 月份 星期`

例子:
- `0 9 * * *` - 每天 9:00 AM
- `0 */12 * * *` - 每 12 小时
- `0 0 * * 1` - 每周一午夜

## 工作流配置选项

### 手动运行时的输入参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `ollama_host` | Ollama 服务器地址 | `http://localhost:11434` |
| `model` | 要使用的模型 | `deepseek-coder:6.7b` |

### 支持的编程语言

Python, JavaScript, TypeScript, JSX, TSX, Java, C++, C, Go, Rust, PHP, Ruby, Shell, YAML, JSON, XML, HTML, CSS, SQL

## 输出结果

### 生成的文件

工作流完成后会生成：

- **`analysis-results.json`** - 详细的 JSON 格式分析结果
- **`analysis-report.md`** - Markdown 格式的易读报告

### 访问结果

1. 打开工作流运行详情
2. 滚动到底部找到 **Artifacts** 部分
3. 点击 **analysis-results** 下载文件

## 分析内容

每个文件的分析包括：

1. **Purpose** - 代码的目的和功能
2. **Key Components** - 主要函数、类和它们的角色
3. **Dependencies** - 外部库和依赖
4. **Issues** - 潜在问题、改进建议
5. **Summary** - 简洁的 1-2 句总结

## 高级配置

### 连接到远程 Ollama 服务器

如果 Ollama 运行在另一台机器上：

1. 确保 Ollama 从外部可访问：
   ```bash
   OLLAMA_HOST=0.0.0.0:11434 ollama serve
   ```

2. 在运行工作流时设置正确的地址：
   ```
   http://your-server-ip:11434
   ```

### 使用其他模型

替换为其他兼容的模型：

```bash
ollama pull codellama:13b
ollama pull neural-chat:latest
```

然后在工作流中指定模型名称。

## 故障排除

### ❌ 连接失败

**问题**: "Failed to connect to Ollama"

**解决方案**:
1. 确保 Ollama 正在运行: `ollama serve`
2. 检查服务器地址是否正确
3. 确保防火墙允许连接

### ❌ 模型不可用

**问题**: "Model deepseek-coder:6.7b not found"

**解决方案**:
```bash
ollama pull deepseek-coder:6.7b
ollama list  # 查看已安装的模型
```

### ❌ 分析超时

**问题**: 分析时间过长或超时

**解决方案**:
1. 检查模型大小和硬件容量
2. 减少目录中的大型文件
3. 考虑使用更小的模型

## 本地测试

在提交到 GitHub 之前，可以本地测试工作流：

```bash
# 安装流程
python3 -m pip install requests

# 运行分析脚本
python3 analyze.py
```

## 安全考虑

⚠️ **重要**：
- 不要将敏感信息（API密钥、密码等）提交到仓库
- Ollama 服务器应该在受保护的网络中运行
- 定期更新 Ollama 和模型

## 计费和资源

✋ **本地部署**：
- Ollama 是开源的，可以免费使用
- 需要足够的本地硬件资源（至少 8GB RAM）

## 许可证

MIT License

## 支持

有问题或建议？请提交 Issue 或 Pull Request。

---

**更新**: 2026年5月9日  
**版本**: 1.0.0

# 深度自定义指南

## 目录

1. [修改分析 Prompt](#修改分析-prompt)
2. [支持更多编程语言](#支持更多编程语言)
3. [自定义输出格式](#自定义输出格式)
4. [调整分析参数](#调整分析参数)
5. [集成其他工具](#集成其他工具)
6. [性能优化](#性能优化)

## 修改分析 Prompt

### 位置
编辑 `analyze.py` 中的 `analyze_file` 方法，修改 `prompt` 变量。

### 当前 Prompt 结构
```python
prompt = f"""Please analyze this code file:

File: {filepath}
Language: {lang}

Code:
```
{content}
```

Provide analysis in the following format:
1. **Purpose**: What does this code do?
2. **Key Components**: Main functions/classes and their roles
3. **Dependencies**: External libraries and dependencies
4. **Issues**: Any potential issues, improvements, or concerns
5. **Summary**: Brief 1-2 sentence summary
"""
```

### 自定义示例

**示例 1: 安全分析焦点**
```python
prompt = f"""Analyze this code for security issues:

File: {filepath}

Code:
```
{content}
```

Focus on:
1. **Security Issues**: Identify vulnerabilities, input validation problems
2. **Authentication/Authorization**: Check access control
3. **Data Protection**: Evaluate encryption, data handling
4. **Dependencies**: Check for known vulnerable packages
5. **Recommendations**: Suggest security improvements
"""
```

**示例 2: 性能分析焦点**
```python
prompt = f"""Analyze this code for performance:

File: {filepath}

Code:
```
{content}
```

Analyze:
1. **Performance Bottlenecks**: Identify slow operations
2. **Complexity**: Time and space complexity assessment
3. **Optimizations**: Suggest improvements
4. **Caching Opportunities**: Identify cacheable operations
5. **Summary**: Overall performance rating
"""
```

**示例 3: 可维护性分析**
```python
prompt = f"""Analyze code quality and maintainability:

File: {filepath}

Code:
```
{content}
```

Evaluate:
1. **Code Quality**: Readability, naming conventions
2. **Documentation**: Comment quality, docstrings
3. **Structure**: Architecture, design patterns
4. **Testing**: Test coverage assessment
5. **Recommendations**: Improvement suggestions
"""
```

## 支持更多编程语言

编辑 `analyze.py` 中的 `CODE_EXTENSIONS` 字典：

```python
CODE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    # 添加新语言
    '.scala': 'Scala',
    '.kotlin': 'Kotlin',
    '.swift': 'Swift',
    '.m': 'Objective-C',
    '.cs': 'C#',
    '.vb': 'Visual Basic',
    '.lua': 'Lua',
    '.pl': 'Perl',
    '.groovy': 'Groovy',
}
```

## 自定义输出格式

### 修改报告生成

编辑 `analyze.py` 中的 `_generate_report` 方法。

**示例: 生成 HTML 报告**
```python
def generate_html_report(self, results, summary_stats):
    """Generate HTML format report."""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Code Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .file { border: 1px solid #ddd; padding: 10px; margin: 10px 0; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Code Analysis Report</h1>
    <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    <h2>Summary</h2>
    <p>Total Files: {summary_stats['total']}</p>
    <p>Analyzed: {summary_stats['analyzed']}</p>
    """
    
    for filepath, result in results.items():
        html += f"<div class='file'><h3>{filepath}</h3>"
        if result['status'] == 'success':
            html += f"<pre>{result['analysis']}</pre>"
        else:
            html += f"<p class='error'>Error: {result.get('error', 'Unknown')}</p>"
        html += "</div>"
    
    html += "</body></html>"
    return html
```

## 调整分析参数

### 在 `.github/workflows/code-analysis.yml` 中调整

```yaml
- name: Analyze code files
  env:
    OLLAMA_HOST: ${{ github.event.inputs.ollama_host || 'http://localhost:11434' }}
    MODEL: ${{ github.event.inputs.model || 'deepseek-coder:6.7b' }}
    # 添加环境变量
    MAX_FILE_SIZE: '100000'  # 增大文件大小限制
    TEMPERATURE: '0.3'       # 降低创意度，更一致的输出
    TIMEOUT: '180'           # 设置超时时间
```

### 更新 Python 脚本以支持这些变量

```python
import os

MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '50000'))
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.1'))
TIMEOUT = int(os.getenv('TIMEOUT', '120'))

self.analyzer = CodeAnalyzer(
    ollama_host, 
    model, 
    max_file_size=MAX_FILE_SIZE
)
```

## 集成其他工具

### 集成 LLama.cpp 而不是 Ollama

```python
import subprocess
import json

def analyze_with_llamacpp(filepath, model_path):
    """Use llama.cpp directly instead of Ollama."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    prompt = f"Analyze this code:\n{content}"
    
    result = subprocess.run([
        './main',
        '-m', model_path,
        '-p', prompt,
        '-n', '500'
    ], capture_output=True, text=True)
    
    return result.stdout
```

### 集成 Together AI API

```python
import together

def analyze_with_together(filepath, api_key):
    """Use Together AI instead of local Ollama."""
    together.api_key = api_key
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    output = together.Complete.create(
        prompt=f"Analyze:\n{content}",
        model="deepseek-1.3b",
        max_tokens=1024,
    )
    
    return output['output']['choices'][0]['text']
```

## 性能优化

### 1. 并行分析（对于多文件）

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def analyze_repository_parallel(self, directory: str, max_workers: int = 4):
    """Analyze files in parallel."""
    files = self.get_code_files(directory)
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(self.analyze_file, f): f for f in files
        }
        
        for future in as_completed(future_to_file):
            filepath = future_to_file[future]
            results[filepath] = future.result()
    
    return results
```

### 2. 缓存分析结果

```python
import hashlib
import pickle

class CachedCodeAnalyzer(CodeAnalyzer):
    def __init__(self, *args, cache_file: str = '.cache/analysis.pkl', **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_file = cache_file
        self.cache = self.load_cache()
    
    def load_cache(self):
        """Load cache from disk."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        return {}
    
    def save_cache(self):
        """Save cache to disk."""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)
    
    def analyze_file(self, filepath: str):
        """Analyze with caching."""
        # 计算文件哈希
        with open(filepath, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        cache_key = f"{filepath}:{file_hash}"
        
        # 检查缓存
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 执行分析
        result = super().analyze_file(filepath)
        
        # 保存到缓存
        self.cache[cache_key] = result
        self.save_cache()
        
        return result
```

### 3. 降低模型温度以加快速度

```yaml
# 在工作流中
"temperature": 0.0,  # 完全确定性，更快
# 而不是
"temperature": 0.1,  # 更多变化，更慢
```

## 跳过大文件

```python
# 编辑 analyze.py

def get_code_files(self, directory: str = '.', min_size: int = 100) -> List[str]:
    """Find code files with size filtering."""
    files = []
    max_size = self.max_file_size
    
    for root, dirs, filenames in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
        
        for filename in filenames:
            ext = Path(filename).suffix.lower()
            if ext in CODE_EXTENSIONS:
                filepath = os.path.join(root, filename)
                size = os.path.getsize(filepath)
                
                # 过滤空文件和过大文件
                if min_size <= size <= max_size:
                    files.append(filepath)
    
    return sorted(files)
```

## 监控和日志

```python
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 在分析中使用
logger.info(f"Analyzing {filepath}")
logger.error(f"Failed to analyze {filepath}: {error}")
```

---

有更多定制需求？查看 [README.md](README.md) 了解更多信息！

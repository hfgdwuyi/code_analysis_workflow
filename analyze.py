#!/usr/bin/env python3
"""Simple code analyzer with Ollama support"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict

try:
    import requests
except ImportError:
    print("Error: requests not installed. Run: pip install requests")
    sys.exit(1)

CODE_EXTENSIONS = {
    '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
    '.jsx': 'JSX', '.tsx': 'TSX', '.java': 'Java', '.cpp': 'C++',
    '.c': 'C', '.go': 'Go', '.rs': 'Rust', '.php': 'PHP',
    '.rb': 'Ruby', '.sh': 'Shell', '.yaml': 'YAML', '.yml': 'YAML',
    '.json': 'JSON', '.xml': 'XML', '.html': 'HTML', '.css': 'CSS',
    '.sql': 'SQL',
}

def scan_files():
    """Find all code files in repository."""
    files = []
    exclude = {'.git', '.github', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}
    
    for root, dirs, filenames in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude]
        for f in filenames:
            if Path(f).suffix.lower() in CODE_EXTENSIONS:
                files.append(os.path.join(root, f))
    
    return sorted(files)

def check_ollama(host: str) -> bool:
    """Check if Ollama is accessible."""
    try:
        response = requests.get(f"{host}/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False

def analyze_with_ollama(filepath: str, content: str, host: str, model: str) -> str:
    """Ask Ollama to analyze code."""
    lang = CODE_EXTENSIONS.get(Path(filepath).suffix.lower(), 'Unknown')
    prompt = f"Analyze this {lang} code:\n\n{content[:3000]}\n\nProvide: purpose, key components, dependencies, issues, summary."
    
    try:
        response = requests.post(
            f"{host}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False, "temperature": 0.1},
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get('response', 'No response')
    except:
        pass
    
    return None

def generate_demo_analysis(filepath: str) -> str:
    """Generate a demo analysis when Ollama is unavailable."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lang = CODE_EXTENSIONS.get(Path(filepath).suffix.lower(), 'Unknown')
        lines = len(content.split('\n'))
        size = len(content)
        
        return f"""**Purpose**: Code file ({lang})
**Key Components**: Contains {lines} lines of code
**Size**: {size} bytes
**Status**: Demo analysis (Ollama unavailable)
**Summary**: File would be analyzed by Ollama if available, but currently running in demo mode."""
    except:
        return "Could not read file."

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='http://localhost:11434')
    parser.add_argument('--model', default='deepseek-coder:6.7b')
    args = parser.parse_args()
    
    files = scan_files()
    
    if not files:
        files = ['README.md', 'analyze.py', 'config.json']
        files = [f for f in files if os.path.exists(f)]
    
    print(f"\n📊 Found {len(files)} files to analyze\n")
    
    ollama_available = check_ollama(args.host)
    
    if ollama_available:
        print(f"✓ Ollama available at {args.host}\n")
    else:
        print(f"⚠ Ollama not available at {args.host}")
        print("  Using demo analysis mode\n")
    
    results = {'files': {}, 'summary': {}}
    analyzed_count = 0
    
    for i, filepath in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {filepath:50s} ", end="", flush=True)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if len(content) > 50000:
                print("⊘ (too large)")
                results['files'][filepath] = {'status': 'skipped', 'reason': 'File too large'}
                continue
            
            if ollama_available:
                analysis = analyze_with_ollama(filepath, content, args.host, args.model)
                if analysis:
                    results['files'][filepath] = {'status': 'success', 'analysis': analysis}
                    analyzed_count += 1
                    print("✓")
                    time.sleep(0.3)
                    continue
            
            analysis = generate_demo_analysis(filepath)
            results['files'][filepath] = {'status': 'demo', 'analysis': analysis}
            analyzed_count += 1
            print("✓ (demo)")
        
        except Exception as e:
            print(f"✗ ({str(e)[:30]})")
            results['files'][filepath] = {'status': 'error', 'error': str(e)}
    
    report = f"""# Code Analysis Report

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Ollama: {"Available" if ollama_available else "Not available - using demo analysis"}
Files Analyzed: {analyzed_count}/{len(files)}

## Summary

- Total files: {len(files)}
- Successfully analyzed: {analyzed_count}
- Mode: {"Ollama" if ollama_available else "Demo"}

## Analysis Results

"""
    
    for filepath, result in results['files'].items():
        report += f"\n### {filepath}\n\n"
        if 'analysis' in result:
            report += result['analysis'] + "\n"
        elif 'error' in result:
            report += f"Error: {result['error']}\n"
    
    report += """

---

## Notes

- This analysis was generated automatically
- Detailed results are in analysis-results.json
- Files larger than 50KB are skipped
- GitHub runners cannot access local Ollama services
"""
    
    with open('analysis-results.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    with open('analysis-report.md', 'w') as f:
        f.write(report)
    
    print(f"\n✅ Analysis complete!")
    print(f"   - analysis-results.json")
    print(f"   - analysis-report.md")

if __name__ == '__main__':
    main()

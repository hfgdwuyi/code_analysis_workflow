#!/usr/bin/env python3
"""
Local code analysis script for testing before pushing to GitHub Actions
"""

import os
import requests
import json
import sys
import argparse
import time
from pathlib import Path
from typing import Dict, List, Optional

# Supported code file extensions
CODE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.jsx': 'JSX',
    '.tsx': 'TSX',
    '.java': 'Java',
    '.cpp': 'C++',
    '.c': 'C',
    '.go': 'Go',
    '.rs': 'Rust',
    '.php': 'PHP',
    '.rb': 'Ruby',
    '.sh': 'Shell',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.json': 'JSON',
    '.xml': 'XML',
    '.html': 'HTML',
    '.css': 'CSS',
    '.sql': 'SQL',
}

class CodeAnalyzer:
    def __init__(self, ollama_host: str, model: str, max_file_size: int = 50000):
        """
        Initialize the code analyzer.
        
        Args:
            ollama_host: URL of the Ollama server
            model: Model name to use for analysis
            max_file_size: Maximum file size in characters to analyze
        """
        self.ollama_host = ollama_host
        self.model = model
        self.max_file_size = max_file_size
        self.exclude_dirs = {'.git', '.github', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', '.pytest_cache'}
    
    def check_ollama_connection(self) -> bool:
        """Check if Ollama server is available."""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                print(f"✓ Connected to Ollama at {self.ollama_host}")
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                print(f"  Available models: {', '.join(model_names)}")
                
                if any(self.model in name for name in model_names):
                    print(f"✓ Model {self.model} is available")
                    return True
                else:
                    print(f"✗ Model {self.model} not found!")
                    print(f"  Available: {', '.join(model_names)}")
                    return False
            else:
                print(f"✗ Failed to connect: HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection refused: {self.ollama_host}")
            print("  Make sure Ollama is running: ollama serve")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def get_code_files(self, directory: str = '.') -> List[str]:
        """Find all code files in the directory."""
        files = []
        
        for root, dirs, filenames in os.walk(directory):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for filename in filenames:
                ext = Path(filename).suffix.lower()
                if ext in CODE_EXTENSIONS:
                    filepath = os.path.join(root, filename)
                    files.append(filepath)
        
        return sorted(files)
    
    def analyze_file(self, filepath: str) -> Dict:
        """Analyze a single file using Ollama."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Skip very large files
            if len(content) > self.max_file_size:
                return {
                    'status': 'skipped',
                    'reason': f'File too large ({len(content)} chars > {self.max_file_size})',
                    'size': len(content)
                }
            
            lang = CODE_EXTENSIONS.get(Path(filepath).suffix.lower(), 'Unknown')
            
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
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.1,
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'analysis': response.json()['response'],
                    'size': len(content)
                }
            else:
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}',
                    'size': len(content)
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def analyze_repository(self, directory: str = '.', output_dir: str = '.') -> Dict:
        """Analyze all code files in the repository."""
        # Get all code files
        code_files = self.get_code_files(directory)
        
        if not code_files:
            print("⚠ No code files found!")
            return {'error': 'No code files found'}
        
        print(f"\n📊 Found {len(code_files)} code files to analyze\n")
        
        results = {}
        summary_stats = {
            'total': len(code_files),
            'analyzed': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Analyze each file
        for i, filepath in enumerate(code_files, 1):
            relative_path = filepath.lstrip('./')
            print(f"[{i}/{len(code_files)}] {relative_path:50s} ", end="", flush=True)
            
            result = self.analyze_file(filepath)
            results[relative_path] = result
            
            if result['status'] == 'success':
                summary_stats['analyzed'] += 1
                print("✓")
            elif result['status'] == 'skipped':
                summary_stats['skipped'] += 1
                print(f"⊘ ({result['reason']})")
            else:
                summary_stats['errors'] += 1
                print(f"✗ ({result.get('error', 'Unknown error')})")
            
            time.sleep(0.5)  # Rate limiting
        
        # Save results
        results_file = os.path.join(output_dir, 'analysis-results.json')
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Detailed results saved to {results_file}")
        
        # Generate markdown report
        report = self._generate_report(results, summary_stats)
        report_file = os.path.join(output_dir, 'analysis-report.md')
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"✓ Report saved to {report_file}")
        
        # Print summary
        self._print_summary(summary_stats)
        
        return {
            'results': results,
            'summary': summary_stats,
            'results_file': results_file,
            'report_file': report_file
        }
    
    def _generate_report(self, results: Dict, summary_stats: Dict) -> str:
        """Generate markdown report."""
        success_rate = (summary_stats['analyzed'] / summary_stats['total'] * 100) if summary_stats['total'] > 0 else 0
        
        report = f"""# Code Analysis Report

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Model: {self.model}
Ollama Server: {self.ollama_host}

## Summary Statistics

- **Total Files Analyzed**: {summary_stats['analyzed']}
- **Skipped Files**: {summary_stats['skipped']}
- **Errors**: {summary_stats['errors']}
- **Success Rate**: {success_rate:.1f}%

## Detailed Analysis

"""
        
        for filepath, result in results.items():
            report += f"\n---\n\n### {filepath}\n\n"
            
            if result['status'] == 'success':
                report += result['analysis']
            elif result['status'] == 'skipped':
                report += f"⊘ **Skipped**: {result['reason']}\n"
            else:
                report += f"✗ **Error**: {result.get('error', 'Unknown error')}\n"
        
        # Add summary
        report += f"""

---

## Analysis Summary

This code analysis was performed using:
- **Model**: {self.model}
- **Ollama Server**: {self.ollama_host}
- **Files Analyzed**: {summary_stats['analyzed']} / {summary_stats['total']}
- **Success Rate**: {success_rate:.1f}%

The analysis provided insights into:
- Code purpose and functionality
- Key components and architecture
- Dependencies and external libraries
- Potential improvements and issues
- Concise summaries for each file

All detailed results are available in `analysis-results.json`.
"""
        
        return report
    
    def _print_summary(self, summary_stats: Dict):
        """Print analysis summary."""
        success_rate = (summary_stats['analyzed'] / summary_stats['total'] * 100) if summary_stats['total'] > 0 else 0
        
        print("\n" + "="*60)
        print("📊 ANALYSIS SUMMARY")
        print("="*60)
        print(f"  Total Files Found:     {summary_stats['total']}")
        print(f"  Successfully Analyzed: {summary_stats['analyzed']}")
        print(f"  Skipped:               {summary_stats['skipped']}")
        print(f"  Errors:                {summary_stats['errors']}")
        print(f"  Success Rate:          {success_rate:.1f}%")
        print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description='Analyze code files using Ollama'
    )
    parser.add_argument(
        '--host',
        default='http://localhost:11434',
        help='Ollama server address (default: http://localhost:11434)'
    )
    parser.add_argument(
        '--model',
        default='deepseek-coder:6.7b',
        help='Model to use (default: deepseek-coder:6.7b)'
    )
    parser.add_argument(
        '--directory',
        default='.',
        help='Directory to analyze (default: current directory)'
    )
    parser.add_argument(
        '--output',
        default='.',
        help='Output directory for results (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = CodeAnalyzer(args.host, args.model)
    
    # Check connection
    print("\n🔍 Checking Ollama connection...\n")
    if not analyzer.check_ollama_connection():
        sys.exit(1)
    
    # Analyze repository
    print()
    analyzer.analyze_repository(args.directory, args.output)

if __name__ == '__main__':
    main()

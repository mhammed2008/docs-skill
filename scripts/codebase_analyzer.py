#!/usr/bin/env python3
"""
Universal Multi-Language Codebase Analyzer & Symbol Extractor  v2.0
Part of the Full-Project Documenter Skill suite.

Scans any codebase and extracts:
- File tree & tech stack taxonomy
- Project metadata from manifest files (package.json, Cargo.toml, etc.)
- Metrics (LOC, files, functions, classes, interfaces)
- AST-level symbol definitions with parent-class tracking, decorators,
  *args/**kwargs, constructors, enums, constants, and JSDoc comments
- Route/endpoint extraction for common web frameworks
- Import/export tracking and inter-file dependency graphs
- Test file detection and separation
Outputs a comprehensive JSON manifest for 100% zero-omission documentation.
"""

import os
import sys
import json
import re
import ast
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_EXCLUDES = {
    '.git', '.svn', '.hg', 'node_modules', 'vendor', '__pycache__',
    'venv', '.venv', 'env', '.env', 'dist', 'build', 'out', 'target',
    'bin', 'obj', '.next', '.nuxt', '.turbo', '.cache', '.idea', '.vscode',
    'coverage', '.pytest_cache', '.mypy_cache', 'Pods', 'derived_data',
    '.dart_tool', '.pub-cache', '.gradle', '.angular',
}

EXTENSION_MAP = {
    '.py': 'Python',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript (React)',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript (React)',
    '.mjs': 'JavaScript (ESM)',
    '.cjs': 'JavaScript (CommonJS)',
    '.go': 'Go',
    '.rs': 'Rust',
    '.java': 'Java',
    '.cs': 'C#',
    '.cpp': 'C++',
    '.cc': 'C++',
    '.cxx': 'C++',
    '.c': 'C',
    '.h': 'C/C++ Header',
    '.hpp': 'C++ Header',
    '.php': 'PHP',
    '.rb': 'Ruby',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.scala': 'Scala',
    '.dart': 'Dart',
    '.sol': 'Solidity',
    '.sh': 'Shell (Bash)',
    '.ps1': 'PowerShell',
    '.sql': 'SQL',
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.less': 'LESS',
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.md': 'Markdown',
    '.toml': 'TOML',
    '.proto': 'Protocol Buffers',
    '.graphql': 'GraphQL',
    '.gql': 'GraphQL',
}

TEST_PATTERNS = [
    re.compile(r'[\\/]tests?[\\/]', re.IGNORECASE),
    re.compile(r'[\\/]__tests__[\\/]', re.IGNORECASE),
    re.compile(r'[\\/]spec[\\/]', re.IGNORECASE),
    re.compile(r'\.(?:test|spec|tests|specs)\.[a-z]+$', re.IGNORECASE),
    re.compile(r'(?:^|[\\/])test_[^/\\]+\.py$', re.IGNORECASE),
    re.compile(r'_test\.go$', re.IGNORECASE),
]


def is_test_file(rel_path: str) -> bool:
    """Detects whether a file is a test file based on path patterns."""
    return any(p.search(rel_path) for p in TEST_PATTERNS)


# ---------------------------------------------------------------------------
# Project Metadata Extraction  (#6)
# ---------------------------------------------------------------------------

def detect_project_metadata(root_path: Path) -> Dict[str, Any]:
    """Reads project manifest files to extract name, version, deps, scripts."""
    meta: Dict[str, Any] = {
        "name": root_path.name,
        "version": "",
        "description": "",
        "dependencies": {},
        "dev_dependencies": {},
        "scripts": {},
        "entry_points": [],
        "detected_manifests": [],
    }

    # --- package.json (Node / JS / TS) ---
    pkg_json = root_path / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text(encoding='utf-8', errors='ignore'))
            meta["name"] = data.get("name", meta["name"])
            meta["version"] = data.get("version", "")
            meta["description"] = data.get("description", "")
            meta["dependencies"] = data.get("dependencies", {})
            meta["dev_dependencies"] = data.get("devDependencies", {})
            meta["scripts"] = data.get("scripts", {})
            if data.get("main"):
                meta["entry_points"].append(data["main"])
            meta["detected_manifests"].append("package.json")
        except Exception:
            pass

    # --- pyproject.toml / setup.cfg / setup.py ---
    pyproject = root_path / "pyproject.toml"
    if pyproject.exists():
        try:
            text = pyproject.read_text(encoding='utf-8', errors='ignore')
            name_m = re.search(r'name\s*=\s*"([^"]+)"', text)
            ver_m = re.search(r'version\s*=\s*"([^"]+)"', text)
            desc_m = re.search(r'description\s*=\s*"([^"]+)"', text)
            if name_m:
                meta["name"] = name_m.group(1)
            if ver_m:
                meta["version"] = ver_m.group(1)
            if desc_m:
                meta["description"] = desc_m.group(1)
            meta["detected_manifests"].append("pyproject.toml")
        except Exception:
            pass

    requirements = root_path / "requirements.txt"
    if requirements.exists():
        try:
            for line in requirements.read_text(encoding='utf-8', errors='ignore').splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = re.split(r'[>=<~!]', line, maxsplit=1)
                    pkg = parts[0].strip()
                    ver = parts[1].strip() if len(parts) > 1 else "*"
                    meta["dependencies"][pkg] = ver
            meta["detected_manifests"].append("requirements.txt")
        except Exception:
            pass

    # --- Cargo.toml (Rust) ---
    cargo = root_path / "Cargo.toml"
    if cargo.exists():
        try:
            text = cargo.read_text(encoding='utf-8', errors='ignore')
            name_m = re.search(r'name\s*=\s*"([^"]+)"', text)
            ver_m = re.search(r'version\s*=\s*"([^"]+)"', text)
            if name_m:
                meta["name"] = name_m.group(1)
            if ver_m:
                meta["version"] = ver_m.group(1)
            meta["detected_manifests"].append("Cargo.toml")
        except Exception:
            pass

    # --- go.mod (Go) ---
    gomod = root_path / "go.mod"
    if gomod.exists():
        try:
            text = gomod.read_text(encoding='utf-8', errors='ignore')
            mod_m = re.search(r'^module\s+(\S+)', text, re.MULTILINE)
            if mod_m:
                meta["name"] = mod_m.group(1)
            meta["detected_manifests"].append("go.mod")
        except Exception:
            pass

    # --- pubspec.yaml (Dart/Flutter) ---
    pubspec = root_path / "pubspec.yaml"
    if pubspec.exists():
        try:
            text = pubspec.read_text(encoding='utf-8', errors='ignore')
            name_m = re.search(r'^name:\s*(\S+)', text, re.MULTILINE)
            ver_m = re.search(r'^version:\s*(\S+)', text, re.MULTILINE)
            desc_m = re.search(r'^description:\s*(.+)$', text, re.MULTILINE)
            if name_m:
                meta["name"] = name_m.group(1)
            if ver_m:
                meta["version"] = ver_m.group(1)
            if desc_m:
                meta["description"] = desc_m.group(1).strip()
            meta["detected_manifests"].append("pubspec.yaml")
        except Exception:
            pass

    # --- Dockerfile ---
    dockerfile = root_path / "Dockerfile"
    if dockerfile.exists():
        meta["detected_manifests"].append("Dockerfile")

    # --- docker-compose.yml ---
    for name in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
        if (root_path / name).exists():
            meta["detected_manifests"].append(name)
            break

    return meta


# ---------------------------------------------------------------------------
# Python AST Visitor with Parent Tracking  (#1, #2, #9)
# ---------------------------------------------------------------------------

class PythonSymbolVisitor(ast.NodeVisitor):
    """
    Walks the Python AST with class-stack tracking so methods know their
    parent class. Extracts decorators, *args, **kwargs, kw-only args,
    and default values.
    """

    def __init__(self):
        self.symbols: List[Dict[str, Any]] = []
        self._class_stack: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        docstring = ast.get_docstring(node) or ""
        bases = [ast.unparse(b) for b in node.bases]
        decorators = [ast.unparse(d) for d in node.decorator_list]
        self.symbols.append({
            "type": "class",
            "name": node.name,
            "line": node.lineno,
            "end_line": getattr(node, "end_lineno", node.lineno),
            "bases": bases,
            "decorators": decorators,
            "docstring": docstring.strip(),
            "signature": f"class {node.name}({', '.join(bases)})",
            "parent_class": self._class_stack[-1] if self._class_stack else None,
        })
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def _visit_function(self, node):
        docstring = ast.get_docstring(node) or ""
        is_async = isinstance(node, ast.AsyncFunctionDef)
        decorators = [ast.unparse(d) for d in node.decorator_list]

        # --- Full argument extraction (#9) ---
        args = []
        all_args = node.args

        # Positional args (with defaults aligned from the right)
        num_pos = len(all_args.args)
        num_defaults = len(all_args.defaults)
        default_offset = num_pos - num_defaults
        for i, a in enumerate(all_args.args):
            arg_str = a.arg
            if a.annotation:
                arg_str += f": {ast.unparse(a.annotation)}"
            if i >= default_offset:
                default_val = ast.unparse(all_args.defaults[i - default_offset])
                arg_str += f" = {default_val}"
            args.append(arg_str)

        # *args
        if all_args.vararg:
            va = f"*{all_args.vararg.arg}"
            if all_args.vararg.annotation:
                va += f": {ast.unparse(all_args.vararg.annotation)}"
            args.append(va)

        # Keyword-only args
        for i, a in enumerate(all_args.kwonlyargs):
            arg_str = a.arg
            if a.annotation:
                arg_str += f": {ast.unparse(a.annotation)}"
            if i < len(all_args.kw_defaults) and all_args.kw_defaults[i] is not None:
                arg_str += f" = {ast.unparse(all_args.kw_defaults[i])}"
            args.append(arg_str)

        # **kwargs
        if all_args.kwarg:
            kw = f"**{all_args.kwarg.arg}"
            if all_args.kwarg.annotation:
                kw += f": {ast.unparse(all_args.kwarg.annotation)}"
            args.append(kw)

        returns = ast.unparse(node.returns) if node.returns else "None"
        prefix = "async " if is_async else ""
        sig = f"{prefix}def {node.name}({', '.join(args)}) -> {returns}"

        # Determine symbol type based on parent class
        parent_class = self._class_stack[-1] if self._class_stack else None
        sym_type = "method" if parent_class else "function"

        # Detect special method kinds via decorators
        is_property = any("property" in d for d in decorators)
        is_staticmethod = any("staticmethod" in d for d in decorators)
        is_classmethod = any("classmethod" in d for d in decorators)

        self.symbols.append({
            "type": sym_type,
            "name": node.name,
            "line": node.lineno,
            "end_line": getattr(node, "end_lineno", node.lineno),
            "is_async": is_async,
            "is_property": is_property,
            "is_staticmethod": is_staticmethod,
            "is_classmethod": is_classmethod,
            "parent_class": parent_class,
            "decorators": decorators,
            "signature": sig,
            "parameters": args,
            "returns": returns,
            "docstring": docstring.strip(),
        })

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._visit_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._visit_function(node)
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# Symbol Extractor
# ---------------------------------------------------------------------------

class SymbolExtractor:
    """Extracts classes, interfaces, functions, methods, types, enums,
    constants, and routes across languages."""

    # --- Python (AST-based with visitor) ---
    @staticmethod
    def extract_python(content: str, filepath: str) -> List[Dict[str, Any]]:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return SymbolExtractor._extract_fallback_regex(content, 'Python')

        visitor = PythonSymbolVisitor()
        visitor.visit(tree)
        return visitor.symbols

    # --- TypeScript / JavaScript ---
    @staticmethod
    def extract_typescript_javascript(content: str, lang: str) -> List[Dict[str, Any]]:
        symbols = []
        lines = content.splitlines()

        # --- JSDoc extraction (#21) ---
        jsdoc_buffer: List[str] = []
        pending_jsdoc = ""
        in_jsdoc = False

        # Regex patterns
        class_regex = re.compile(
            r'^(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z0-9_$]+)(?:<[^>]+>)?(?:\s+extends\s+([A-Za-z0-9_$.]+))?(?:\s+implements\s+([^{]+))?'
        )
        interface_regex = re.compile(
            r'^(?:export\s+)?interface\s+([A-Za-z0-9_$]+)(?:<[^>]+>)?(?:\s+extends\s+([^{]+))?'
        )
        type_regex = re.compile(
            r'^(?:export\s+)?type\s+([A-Za-z0-9_$]+)(?:<[^>]+>)?\s*='
        )
        enum_regex = re.compile(
            r'^(?:export\s+)?(?:const\s+)?enum\s+([A-Za-z0-9_$]+)'
        )
        func_regex = re.compile(
            r'^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z0-9_$]*)\s*\(([^)]*)\)(?:\s*:\s*([^{]+))?'
        )
        arrow_func_regex = re.compile(
            r'^(?:export\s+)?(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*(?::\s*[^=]+)?\s*=\s*(?:async\s*)?\(([^)]*)\)(?:\s*:\s*([^=]+))?\s*=>'
        )
        # FIX #3: constructor is NO LONGER excluded
        method_regex = re.compile(
            r'^\s*(?:(?:public|private|protected|static|readonly|override|abstract|async|get|set)\s+)*([A-Za-z0-9_$]+)\s*\(([^)]*)\)(?:\s*:\s*([^{]+))?'
        )
        method_exclude = {'if', 'for', 'while', 'switch', 'catch', 'return', 'throw', 'new', 'delete', 'typeof'}

        # Decorator / annotation patterns
        decorator_regex = re.compile(r'^\s*@([A-Za-z0-9_$.]+)\s*(?:\(([^)]*)\))?')

        # Export tracking (#8)
        export_regex = re.compile(r'^export\s+(?:default\s+)?(?:const|let|var|function|class|interface|type|enum|abstract)')
        named_export_regex = re.compile(r'^export\s*\{([^}]+)\}')

        pending_decorators: List[str] = []

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()

            # --- JSDoc tracking (#21) ---
            if stripped.startswith('/**'):
                in_jsdoc = True
                jsdoc_buffer = [stripped]
                if stripped.endswith('*/'):
                    in_jsdoc = False
                    pending_jsdoc = '\n'.join(jsdoc_buffer)
                    jsdoc_buffer = []
                continue
            if in_jsdoc:
                jsdoc_buffer.append(stripped)
                if stripped.endswith('*/'):
                    in_jsdoc = False
                    pending_jsdoc = '\n'.join(jsdoc_buffer)
                    jsdoc_buffer = []
                continue

            if not stripped or stripped.startswith('//'):
                continue

            # Decorator accumulation
            dec_match = decorator_regex.match(stripped)
            if dec_match:
                full_dec = dec_match.group(0).strip()
                pending_decorators.append(full_dec)
                continue

            def consume_jsdoc_and_decorators():
                nonlocal pending_jsdoc, pending_decorators
                doc = pending_jsdoc
                decs = list(pending_decorators)
                pending_jsdoc = ""
                pending_decorators = []
                return doc, decs

            # Enum (#11)
            match = enum_regex.search(stripped)
            if match:
                doc, decs = consume_jsdoc_and_decorators()
                symbols.append({
                    "type": "enum",
                    "name": match.group(1),
                    "line": idx,
                    "signature": stripped.rstrip('{').strip(),
                    "jsdoc": doc,
                    "decorators": decs,
                })
                continue

            # Class
            match = class_regex.search(stripped)
            if match:
                doc, decs = consume_jsdoc_and_decorators()
                symbols.append({
                    "type": "class",
                    "name": match.group(1),
                    "line": idx,
                    "signature": stripped.rstrip('{').strip(),
                    "extends": match.group(2) or "",
                    "implements": match.group(3).strip() if match.group(3) else "",
                    "jsdoc": doc,
                    "decorators": decs,
                })
                continue

            # Interface
            match = interface_regex.search(stripped)
            if match:
                doc, decs = consume_jsdoc_and_decorators()
                symbols.append({
                    "type": "interface",
                    "name": match.group(1),
                    "line": idx,
                    "signature": stripped.rstrip('{').strip(),
                    "extends": match.group(2).strip() if match.group(2) else "",
                    "jsdoc": doc,
                    "decorators": decs,
                })
                continue

            # Type alias
            match = type_regex.search(stripped)
            if match:
                doc, decs = consume_jsdoc_and_decorators()
                symbols.append({
                    "type": "type_alias",
                    "name": match.group(1),
                    "line": idx,
                    "signature": stripped[:150].strip(),
                    "jsdoc": doc,
                    "decorators": decs,
                })
                continue

            # Function declaration
            match = func_regex.search(stripped)
            if match and match.group(1):
                doc, decs = consume_jsdoc_and_decorators()
                symbols.append({
                    "type": "function",
                    "name": match.group(1),
                    "line": idx,
                    "signature": stripped.rstrip('{').strip(),
                    "params": match.group(2).strip(),
                    "returns": match.group(3).strip() if match.group(3) else "void/inferred",
                    "jsdoc": doc,
                    "decorators": decs,
                })
                continue

            # Arrow function
            match = arrow_func_regex.search(stripped)
            if match:
                doc, decs = consume_jsdoc_and_decorators()
                symbols.append({
                    "type": "function",
                    "name": match.group(1),
                    "line": idx,
                    "signature": stripped.rstrip('{').strip(),
                    "params": match.group(2).strip(),
                    "returns": match.group(3).strip() if match.group(3) else "inferred",
                    "jsdoc": doc,
                    "decorators": decs,
                })
                continue

            # Method inside class/object — constructor is now INCLUDED (#3)
            match = method_regex.search(stripped)
            if match and match.group(1) not in method_exclude:
                doc, decs = consume_jsdoc_and_decorators()
                symbols.append({
                    "type": "method",
                    "name": match.group(1),
                    "line": idx,
                    "signature": stripped.rstrip('{').strip(),
                    "params": match.group(2).strip(),
                    "returns": match.group(3).strip() if match.group(3) else "inferred",
                    "jsdoc": doc,
                    "decorators": decs,
                })

        return symbols

    # --- Go ---
    @staticmethod
    def extract_go(content: str) -> List[Dict[str, Any]]:
        symbols = []
        lines = content.splitlines()

        type_regex = re.compile(r'^type\s+([A-Za-z0-9_]+)\s+(struct|interface)')
        func_regex = re.compile(r'^func\s+(?:\(([^)]+)\)\s+)?([A-Za-z0-9_]+)\s*\(([^)]*)\)(?:\s*(?:\(([^)]+)\)|([^{]+)))?')

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()

            match = type_regex.search(stripped)
            if match:
                symbols.append({
                    "type": match.group(2),
                    "name": match.group(1),
                    "line": idx,
                    "signature": stripped.rstrip('{').strip()
                })
                continue

            match = func_regex.search(stripped)
            if match:
                receiver = match.group(1) or ""
                func_name = match.group(2)
                params = match.group(3) or ""
                returns = match.group(4) or match.group(5) or "void"
                sym_type = "method" if receiver else "function"
                recv_str = f"({receiver}) " if receiver else ""
                sig = f"func {recv_str}{func_name}({params}) {returns.strip()}"
                symbols.append({
                    "type": sym_type,
                    "name": func_name,
                    "receiver": receiver.strip(),
                    "line": idx,
                    "signature": sig.strip(),
                    "params": params.strip(),
                    "returns": returns.strip()
                })

        return symbols

    # --- Rust ---
    @staticmethod
    def extract_rust(content: str) -> List[Dict[str, Any]]:
        symbols = []
        lines = content.splitlines()

        struct_regex = re.compile(r'^(?:pub(?:\([^)]+\))?\s+)?(?:struct|enum|union)\s+([A-Za-z0-9_]+)')
        trait_regex = re.compile(r'^(?:pub(?:\([^)]+\))?\s+)?trait\s+([A-Za-z0-9_]+)')
        fn_regex = re.compile(r'^(?:pub(?:\([^)]+\))?\s+)?(?:async\s+)?(?:unsafe\s+)?(?:extern\s+"[^"]+"\s+)?fn\s+([A-Za-z0-9_]+)(?:<[^>]+>)?\s*\(([^)]*)\)(?:\s*->\s*([^{;]+))?')
        impl_regex = re.compile(r'^impl(?:<[^>]+>)?\s+(?:([A-Za-z0-9_]+)\s+for\s+)?([A-Za-z0-9_]+)')

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()

            match = struct_regex.search(stripped)
            if match:
                symbols.append({
                    "type": "struct/enum",
                    "name": match.group(1),
                    "line": idx,
                    "signature": stripped.rstrip('{').strip()
                })
                continue

            match = trait_regex.search(stripped)
            if match:
                symbols.append({
                    "type": "trait",
                    "name": match.group(1),
                    "line": idx,
                    "signature": stripped.rstrip('{').strip()
                })
                continue

            match = impl_regex.search(stripped)
            if match:
                symbols.append({
                    "type": "impl",
                    "name": match.group(2),
                    "trait_for": match.group(1) or "",
                    "line": idx,
                    "signature": stripped.rstrip('{').strip()
                })
                continue

            match = fn_regex.search(stripped)
            if match:
                symbols.append({
                    "type": "function",
                    "name": match.group(1),
                    "line": idx,
                    "signature": stripped.rstrip('{;').strip(),
                    "params": match.group(2).strip(),
                    "returns": match.group(3).strip() if match.group(3) else "()"
                })

        return symbols

    # --- Java & C# ---
    @staticmethod
    def extract_java_csharp(content: str, lang: str) -> List[Dict[str, Any]]:
        symbols = []
        lines = content.splitlines()

        class_regex = re.compile(
            r'^(?:(?:public|private|protected|internal|abstract|static|final|sealed|partial)\s+)*(?:class|interface|record|enum|struct)\s+([A-Za-z0-9_]+)'
        )
        method_regex = re.compile(
            r'^(?:(?:public|private|protected|internal|abstract|static|final|sealed|virtual|override|async|synchronized)\s+)+([A-Za-z0-9_<>\[\]?]+)\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)'
        )
        constructor_regex = re.compile(
            r'^\s*(?:public|private|protected|internal)\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)\s*(?:\{|:)'
        )
        annotation_regex = re.compile(r'^\s*@([A-Za-z0-9_]+)(?:\(([^)]*)\))?')
        method_exclude = {'if', 'for', 'while', 'switch', 'catch', 'return', 'throw'}
        pending_annotations: List[str] = []

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                continue

            # Annotation accumulation
            ann_match = annotation_regex.match(stripped)
            if ann_match:
                pending_annotations.append(ann_match.group(0).strip())
                continue

            def consume_annotations():
                nonlocal pending_annotations
                anns = list(pending_annotations)
                pending_annotations = []
                return anns

            match = class_regex.search(stripped)
            if match:
                anns = consume_annotations()
                symbols.append({
                    "type": "class_or_interface",
                    "name": match.group(1),
                    "line": idx,
                    "signature": stripped.rstrip('{').strip(),
                    "decorators": anns,
                })
                continue

            match = method_regex.search(stripped)
            if match and match.group(2) not in method_exclude:
                anns = consume_annotations()
                symbols.append({
                    "type": "method",
                    "name": match.group(2),
                    "returns": match.group(1),
                    "params": match.group(3).strip(),
                    "line": idx,
                    "signature": stripped.rstrip('{;').strip(),
                    "decorators": anns,
                })
                continue

            match = constructor_regex.search(stripped)
            if match:
                anns = consume_annotations()
                symbols.append({
                    "type": "constructor",
                    "name": match.group(1),
                    "params": match.group(2).strip(),
                    "line": idx,
                    "signature": stripped.rstrip('{;:').strip(),
                    "decorators": anns,
                })

        return symbols

    # --- Fallback regex for unsupported languages ---
    @staticmethod
    def _extract_fallback_regex(content: str, lang: str) -> List[Dict[str, Any]]:
        symbols = []
        lines = content.splitlines()
        generic_fn = re.compile(r'(?:def|function|fn|func|sub|procedure)\s+([A-Za-z0-9_]+)\s*\(')
        for idx, line in enumerate(lines, start=1):
            m = generic_fn.search(line)
            if m:
                symbols.append({
                    "type": "function",
                    "name": m.group(1),
                    "line": idx,
                    "signature": line.strip()[:120]
                })
        return symbols


# ---------------------------------------------------------------------------
# Route / Endpoint Extraction  (#7)
# ---------------------------------------------------------------------------

def extract_routes(content: str, lang: str, filepath: str) -> List[Dict[str, Any]]:
    """Extracts HTTP route/endpoint definitions from common web frameworks."""
    routes = []
    lines = content.splitlines()

    if lang == 'Python':
        # Flask / FastAPI / Django
        route_regex = re.compile(
            r'@(?:app|router|api|bp|blueprint)\.\s*(get|post|put|patch|delete|head|options|route|api_route)\s*\(\s*["\']([^"\']+)["\']'
            , re.IGNORECASE
        )
        for idx, line in enumerate(lines, start=1):
            m = route_regex.search(line)
            if m:
                method = m.group(1).upper()
                if method in ('ROUTE', 'API_ROUTE'):
                    method = 'ANY'
                routes.append({
                    "method": method,
                    "path": m.group(2),
                    "line": idx,
                    "file": filepath,
                })

    elif 'TypeScript' in lang or 'JavaScript' in lang:
        # Express / Fastify / Nest / Hono
        express_regex = re.compile(
            r'(?:app|router|server)\.\s*(get|post|put|patch|delete|head|options|all|use)\s*\(\s*["\']([^"\']+)["\']'
            , re.IGNORECASE
        )
        # Nest.js / decorator-based
        nest_regex = re.compile(
            r'@(Get|Post|Put|Patch|Delete|Head|Options|All)\s*\(\s*["\']?([^"\')\s]*)["\']?\s*\)'
            , re.IGNORECASE
        )
        # Next.js file-based route detection
        if re.search(r'[\\/](?:app|pages)[\\/](?:api[\\/])?', filepath):
            exported_methods = re.findall(r'export\s+(?:async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b', content, re.IGNORECASE)
            for method in exported_methods:
                # Derive route from file path
                route_path = filepath
                route_path = re.sub(r'.*[\\/](app|pages)[\\/]', '/', route_path)
                route_path = re.sub(r'[\\/]route\.[jt]sx?$', '', route_path)
                route_path = re.sub(r'[\\/]page\.[jt]sx?$', '', route_path)
                route_path = re.sub(r'\.[jt]sx?$', '', route_path)
                route_path = route_path.replace('\\', '/')
                routes.append({
                    "method": method.upper(),
                    "path": route_path or "/",
                    "line": 0,
                    "file": filepath,
                    "framework": "Next.js (file-based)",
                })

        for idx, line in enumerate(lines, start=1):
            m = express_regex.search(line)
            if m:
                routes.append({
                    "method": m.group(1).upper(),
                    "path": m.group(2),
                    "line": idx,
                    "file": filepath,
                })
            m = nest_regex.search(line)
            if m:
                routes.append({
                    "method": m.group(1).upper(),
                    "path": m.group(2) or "/",
                    "line": idx,
                    "file": filepath,
                    "framework": "NestJS",
                })

    elif lang == 'Go':
        go_route = re.compile(
            r'(?:Handle|HandleFunc|Get|Post|Put|Patch|Delete|Head|Options|Route|Method)\s*\(\s*["\']([^"\']+)["\']'
        )
        for idx, line in enumerate(lines, start=1):
            m = go_route.search(line)
            if m:
                routes.append({
                    "method": "ANY",
                    "path": m.group(1),
                    "line": idx,
                    "file": filepath,
                })

    elif lang in ('Java', 'C#'):
        # Spring Boot / ASP.NET
        mapping_regex = re.compile(
            r'@(GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|RequestMapping)\s*\(\s*(?:value\s*=\s*)?["\']?([^"\')\s,]*)'
        )
        aspnet_regex = re.compile(
            r'\[(Http(?:Get|Post|Put|Patch|Delete))\s*(?:\(\s*"([^"]*)"\s*\))?\]'
        )
        for idx, line in enumerate(lines, start=1):
            m = mapping_regex.search(line)
            if m:
                method = m.group(1).replace('Mapping', '').upper()
                if method == 'REQUEST':
                    method = 'ANY'
                routes.append({
                    "method": method,
                    "path": m.group(2) or "/",
                    "line": idx,
                    "file": filepath,
                })
            m = aspnet_regex.search(line)
            if m:
                method = m.group(1).replace('Http', '').upper()
                routes.append({
                    "method": method,
                    "path": m.group(2) or "/",
                    "line": idx,
                    "file": filepath,
                })

    return routes


# ---------------------------------------------------------------------------
# Import & Export Extraction
# ---------------------------------------------------------------------------

def extract_imports(lines: List[str], lang: str) -> List[str]:
    """Extracts import statements from source code lines."""
    imports = []

    if lang == 'Python':
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                imports.append(stripped)

    elif 'TypeScript' in lang or 'JavaScript' in lang:
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import ') or 'require(' in stripped:
                imports.append(stripped[:150])

    elif lang == 'Go':
        in_block = False
        for line in lines:
            sl = line.strip()
            if sl.startswith('import ('):
                in_block = True
            elif in_block:
                if sl.startswith(')'):
                    in_block = False
                elif sl:
                    imports.append(sl.strip('"').strip())
            elif sl.startswith('import '):
                imports.append(sl.replace('import ', '').strip().strip('"'))

    elif lang == 'Rust':
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('use '):
                imports.append(stripped.rstrip(';'))

    elif lang in ('Java', 'Kotlin', 'Scala'):
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import '):
                imports.append(stripped.rstrip(';'))

    elif lang == 'C#':
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('using ') and not stripped.startswith('using ('):
                imports.append(stripped.rstrip(';'))

    elif lang == 'PHP':
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('use '):
                imports.append(stripped.rstrip(';'))

    elif lang == 'Dart':
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import '):
                imports.append(stripped.rstrip(';'))

    return imports


def extract_exports(content: str, lang: str) -> List[str]:
    """Extracts export declarations (#8)."""
    exports = []
    if 'TypeScript' in lang or 'JavaScript' in lang:
        # Named exports
        for m in re.finditer(r'export\s+(?:default\s+)?(?:const|let|var|function\*?|class|interface|type|enum|abstract\s+class)\s+([A-Za-z0-9_$]+)', content):
            exports.append(m.group(1))
        # Re-exports: export { Foo, Bar } from '...'
        for m in re.finditer(r'export\s*\{([^}]+)\}', content):
            for name in m.group(1).split(','):
                name = name.strip().split(' as ')[0].strip()
                if name:
                    exports.append(name)
        # module.exports
        for m in re.finditer(r'module\.exports\s*=\s*(\{[^}]+\}|[A-Za-z0-9_$]+)', content):
            exports.append(m.group(1)[:60])
    return exports


# ---------------------------------------------------------------------------
# Main Scanner
# ---------------------------------------------------------------------------

def scan_codebase(root_path: Path, excludes: set) -> Dict[str, Any]:
    file_inventory = []
    language_counts: Dict[str, int] = {}
    total_loc = 0
    total_symbols = 0
    dependency_graph: Dict[str, List[str]] = {}
    all_routes: List[Dict[str, Any]] = []
    test_file_count = 0

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in excludes and not d.startswith('.')]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in EXTENSION_MAP:
                continue

            full_path = Path(dirpath) / fname
            rel_path = full_path.relative_to(root_path).as_posix()

            try:
                content = full_path.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue

            source_lines = content.splitlines()
            loc = len(source_lines)
            total_loc += loc
            lang = EXTENSION_MAP[ext]
            language_counts[lang] = language_counts.get(lang, 0) + 1

            # Test file detection (#20)
            test_flag = is_test_file(rel_path)
            if test_flag:
                test_file_count += 1

            # Extract symbols based on language
            symbols: List[Dict[str, Any]] = []
            if lang == 'Python':
                symbols = SymbolExtractor.extract_python(content, rel_path)
            elif 'TypeScript' in lang or 'JavaScript' in lang:
                symbols = SymbolExtractor.extract_typescript_javascript(content, lang)
            elif lang == 'Go':
                symbols = SymbolExtractor.extract_go(content)
            elif lang == 'Rust':
                symbols = SymbolExtractor.extract_rust(content)
            elif lang in ('Java', 'C#'):
                symbols = SymbolExtractor.extract_java_csharp(content, lang)
            else:
                symbols = SymbolExtractor._extract_fallback_regex(content, lang)

            total_symbols += len(symbols)

            # Import & export extraction
            imports = extract_imports(source_lines, lang)
            exports = extract_exports(content, lang)

            # Route extraction (#7)
            routes = extract_routes(content, lang, rel_path)
            all_routes.extend(routes)

            file_info = {
                "path": rel_path,
                "language": lang,
                "lines": loc,
                "is_test": test_flag,
                "symbol_count": len(symbols),
                "symbols": symbols,
                "imports": imports[:30],
                "exports": exports[:20],
                "routes": routes,
            }

            file_inventory.append(file_info)
            if imports:
                dependency_graph[rel_path] = imports

    # Project metadata
    project_meta = detect_project_metadata(root_path)

    return {
        "version": "2.0",
        "project_meta": project_meta,
        "summary": {
            "root": str(root_path.resolve()),
            "total_files": len(file_inventory),
            "total_loc": total_loc,
            "total_symbols": total_symbols,
            "total_routes": len(all_routes),
            "test_files": test_file_count,
            "production_files": len(file_inventory) - test_file_count,
            "language_breakdown": language_counts,
        },
        "routes": all_routes,
        "files": file_inventory,
        "dependency_graph": dependency_graph,
    }


def main():
    parser = argparse.ArgumentParser(description="Universal Codebase Analyzer & Symbol Extractor v2.0")
    parser.add_argument("path", nargs="?", default=".", help="Root directory of the project to analyze")
    parser.add_argument("--output", "-o", default="codebase_manifest.json", help="Path to write JSON manifest")
    parser.add_argument("--exclude", "-e", nargs="*", default=[], help="Extra directories to exclude")
    args = parser.parse_args()

    root = Path(args.path)
    if not root.exists():
        print(f"Error: Path {root} does not exist.", file=sys.stderr)
        sys.exit(1)

    excludes = DEFAULT_EXCLUDES.union(set(args.exclude))
    print(f"[*] Scanning codebase at: {root.resolve()} ...")
    manifest = scan_codebase(root, excludes)

    output_path = Path(args.output)
    output_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    s = manifest["summary"]
    pm = manifest["project_meta"]
    print(f"\n[+] Scan Complete!")
    print(f"    Project:               {pm['name']} {pm['version']}")
    print(f"    Manifests Detected:    {', '.join(pm['detected_manifests']) or 'none'}")
    print(f"    Total Files Analyzed:  {s['total_files']} ({s['production_files']} prod, {s['test_files']} test)")
    print(f"    Total Lines of Code:   {s['total_loc']}")
    print(f"    Total Symbols:         {s['total_symbols']}")
    print(f"    Total API Routes:      {s['total_routes']}")
    print(f"    Language Breakdown:")
    for lang, count in s['language_breakdown'].items():
        print(f"        * {lang}: {count} files")
    print(f"[+] Full JSON manifest written to: {output_path.resolve()}\n")


if __name__ == "__main__":
    main()

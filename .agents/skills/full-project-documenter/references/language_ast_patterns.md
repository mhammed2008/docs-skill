# Multi-Language AST & Symbol Extraction Patterns

This reference provides parsing guidelines and regular expression heuristics across 15+ programming languages to ensure that no function, class, trait, method, or endpoint is overlooked during analysis.

---

## 1. TypeScript & JavaScript (ES6+ / Node / React)

### Class & Interface Declarations
```regex
^(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z0-9_$]+)(?:<[^>]+>)?(?:\s+extends\s+([A-Za-z0-9_$.]+))?(?:\s+implements\s+([^{]+))?
```

### Traditional Functions & Generators
```regex
^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z0-9_$]*)\s*\(([^)]*)\)(?:\s*:\s*([^{]+))?
```

### Arrow Functions & Functional Components
```regex
^(?:export\s+)?(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?\(([^)]*)\)(?:\s*:\s*([^=]+))?\s*=>
```

### Class Methods & Getters/Setters
```regex
^\s*(?:(?:public|private|protected|static|readonly|override|async)\s+)*(?:get\s+|set\s+)?([A-Za-z0-9_$]+)\s*\(([^)]*)\)(?:\s*:\s*([^{]+))?
```

---

## 2. Python (3.8+)

### AST Native Parser (Preferred)
Always use Python's built-in `ast` module:
- `ast.ClassDef`: Extracts class name, base classes, decorators, and docstring.
- `ast.FunctionDef` / `ast.AsyncFunctionDef`: Extracts function name, positional args, keyword args, type annotations, return annotation, decorators, and docstring.

### Fallback Regex
```regex
^(?:async\s+)?def\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?:
```

---

## 3. Go (Golang)

### Struct & Interface Declarations
```regex
^type\s+([A-Za-z0-9_]+)\s+(struct|interface)
```

### Functions & Methods
```regex
^func\s+(?:\(([^)]+)\)\s+)?([A-Za-z0-9_]+)\s*\(([^)]*)\)(?:\s*(?:\(([^)]+)\)|([^{]+)))?
```
- Group 1: Receiver (e.g. `s *Server`) -> Identifies methods vs standalone functions.
- Group 2: Function name.
- Group 3: Input parameters.
- Group 4/5: Return values.

---

## 4. Rust

### Structs, Enums, Unions & Traits
```regex
^(?:pub(?:\([^)]+\))?\s+)?(?:struct|enum|union|trait)\s+([A-Za-z0-9_]+)
```

### Functions, Methods & Associated Functions
```regex
^(?:pub(?:\([^)]+\))?\s+)?(?:async\s+)?(?:unsafe\s+)?fn\s+([A-Za-z0-9_]+)(?:<[^>]+>)?\s*\(([^)]*)\)(?:\s*->\s*([^{;]+))?
```

---

## 5. Java & C#

### Classes, Records, Enums, Interfaces
```regex
^(?:(?:public|private|protected|internal|abstract|static|final|sealed|partial)\s+)*(?:class|interface|record|enum|struct)\s+([A-Za-z0-9_]+)
```

### Methods
```regex
^(?:(?:public|private|protected|internal|abstract|static|final|sealed|virtual|override|async)\s+)+([A-Za-z0-9_<>[\]?]+)\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)
```

---

## 6. C & C++

### Functions & Methods
```regex
^(?:[A-Za-z0-9_:<>&*]+\s+)+([A-Za-z0-9_]+)\s*\(([^)]*)\)(?:\s*const)?\s*(?:\{|;)
```

---

## 7. PHP

### Classes & Interfaces
```regex
^(?:abstract\s+|final\s+)?(?:class|interface|trait|enum)\s+([A-Za-z0-9_]+)
```

### Functions & Methods
```regex
^(?:(?:public|protected|private|static|final|abstract)\s+)*function\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)(?:\s*:\s*([^{;]+))?
```

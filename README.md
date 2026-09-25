# Full-Project Documenter Skill (Zero-Omission Engine)

[![Antigravity Skill](https://img.shields.io/badge/Antigravity-Customization_Skill-blue.svg)](https://github.com)
[![Status](https://img.shields.io/badge/Coverage-100%25_Zero_Omission-brightgreen.svg)](https://github.com)
[![Platform](https://img.shields.io/badge/Stack-Multi--Language_Universal-orange.svg)](https://github.com)

A specialized, enterprise-grade AI skill for Google Antigravity and AI coding agents. Designed to **analyze and document 100% of any codebase's features, data models, APIs, and every single class, function, and method without skipping, summarizing, or suffering token fatigue**.

---

## Why This Skill Exists

Standard AI coding assistants suffer from **token fatigue** and **summarization bias** when asked to document projects:
- They document the first 3 files and write `// and so on...`
- They group 20 functions into a single bullet point
- They skip internal helper functions, private methods, and error cases
- They omit system data flows, state machines, and sequence diagrams

The **Full-Project Documenter Skill** eliminates this behavior by enforcing a **Token-Budget Agnostic Zero-Omission Protocol** backed by automated AST extraction and a coverage verification gate.

---

## Directory Architecture

```text
docs-skill/
├── SKILL.md                          # Core Antigravity skill specification with frontmatter
├── README.md                         # Presentation, setup, and usage guide
├── scripts/
│   ├── codebase_analyzer.py          # AST & regex symbol extractor across 15+ languages
│   ├── generate_mermaid_graphs.py    # Auto-synthesizes Mermaid C4 & class diagrams
│   └── verify_coverage.py            # Automated audit: proves 100% of symbols are documented
├── templates/
│   ├── 00_overview_and_architecture.md
│   ├── 01_feature_specification.md
│   ├── 02_system_data_flows.md
│   ├── 03_data_models_and_schemas.md
│   ├── 04_api_and_integrations.md
│   ├── 05_exhaustive_function_index.md
│   ├── 06_configuration_and_env.md
│   └── 07_deployment_and_operations.md
└── references/
    ├── zero_omission_protocol.md     # In-depth 6-phase execution handbook
    ├── language_ast_patterns.md      # AST patterns (TS, Py, Go, Rust, Java, C#, C++, etc.)
    └── mermaid_architecture_guide.md # Clean Mermaid syntax & best practices
```

---

## Generated Documentation Output

When this skill runs on any codebase, it outputs a modular, publication-ready documentation suite inside `docs/`:

| Document | Purpose & Contents |
| :--- | :--- |
| [`00_OVERVIEW_AND_ARCHITECTURE.md`](./templates/00_overview_and_architecture.md) | Executive summary, full tech stack taxonomy, C4 architecture diagrams, directory tree map. |
| [`01_FEATURE_SPECIFICATION.md`](./templates/01_feature_specification.md) | Master feature matrix, user stories, sequence diagrams, edge cases, and code traces. |
| [`02_SYSTEM_DATA_FLOWS.md`](./templates/02_system_data_flows.md) | Lifecycle state machines, async worker queues, WebSockets, event pipelines, caching. |
| [`03_DATA_MODELS_AND_SCHEMAS.md`](./templates/03_data_models_and_schemas.md) | Complete Mermaid ERD, column-by-column database dictionary, DTOs, migrations. |
| [`04_API_AND_INTEGRATIONS.md`](./templates/04_api_and_integrations.md) | 100% endpoint encyclopedia (REST, GraphQL, gRPC, CLI), request/response JSON, webhooks. |
| [`05_functions/*.md`](./templates/05_exhaustive_function_index.md) | **Atomic Symbol Encyclopedia**: Every function, method, signature, params, return, errors, call graph, and step-by-step logic. |
| [`06_CONFIGURATION_AND_ENV.md`](./templates/06_configuration_and_env.md) | Environment variables dictionary, configuration files, secrets management. |
| [`07_DEPLOYMENT_AND_OPERATIONS.md`](./templates/07_deployment_and_operations.md) | Build instructions, Dockerfiles, test suite topology, health checks, incident runbooks. |
| `COVERAGE_AUDIT.md` | Verification report proving 100% symbol coverage. |

---

## Installation in Antigravity

### Option 1: Global Installation (Available across all projects)
Copy the skill folder to your global Antigravity configuration directory:

```bash
# Windows PowerShell
Copy-Item -Recurse -Force "d:\Maxcode\docs-skill" "$HOME\.gemini\config\skills\full-project-documenter"
```

### Option 2: Workspace Project Installation (Scoped to a specific repo)
Place the skill into your project's `.agents/skills/` directory:

```bash
# Inside any project repository:
mkdir -p .agents/skills/full-project-documenter
Copy-Item -Recurse -Force "d:\Maxcode\docs-skill\*" ".agents\skills\full-project-documenter\"
```

---

## How to Trigger & Use

### 1. Slash Command (Fastest & Direct)
In any project, simply type:

```text
/docs
```
or with path / parameters:
```text
/docs --exclude tests,vendor
```

### 2. Mentioning the Skill
```text
@docs document this entire project
```
or
```text
@full-project-documenter analyze every single feature and function
```

### 3. Natural Language
```text
Generate full documentation for this project. Analyze every single feature and function without worrying about token usage.
```

---

## Automated Verification Workflow

The skill includes automated tooling to guarantee zero omissions:

```bash
# Step 1: Scan codebase & extract manifest of all files and functions
python scripts/codebase_analyzer.py . --output codebase_manifest.json

# Step 2: Generate architecture & class diagrams in Mermaid
python scripts/generate_mermaid_graphs.py codebase_manifest.json

# Step 3: Run documentation synthesis (executed by the AI agent)

# Step 4: Audit 100% symbol and function coverage
python scripts/verify_coverage.py --manifest codebase_manifest.json --docs docs/
```

If any function is missing from the documentation, `verify_coverage.py` exits with status code `2` and displays the exact missing symbols so the agent can document them before completing.

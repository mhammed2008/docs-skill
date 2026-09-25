---
name: full-project-documenter
description: >-
  Universal exhaustive codebase documentation engine. Scans, extracts, and documents 100% of a project's
  architecture, features, data models, API endpoints, and every single class, function, method, parameter,
  and return value without skipping or summarizing. Generates navigable, multi-tiered documentation suites
  with Mermaid diagrams, call graphs, and exhaustive file-by-file symbol encyclopedias. Activates on `/docs`,
  `/doc`, `@docs`, `@full-project-documenter`, or when asked to "generate full docs", "document this project",
  "create complete documentation", or analyze every feature and function in a codebase.
---

# Full-Project Documenter Skill (Zero-Omission Engine) v2.0

The **Full-Project Documenter** is an exhaustive documentation engine designed to analyze and document **100% of a project's features and 100% of its functions, classes, and methods**.

> [!IMPORTANT]
> **The Zero-Omission Mandate**:
> 1. **Do not worry about token usage**. Never compress, truncate, summarize, or omit functions or features to save tokens.
> 2. **Never emit placeholders**: Never write `// other methods omitted`, `...`, or `left as an exercise`.
> 3. **Document every symbol**: Every single function, method, constructor, interface, class, and endpoint detected in the project must appear in the documentation with full technical fidelity.
> 4. **Multi-tiered modular output**: For medium to large codebases, write documentation into a structured `docs/` suite to prevent single-file context overflow.

> [!WARNING]
> **Template Placeholder Rule**: All bracketed `[placeholder]` text from templates MUST be replaced with project-specific content. Never leave template placeholders like `[e.g. Node.js]` or `[Feature Title]` in the final output.

---

## Step 0: Project Sizing & Mode Selection

Before starting, determine the project's scale and pick the right output mode:

| Project Size | Files | Symbols | Mode | Output Strategy |
|:---|:---|:---|:---|:---|
| **Micro** | ≤ 5 | ≤ 20 | Single-file | One consolidated `DOCUMENTATION.md` covering everything |
| **Small** | 6–20 | 21–80 | Compact | 3–4 focused documents (overview, features, functions, ops) |
| **Medium** | 21–100 | 81–300 | Standard | Full 8-document suite as described below |
| **Large** | 100+ | 300+ | Modular | Full suite + partitioned `05_functions/` per module |

**Auto-detection**: After Phase 1 manifest generation, check `total_files` and `total_symbols` to pick the mode automatically.

---

## Documentation Suite Architecture

When invoked on a target project, this skill synthesizes an enterprise-grade documentation suite inside the project's `docs/` folder:

```text
docs/
├── INDEX.md                           # Navigation hub with links to all documents
├── 00_OVERVIEW_AND_ARCHITECTURE.md    # Executive summary, stack taxonomy, C4 architecture diagrams
├── 01_FEATURE_SPECIFICATION.md        # 100% feature catalog with user stories & sequence flows
├── 02_SYSTEM_DATA_FLOWS.md            # State machines, async queues, WebSockets, event pipelines
├── 03_DATA_MODELS_AND_SCHEMAS.md      # ERD diagrams, table dictionaries, DTOs, migrations
├── 04_API_AND_INTEGRATIONS.md         # Full REST/GraphQL/gRPC/CLI catalog & external webhooks
├── 05_functions/                      # Exhaustive file-by-file function & method encyclopedia
│   ├── [module_1].md                  # Every class, method, function, parameter, and error
│   ├── [module_2].md
│   └── ...
├── 06_CONFIGURATION_AND_ENV.md        # Environment variables, config files, secrets
├── 07_DEPLOYMENT_AND_OPERATIONS.md    # Build pipelines, Docker, tests, monitoring, runbooks
└── COVERAGE_AUDIT.md                  # Verification report proving 100% symbol coverage
```

> [!IMPORTANT]
> **Progress Checkpointing**: Write each document to disk **as soon as it is complete** — do NOT wait until all phases finish. This way, if the session is interrupted or hits context limits, prior phases are preserved and the pipeline can resume by checking which `docs/0X_*.md` files already exist.

---

## Execution Protocol: The 6-Phase Pipeline

### Phase 1: Codebase Reconnaissance & Symbol Manifest

1. **Locate the Project Root**:
   Determine the target codebase root directory.
2. **Execute the Codebase Analyzer Script**:
   Run the included analyzer script to parse all source files and generate `codebase_manifest.json`:
   ```bash
   python scripts/codebase_analyzer.py <path_to_project> --output codebase_manifest.json
   ```
   *Note: If running in an environment without direct script access, use native tools (`list_dir`, `grep_search`, `view_file`) guided by [language_ast_patterns.md](./references/language_ast_patterns.md).*
3. **Inspect the Manifest Metrics**:
   Read `codebase_manifest.json` to note:
   - `project_meta` — project name, version, dependencies, scripts
   - `total_files` / `production_files` / `test_files`
   - `total_loc`, `total_symbols`, `total_routes`
   - `language_breakdown`
   - `routes` — pre-extracted HTTP endpoints
4. **Select Output Mode**: Use the sizing table above to pick Micro / Small / Medium / Large mode.

---

### Phase 2: System Overview & Architecture (`00_OVERVIEW_AND_ARCHITECTURE.md`)

Use [00_overview_and_architecture.md](./templates/00_overview_and_architecture.md) as the blueprint:
1. **Executive Mission & Target Users**: Explain what the system accomplishes and who uses it. Use `project_meta.description` from the manifest.
2. **Tech Stack Taxonomy**: Build an exhaustive table covering runtime, framework, ORM, database, queues, and build tooling. Use `project_meta.dependencies` and `project_meta.dev_dependencies` for exact versions.
3. **C4 System Architecture (Mermaid)**:
   - Run `scripts/generate_mermaid_graphs.py codebase_manifest.json` to generate clean Mermaid diagrams.
   - Embed system context, container topology, and component boundaries.
4. **Directory Structure Map**: Map every top-level folder with its design rationale.
5. **Architectural Invariants**: Document architectural patterns (e.g. Hexagonal, Clean Architecture, CQRS, MVC).

**Monorepo Detection**: If the project root contains workspace indicators (`pnpm-workspace.yaml`, `lerna.json`, Turborepo `turbo.json`, Cargo `[workspace]`, Go `work.sum`), document each workspace member/package independently within the suite and add a top-level monorepo architecture map showing inter-package dependencies.

**✅ CHECKPOINT**: Write `docs/00_OVERVIEW_AND_ARCHITECTURE.md` to disk now.

---

### Phase 3: Feature Specifications & Data Flows

1. **Master Feature Matrix** (`01_FEATURE_SPECIFICATION.md`):
   - Inventory every feature (user-facing and internal/background).
   - Assign IDs (`FEAT-01`, `FEAT-02`, ...).
   - Trace each feature directly to its frontend component, API route, service handler, and database model.
   - Use the manifest's `routes` field to pre-populate the endpoint mappings.
   - Use [01_feature_specification.md](./templates/01_feature_specification.md).
   - Provide a Mermaid sequence diagram for every primary feature workflow.
   - Document edge cases, error conditions, and permission rules.

   **✅ CHECKPOINT**: Write `docs/01_FEATURE_SPECIFICATION.md` to disk now.

2. **Dynamic Flows & State Machines** (`02_SYSTEM_DATA_FLOWS.md`):
   - Use [02_system_data_flows.md](./templates/02_system_data_flows.md).
   - Document entity lifecycle state machines (`Draft` -> `Active` -> `Completed`).
   - Document message brokers, worker queues, retry backoffs, and WebSocket lifecycles.

   **✅ CHECKPOINT**: Write `docs/02_SYSTEM_DATA_FLOWS.md` to disk now.

---

### Phase 4: Data Architecture & API Catalog

1. **Data Models & Database Schemas** (`03_DATA_MODELS_AND_SCHEMAS.md`):
   - Use [03_data_models_and_schemas.md](./templates/03_data_models_and_schemas.md).
   - Render complete Mermaid Entity-Relationship Diagrams (ERD).
   - Document every table/collection, column, type, foreign key, index, and constraint.
   - Catalog all DTOs and validation schemas.

   **✅ CHECKPOINT**: Write `docs/03_DATA_MODELS_AND_SCHEMAS.md` to disk now.

2. **API & Third-Party Integrations** (`04_API_AND_INTEGRATIONS.md`):
   - Use [04_api_and_integrations.md](./templates/04_api_and_integrations.md).
   - **Start from the manifest's `routes` array** — these are pre-extracted endpoints. Enrich each with handler details, middleware, request/response schemas.
   - Document 100% of endpoints (HTTP, GraphQL, gRPC, CLI).
   - Include route, HTTP method, auth guards, headers, query params, request body schema, and all response codes (200/201, 400, 401, 404, 500) with JSON payloads.
   - Catalog external third-party integrations and incoming webhooks.

   **✅ CHECKPOINT**: Write `docs/04_API_AND_INTEGRATIONS.md` to disk now.

---

### Phase 5: Exhaustive Function & Symbol Indexing (`docs/05_functions/`)

> [!CAUTION]
> **Zero Summarization Rule**:
> This phase is where most documentations fail. You MUST analyze and catalog **EVERY SINGLE FUNCTION, METHOD, AND CONSTRUCTOR**.

1. **Partition by Module**:
   Do NOT combine 50+ functions into one file. Create modular chapters inside `docs/05_functions/`:
   - `docs/05_functions/auth.md`
   - `docs/05_functions/controllers.md`
   - `docs/05_functions/services.md`
   - `docs/05_functions/utils.md`

2. **Separate Test Files**: Files flagged with `"is_test": true` in the manifest should be documented in a separate `docs/05_functions/tests.md` (or `tests/` subfolder) rather than mixed in with production code.

3. **Document Every Symbol According to the Standard**:
   For each symbol, follow [05_exhaustive_function_index.md](./templates/05_exhaustive_function_index.md):
   - **Exact Signature**: Typed signature with parameters, defaults, `*args`, `**kwargs`.
   - **File & Line**: `path/to/file.ext#L12-L45`
   - **Parent Class**: If a method, name the class it belongs to (from `parent_class` field).
   - **Visibility & Modifiers**: `public`, `private`, `async`, `static`, `@property`, `@classmethod`, etc.
   - **Decorators**: List all decorators/annotations (from `decorators` field).
   - **Core Purpose**: Concise explanation of the business/technical goal.
   - **Parameters Table**: Name, type, required/optional, default, semantics.
   - **Return Value**: Type and description of resolved/returned value.
   - **Exceptions / Errors**: Specific exceptions thrown and trigger conditions.
   - **Algorithmic Logic**: Step-by-step numbered breakdown of the internal logic.
   - **Call Graph**: Ingoing callers ("Called By") and outgoing callees ("Calls").
   - **Side Effects**: Database writes, network I/O, cache invalidations, state mutations.

   **✅ CHECKPOINT**: Write each `docs/05_functions/[module].md` to disk as you complete it.

---

### Phase 6: Operational Runbooks & 100% Coverage Verification

1. **Configuration & Operations**:
   - Synthesize `06_CONFIGURATION_AND_ENV.md` using [06_configuration_and_env.md](./templates/06_configuration_and_env.md).
     Use `project_meta.scripts` for build/test commands and `project_meta.dependencies` for exact versions.
   - Synthesize `07_DEPLOYMENT_AND_OPERATIONS.md` using [07_deployment_and_operations.md](./templates/07_deployment_and_operations.md).

   **✅ CHECKPOINT**: Write both documents to disk now.

2. **Generate `docs/INDEX.md` Navigation Hub**:
   Create a master index document with:
   - Table of contents linking to every `docs/` document
   - Quick-reference symbol lookup table (top-level classes and key functions)
   - Project metadata summary (name, version, language, total LOC)

   **✅ CHECKPOINT**: Write `docs/INDEX.md` to disk now.

3. **Execute Automated Coverage Audit**:
   Run the zero-omission verifier:
   ```bash
   python scripts/verify_coverage.py --manifest codebase_manifest.json --docs docs/ --output-json docs/COVERAGE_AUDIT.json
   ```

4. **Enforce 100% Verification Gate**:
   - The verifier compares every symbol in `codebase_manifest.json` against the generated markdown files using **word-boundary matching** (not naive substring).
   - Symbols with very short or generic names (e.g. `get`, `run`, `init`) are skipped from verification but should still be documented.
   - If any symbol was omitted or missed, immediately document the missing symbol in its respective `05_functions/` chapter.
   - Save the audit results to `docs/COVERAGE_AUDIT.md`.
   - Conclude only when 100% verified coverage is achieved!

---

## Supporting Resources

- [Zero-Omission Protocol Guide](./references/zero_omission_protocol.md)
- [Multi-Language AST Patterns](./references/language_ast_patterns.md)
- [Mermaid Diagramming Standards](./references/mermaid_architecture_guide.md)
- [Analyzer Script](./scripts/codebase_analyzer.py)
- [Diagram Generator Script](./scripts/generate_mermaid_graphs.py)
- [Coverage Verifier Script](./scripts/verify_coverage.py)

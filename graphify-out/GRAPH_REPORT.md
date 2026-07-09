# Graph Report - .  (2026-06-05)

## Corpus Check
- Corpus is ~7,163 words - fits in a single context window. You may not need a graph.

## Summary
- 104 nodes · 156 edges · 8 communities detected
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 17 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]

## God Nodes (most connected - your core abstractions)
1. `AutomationChain` - 12 edges
2. `make_sample()` - 8 edges
3. `build_graph()` - 8 edges
4. `generate_test()` - 7 edges
5. `main()` - 6 edges
6. `load_all_corpus()` - 6 edges
7. `AutomationResponse` - 6 edges
8. `create_convert_pairs()` - 5 edges
9. `create_review_pairs()` - 5 edges
10. `review_test()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Alpaca/ChatML training data schema` --conceptually_related_to--> `make_sample()`  [INFERRED]
  poc-1-finetune/README.md → /Users/ashraf-macbookair/repos/projects/automation-model-trainer/poc-1-finetune/scripts/prepare_dataset.py
- `Corpus priority tiers (custom-patterns > official docs > community)` --conceptually_related_to--> `load_all_corpus()`  [INFERRED]
  poc-2-rag/README.md → /Users/ashraf-macbookair/repos/projects/automation-model-trainer/poc-2-rag/pipeline/ingest.py
- `format_sample (alpaca formatter)` --shares_data_with--> `make_sample()`  [INFERRED]
  poc-1-finetune/scripts/train_qlora.py → /Users/ashraf-macbookair/repos/projects/automation-model-trainer/poc-1-finetune/scripts/prepare_dataset.py
- `load_system_prompt()` --references--> `Playwright TS Framework-Specific System Prompt`  [EXTRACTED]
  /Users/ashraf-macbookair/repos/projects/automation-model-trainer/poc-3-prompt/chains/automation_chain.py → poc-3-prompt/system-prompts/playwright.md
- `DEFAULT_BASE_PROMPT` --semantically_similar_to--> `Automation Expert Base System Prompt`  [INFERRED] [semantically similar]
  poc-3-prompt/chains/automation_chain.py → poc-3-prompt/system-prompts/base.md

## Hyperedges (group relationships)
- **All Three POCs Implement the Same Four Tasks (generate, review, convert, qa)** — prepare_dataset_main, ingest_ingest, automation_chain_automationchain, server_generate_test, server_review_test, server_convert_test, server_ask_question, evaluate_all_run_poc1_finetune, evaluate_all_run_poc2_rag, evaluate_all_run_poc3_prompt [EXTRACTED 0.95]
- **LangGraph State Machine Nodes (load_prompt → generate → validate → hitl)** — automation_chain_load_prompt_node, automation_chain_claude_generate_node, automation_chain_validate_output_node, automation_chain_hitl_node, automation_chain_should_retry, automation_chain_build_graph [EXTRACTED 1.00]
- **POC 1 Fine-Tuning Data Pipeline (extract → convert/review pairs → JSONL → format → train)** — prepare_dataset_extract_playwright_ts, prepare_dataset_extract_java_tests, prepare_dataset_extract_postman_collections, prepare_dataset_create_convert_pairs, prepare_dataset_create_review_pairs, train_qlora_format_sample, train_qlora_train_unsloth, train_qlora_train_mlx [INFERRED 0.90]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.11
Nodes (23): BaseModel, FastAPI app (Automation Expert API), ask_question(), AskRequest, AskRequest, AutomationResponse, AutomationGenerator, AutomationResponse (+15 more)

### Community 1 - "Community 1"
Cohesion: 0.18
Nodes (15): AutomationState, build_graph(), claude_generate_node(), hitl_node(), load_few_shots(), load_prompt_node(), automation_chain.py ------------------- LangGraph chain for automation test gene, Load framework-specific system prompt and few-shots. (+7 more)

### Community 2 - "Community 2"
Cohesion: 0.24
Nodes (14): create_convert_pairs(), create_review_pairs(), extract_java_tests(), extract_playwright_ts(), extract_postman_collections(), main(), make_sample(), prepare_dataset.py ------------------ Extracts training pairs from your 5 source (+6 more)

### Community 3 - "Community 3"
Cohesion: 0.26
Nodes (12): AutomationChain, cli(), judge_output(), main(), evaluate_all.py --------------- Runs all 7 golden test cases against all three P, Heuristic judge — checks for expected markers.     For full LLM-as-Judge, see po, Call POC 2 RAG API (must be running on :8000)., Run POC 3 LangGraph chain. (+4 more)

### Community 4 - "Community 4"
Cohesion: 0.27
Nodes (9): CODE_SPLITTER (RecursiveCharacterTextSplitter), CORPUS_METADATA, ingest(), load_all_corpus(), load_corpus_dir(), ingest.py --------- Loads automation framework docs and your project patterns in, Load all supported files from a corpus subdirectory., Load all corpus subdirectories with priority ordering. (+1 more)

### Community 5 - "Community 5"
Cohesion: 0.31
Nodes (8): format_sample (alpaca formatter), load_config(), main(), train_qlora.py -------------- QLoRA fine-tuning for Qwen2.5-Coder-7B on automati, MLX fine-tuning for M4 Mac — fast iteration without GPU.     Uses mlx-lm which s, Full QLoRA training via Unsloth — use on Vast.ai A100., train_mlx(), train_unsloth()

### Community 6 - "Community 6"
Cohesion: 0.22
Nodes (9): POC 1 Fine-Tuning (concept), Rationale: QLoRA on Qwen2.5-Coder-7B for offline/private codebases, POC 2 RAG Pipeline (concept), Rationale: RAG for zero-GPU, always-up-to-date production use, POC 3 Prompt Engineering (concept), Rationale: Prompt Engineering first — fastest to ship, zero training, automation-model-trainer root README, 5 Source Projects (ai-web-automation, langgraph-hitl-agent, rag-system, AeroSense ChartQA, Jeppesen) (+1 more)

### Community 7 - "Community 7"
Cohesion: 0.83
Nodes (4): DEFAULT_BASE_PROMPT, load_system_prompt(), Automation Expert Base System Prompt, Playwright TS Framework-Specific System Prompt

## Knowledge Gaps
- **36 isolated node(s):** `prepare_dataset.py ------------------ Extracts training pairs from your 5 source`, `Extract Playwright TypeScript patterns from ai-web-automation structure.`, `Extract Java test patterns (TestNG, RestAssured, Selenium).`, `Extract Postman collections as test generation targets.`, `Cross-framework conversion pairs.     For each Playwright TS sample, create a 'c` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AutomationChain` connect `Community 3` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.396) - this node is a cross-community bridge._
- **Why does `train_mlx()` connect `Community 5` to `Community 3`?**
  _High betweenness centrality (0.271) - this node is a cross-community bridge._
- **Why does `generate_test()` connect `Community 0` to `Community 3`?**
  _High betweenness centrality (0.270) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `AutomationChain` (e.g. with `evaluate_all.py --------------- Runs all 7 golden test cases against all three P` and `Call POC 2 RAG API (must be running on :8000).`) actually correct?**
  _`AutomationChain` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `make_sample()` (e.g. with `Alpaca/ChatML training data schema` and `format_sample (alpaca formatter)`) actually correct?**
  _`make_sample()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `prepare_dataset.py ------------------ Extracts training pairs from your 5 source`, `Extract Playwright TypeScript patterns from ai-web-automation structure.`, `Extract Java test patterns (TestNG, RestAssured, Selenium).` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.11 - nodes in this community are weakly interconnected._
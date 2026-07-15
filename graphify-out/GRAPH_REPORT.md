# Graph Report - .  (2026-07-14)

## Corpus Check
- 62 files · ~27,427 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 569 nodes · 986 edges · 44 communities (31 shown, 13 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.76)
- Token cost: 27,852 input · 27,852 output

## Community Hubs (Navigation)
- [[_COMMUNITY_BaseTest + ChainedEndpointTest.java + Ch|BaseTest + ChainedEndpointTest.java + Ch]]
- [[_COMMUNITY_AeroSense ChartQA + ai-web-automation +|AeroSense ChartQA + ai-web-automation + ]]
- [[_COMMUNITY_Framework + automation_chain.py + Automa|Framework + automation_chain.py + Automa]]
- [[_COMMUNITY_examples-generated-selenium-test.java +|examples-generated-selenium-test.java + ]]
- [[_COMMUNITY_examples-generated-selenium-test.java +|examples-generated-selenium-test.java + ]]
- [[_COMMUNITY_contact-generated-selenium-test.java + C|contact-generated-selenium-test.java + C]]
- [[_COMMUNITY_contact-generated-selenium-test.java + C|contact-generated-selenium-test.java + C]]
- [[_COMMUNITY_login-generated-selenium-test.java + Aut|login-generated-selenium-test.java + Aut]]
- [[_COMMUNITY_LoginTest.java + BeforeMethod + DataProv|LoginTest.java + BeforeMethod + DataProv]]
- [[_COMMUNITY_login-generated-selenium-test.java + Aut|login-generated-selenium-test.java + Aut]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 43|Community 43]]

## God Nodes (most connected - your core abstractions)
1. `PageTests` - 17 edges
2. `PageTests` - 17 edges
3. `CartCheckoutTest` - 16 edges
4. `ContactTests` - 16 edges
5. `CartCheckoutTest` - 16 edges
6. `ContactTests` - 16 edges
7. `LoginTest` - 15 edges
8. `AuthLoginTests` - 15 edges
9. `LoginTest` - 15 edges
10. `AuthLoginTests` - 15 edges

## Surprising Connections (you probably didn't know these)
- `run_poc3_prompt()` --calls--> `AutomationChain`  [INFERRED]
  shared/utils/evaluate_all.py → poc-3-prompt/chains/automation_chain.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **POC 1 Fine-Tuning Stack** — poc_1_finetune, qwen25_coder_7b, qlora, unsloth, peft [EXTRACTED 1.00]
- **POC 2 RAG Pipeline Stack** — poc_2_rag, langchain, chromadb, crossencoder, ollama [EXTRACTED 1.00]
- **POC Evaluation Framework** — poc_1_finetune, poc_2_rag, poc_3_prompt, test_cases, pattern_library [INFERRED 0.85]

## Communities (44 total, 13 thin omitted)

### Community 0 - "BaseTest + ChainedEndpointTest.java + Ch"
Cohesion: 0.08
Nodes (14): BaseTest, ChainedEndpointTest, Test, Test, SampleRegressionTest, ChainedEndpointTest, Test, ContractValidationTest (+6 more)

### Community 1 - "AeroSense ChartQA + ai-web-automation + "
Cohesion: 0.09
Nodes (34): AeroSense ChartQA, ai-web-automation, ChromaDB, Claude API / Anthropic API, CrossEncoder, FastAPI, Jeppesen TestNG/Java, LangChain (+26 more)

### Community 2 - "Framework + automation_chain.py + Automa"
Cohesion: 0.10
Nodes (31): Framework, AutomationChain, AutomationState, build_graph(), claude_generate_node(), cli(), hitl_node(), load_few_shots() (+23 more)

### Community 3 - "examples-generated-selenium-test.java + "
Cohesion: 0.18
Nodes (9): AfterEach, BeforeEach, DisplayName, String, Test, TestMethodOrder, WebDriver, WebDriverWait (+1 more)

### Community 4 - "examples-generated-selenium-test.java + "
Cohesion: 0.18
Nodes (9): AfterEach, BeforeEach, DisplayName, String, Test, TestMethodOrder, WebDriver, WebDriverWait (+1 more)

### Community 5 - "contact-generated-selenium-test.java + C"
Cohesion: 0.18
Nodes (9): ContactTests, AfterEach, BeforeEach, DisplayName, String, Test, TestMethodOrder, WebDriver (+1 more)

### Community 6 - "contact-generated-selenium-test.java + C"
Cohesion: 0.18
Nodes (9): ContactTests, AfterEach, BeforeEach, DisplayName, String, Test, TestMethodOrder, WebDriver (+1 more)

### Community 7 - "login-generated-selenium-test.java + Aut"
Cohesion: 0.18
Nodes (9): AuthLoginTests, AfterEach, BeforeEach, DisplayName, String, Test, TestMethodOrder, WebDriver (+1 more)

### Community 8 - "LoginTest.java + BeforeMethod + DataProv"
Cohesion: 0.17
Nodes (7): BeforeMethod, DataProvider, LoginPage, Object, String, Test, LoginTest

### Community 9 - "login-generated-selenium-test.java + Aut"
Cohesion: 0.18
Nodes (9): AuthLoginTests, AfterEach, BeforeEach, DisplayName, String, Test, TestMethodOrder, WebDriver (+1 more)

### Community 10 - "Community 10"
Cohesion: 0.17
Nodes (7): BeforeMethod, DataProvider, LoginPage, Object, String, Test, LoginTest

### Community 11 - "Community 11"
Cohesion: 0.19
Nodes (9): AfterEach, BeforeEach, DisplayName, String, Test, TestMethodOrder, WebDriver, WebDriverWait (+1 more)

### Community 12 - "Community 12"
Cohesion: 0.19
Nodes (9): AfterEach, BeforeEach, DisplayName, String, Test, TestMethodOrder, WebDriver, WebDriverWait (+1 more)

### Community 13 - "Community 13"
Cohesion: 0.19
Nodes (15): BaseModel, ask_question(), AskRequest, AutomationResponse, convert_test(), ConvertRequest, generate_test(), GenerateRequest (+7 more)

### Community 14 - "Community 14"
Cohesion: 0.25
Nodes (5): CartCheckoutTest, BeforeMethod, CartPage, InventoryPage, Test

### Community 15 - "Community 15"
Cohesion: 0.25
Nodes (5): CartCheckoutTest, BeforeMethod, CartPage, InventoryPage, Test

### Community 16 - "Community 16"
Cohesion: 0.23
Nodes (4): InventoryTest, BeforeMethod, InventoryPage, Test

### Community 17 - "Community 17"
Cohesion: 0.23
Nodes (4): InventoryTest, BeforeMethod, InventoryPage, Test

### Community 18 - "Community 18"
Cohesion: 0.26
Nodes (14): create_convert_pairs(), create_review_pairs(), extract_java_tests(), extract_playwright_ts(), extract_postman_collections(), main(), make_sample(), Path (+6 more)

### Community 19 - "Community 19"
Cohesion: 0.25
Nodes (4): DataProvider, Object, Test, NegativeEdgeCaseTest

### Community 20 - "Community 20"
Cohesion: 0.25
Nodes (4): DataProvider, Object, Test, NegativeEdgeCaseTest

### Community 23 - "Community 23"
Cohesion: 0.33
Nodes (3): CrudWorkflowTest, Test, UserPayload

### Community 26 - "Community 26"
Cohesion: 0.36
Nodes (8): load_config(), main(), Path, train_qlora.py -------------- QLoRA fine-tuning for Qwen2.5-Coder-7B on automa, MLX fine-tuning for M4 Mac — fast iteration without GPU.     Uses mlx-lm which, Full QLoRA training via Unsloth — use on Vast.ai A100., train_mlx(), train_unsloth()

## Knowledge Gaps
- **1 isolated node(s):** `Shared Utils`
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LoginTest` connect `LoginTest.java + BeforeMethod + DataProv` to `BaseTest + ChainedEndpointTest.java + Ch`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `LoginTest` connect `Community 10` to `BaseTest + ChainedEndpointTest.java + Ch`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `CartCheckoutTest` connect `Community 15` to `BaseTest + ChainedEndpointTest.java + Ch`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **What connects `prepare_dataset.py ------------------ Extracts training pairs from your 5 sour`, `Extract Playwright TypeScript patterns from ai-web-automation structure.`, `Extract Java test patterns (TestNG, RestAssured, Selenium).` to the rest of the system?**
  _39 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `BaseTest + ChainedEndpointTest.java + Ch` be split into smaller, more focused modules?**
  _Cohesion score 0.07973421926910298 - nodes in this community are weakly interconnected._
- **Should `AeroSense ChartQA + ai-web-automation + ` be split into smaller, more focused modules?**
  _Cohesion score 0.08739495798319327 - nodes in this community are weakly interconnected._
- **Should `Framework + automation_chain.py + Automa` be split into smaller, more focused modules?**
  _Cohesion score 0.09747899159663866 - nodes in this community are weakly interconnected._
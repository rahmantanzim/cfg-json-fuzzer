# CFG-Fuzzing: Deterministic Grammar-Based JSON Fuzzer

A highly controlled, hybrid fuzzing pipeline engineered to systematically stress-test JSON parsers—specifically targeting Python's heavily guarded native C-backend `json` module. 

Traditional mutational fuzzers often fail against structured data formats due to the "syntactic bottleneck" (random mutations cause immediate syntax errors, preventing deep code exploration). This project solves that by utilizing a formal **Context-Free Grammar (CFG)** and an **Abstract Syntax Tree (AST)** to generate syntactically flawless payloads, applying targeted semantic corruption *before* serialization to uncover deep memory-management flaws like stack exhaustion.

---

## Key Features

* **RFC 8259 Compliant CFG:** Generates deeply nested, 100% syntactically valid JSON structures to bypass initial parser validations.
* **AST-Level Mutation:** Anomalies are injected directly into the in-memory Abstract Syntax Tree prior to string serialization, ensuring contextually accurate exploits.
* **Cryptographic Crash Deduplication:** Uses MD5 hashing on exception stack traces to automatically filter out duplicate system faults and isolate unique zero-day root causes.
* **Coverage-Ready:** Fully instrumented for white-box testing and statement coverage tracking.

---

## System Architecture

The fuzzer operates in a strict four-phase pipeline:

1. **CFG Definition (`grammar.py`):** Defines the strict rules for valid JSON generation.
2. **AST Construction (`generator.py`):** Builds the payload in memory as a node tree. Features a `max_depth` safety net to prevent infinite recursive generation.
3. **Semantic Anomaly Injection (`mutator.py`):** Traverses the AST and applies deterministic heuristics:
    * **Boundary Injection:** Substitutes valid `<number>` nodes with `NaN`, `Infinity`, or extreme integers.
    * **Malicious Strings:** Injects format string specifiers (`%s%n%x%d`) or null bytes.
    * **Maximum Nesting (DoS Trigger):** Wraps payloads in massive layers of structural brackets to force `RecursionError` and stack exhaustion.
4. **Orchestrator Execution (`fuzzer.py`):** Fires the serialized payloads directly into `json.loads()`, handles standard `JSONDecodeError` rejections safely, and logs unhandled system faults to the disk.

---

## 📂 Project Structure

```text
CFG-fuzzing/
├── crashes/             # Auto-generated logs of unique payloads that successfully crashed the parser
├── htmlcov/             # Auto-generated HTML coverage dashboard (created after running tests)
├── fuzzer.py            # Main execution engine and crash deduplication monitor
├── generator.py         # CFG-based JSON generator (AST expansion)
├── grammar.py           # Context-Free Grammar definitions
├── mutator.py           # AST-level anomaly injection engine
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore configurations
└── README.md            # Project documentation
```
---

## 📂 Installation & Setup

1. **Clone the repository**
`git clone <rahmantanzim/cfg-json-fuzzer>`
`cd CFG-fuzzing`

2. **Install dependencies**
`pip install -r requirements.txt`

3. **Run the Fuzzer with Coverage Tracking:** To execute the fuzzer and track how much of the target system is explored:
`python3 -m coverage run fuzzer.py`

4. **View Terminal Metrics:** To view a quick breakdown of your statement coverage in the terminal:
`python3 -m coverage report -m`

5. **Generate the Interactive Dashboard:** To generate a highly readable, line-by-line HTML coverage report:
`python3 -m coverage html`

Open `htmlcov/index.html` in your web browser to view the results.

---

## Campaign Metrics & Results

Based on our latest 5,000-iteration automated fuzzing campaign targeting Python's native json.loads():

1. **Execution Speed:** 5,000 payloads generated, mutated, and executed natively in 0.89 seconds (7.10 seconds under full coverage instrumentation).
2. **Syntactic Bypass:** 2,949 payloads parsed entirely successfully (proving the CFG bypassed the syntactic bottleneck).
    * 1377 payloads were safely rejected due to deliberate structural corruption.
3. **Vulnerability Discovery:** Triggered 674 total system crashes (primarily RecursionError).
4. **Deduplication** The cryptographic engine successfully collapsed those 674 crashes into exactly 2 Unique Root Vulnerabilities.
5. **Code Coverage:** Achieved a highly robust 85% Overall Code Coverage across the fuzzer ecosystem (including 99% coverage on the core orchestrator and 100% on the grammar definitions).

---
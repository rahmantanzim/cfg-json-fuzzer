# CFG-Fuzzing: Grammar-Based JSON Fuzzer

A highly controlled, hybrid fuzzing pipeline designed to stress-test JSON parsers—specifically targeting Python's heavily guarded native C-backend `json` module. This project utilizes a **Producer-Consumer architecture** to bypass standard syntactic validation and uncover deep memory-management flaws such as Stack Exhaustion or Recursion Errors.

## System Architecture

The fuzzer operates in a strict two-phase pipeline:

1. **The Producer (Generator - `generator.py`):** Uses Abstract Syntax Tree (AST) expansion based on a custom Context-Free Grammar (CFG). It generates deep, highly varied, and 100% syntactically valid JSON payloads to safely bypass the parser's initial security gates. It features a `max_depth` safety net to prevent infinite recursion during generation.
2. **The Consumer (Mutator - `mutator.py`):** Takes the syntactically valid JSON and applies targeted deterministic corruption to break the parser's logic and memory limits.
3. **The Orchestrator (`fuzzer.py`):** Fires the payloads directly into `json.loads()`, safely handling standard `JSONDecodeError` rejections while specifically logging critical system failures like `RecursionError`.

## Mutation Strategies

The Mutator deploys four primary deterministic heuristics:
* **Maximum Nesting (The DoS Trigger):** Wraps valid payloads in 500–1500 layers of structural brackets (`[[[[...]]]]`). This specifically targets the call stack, forcing a `RecursionError`.
* **Boundary Injection:** Targets integer overflow by replacing valid numbers with extreme edge cases (e.g., `-999999999999...999`).
* **Structure Corruption:** Randomly strips essential structural delimiters (like `:` or `,`) to test basic syntax exception handling.
* **Malicious Strings:** Replaces valid strings with null bytes (`\u0000`) and format string payloads.

## 📂 Project Structure

```text
CFG-fuzzing/
├── crashes/             # Auto-generated logs of payloads that successfully crashed the parser
├── fuzzer.py            # Main execution engine and exception monitor
├── generator.py         # CFG-based JSON generator (AST expansion)
├── grammar.py           # Context-Free Grammar definitions
├── mutator.py           # Anomaly injection engine
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore configurations
└── README.md            # Project documentation 

```


## Installation & Setup
1. Clone the repository:
```
git clone <your-repository-url>
cd CFG-fuzzing
```
2. Set up the environment:
It is recommended to use a virtual environment.
```
python3 -m venv venv
source venv/bin/activate
```
3. Install dependencies:
```
pip install -r requirements.txt
```

## Usage & Generating Reports
Run the Fuzzer with Coverage Tracking:
To execute the fuzzer and track how much of the system is explored:

```
python3 -m coverage run fuzzer.py
```

Note: Any payload that breaches the parser's limits will be saved as a .json file in the crashes/ directory.

View Metrics & Coverage:
To view the terminal report:

```
python3 -m coverage report -m
```
To generate an interactive HTML coverage report (opens in htmlcov/index.html):

```
python3 -m coverage html
```
## Campaign Metrics & Results
Based on the latest automated fuzzing campaign:

# Execution Speed: 5,000 payloads generated and tested in ~0.62 seconds.

# Critical Crashes: Successfully triggered 1,095 RecursionError crashes (Denial of Service via Stack Exhaustion) against Python's native json.loads().

# System Defense: 1,378 payloads were safely rejected by the parser (JSONDecodeError), and 2,527 were parsed as valid.

# Code Coverage: Achieved a highly robust 82% Overall Code Coverage (87% on the core fuzzer engine), successfully exploring the deepest exception-handling blocks.
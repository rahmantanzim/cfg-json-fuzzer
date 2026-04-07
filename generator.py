import random
import re
import json
from grammar import JSON_GRAMMAR

class JSONGenerator:
    def __init__(self, grammar, max_depth=8):
        self.grammar = grammar
        self.max_depth = max_depth

    def generate(self, symbol="<start>", current_depth=0):
        # 1. Base Case: If it's a raw string/terminal, return it directly
        if not (symbol.startswith("<") and symbol.endswith(">")):
            return symbol

        # 2. Depth Limit Safety Net (Only triggers if it goes too deep)
        if current_depth >= self.max_depth:
            fallbacks = {
                "<value>": random.choice(["\"fuzz_deep\"", "9999", "null"]),
                "<object>": "{}",
                "<array>": "[]",
                "<string>": "\"limit_string\"",
                "<number>": "0",
                "<members>": "\"limit_key\": \"limit_val\"",
                "<elements>": "null",
                "<pair>": "\"limit_key\": 0"
            }
            return fallbacks.get(symbol, "")

        options = self.grammar.get(symbol, [symbol])
        
        # 3. SMART HEURISTICS (To guarantee large, nested JSONs)
        # Force it to pick nested structures early on, not empty {} or []
        if current_depth < 3 and symbol in ["<object>", "<array>"]:
            rich_options = [opt for opt in options if opt not in ["{}", "[]"]]
            if rich_options:
                options = rich_options
                
        # Prevent horizontal infinite loops (arrays with 1000 items)
        if current_depth > 5 and symbol in ["<members>", "<elements>"]:
            short_options = [opt for opt in options if "," not in opt]
            if short_options:
                options = short_options

        expansion = random.choice(options)

        # 4. PROPER AST EXPANSION (The actual fix)
        # Instead of replacing strings blindly, we split the rule into tokens 
        # and evaluate each token independently.
        parts = re.split(r'(<[^>]+>)', expansion)
        
        result = ""
        for part in parts:
            if part.startswith("<") and part.endswith(">"):
                # Recursively expand tags
                result += self.generate(part, current_depth + 1)
            else:
                # Add normal text (brackets, colons, commas)
                result += part

        # Clean up weird spacing for a perfect JSON format
        return result.replace(" ,", ",").replace(" :", ":").replace("{ ", "{").replace(" }", "}").strip()

# --- Validation Block ---
if __name__ == "__main__":
    generator = JSONGenerator(JSON_GRAMMAR, max_depth=8)
    print("--- Generating Massive & Valid JSON ---")
    
    for i in range(3):
        raw_json = generator.generate()
        print(f"\n[Sample {i+1}]: {raw_json}")
        
        try:
            json.loads(raw_json)
            print("Status: VALID JSON ✓")
        except json.JSONDecodeError as e:
            print(f"Status: INVALID ✗ (Error: {e})")
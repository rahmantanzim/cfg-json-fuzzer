import random
import re
import json
from grammar import JSON_GRAMMAR

class ASTNode:
    def __init__(self, symbol, children=None, value=None):
        self.symbol = symbol      # The grammar tag, e.g., "<object>" or "<number>"
        self.children = children or [] # Child Abstract Syntax Tree nodes
        self.value = value        # Terminal string value (if it's a leaf node)

    def to_string(self):
        """Recursively resolves the tree into a final JSON string."""
        if self.value is not None:
            return str(self.value)
        return "".join(child.to_string() for child in self.children)

class JSONGenerator:
    def __init__(self, grammar, max_depth=30):
        self.grammar = grammar
        self.max_depth = max_depth

    def generate(self, symbol="<start>", current_depth=0) -> ASTNode:
        # 1. Base Case: If it's a terminal, return a leaf node
        if not (symbol.startswith("<") and symbol.endswith(">")):
            return ASTNode(symbol=symbol, value=symbol)

        # 2. Depth Limit Safety Net
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
            fallback_val = fallbacks.get(symbol, "")
            return ASTNode(symbol=symbol, value=fallback_val)

        options = self.grammar.get(symbol, [symbol])

       # Smart Heuristics
        # 1. Force nested structures early on
        if current_depth < 3 and symbol in ["<object>", "<array>"]:
            rich_options = [opt for opt in options if opt not in ["{}", "[]"]]
            if rich_options:
                options = rich_options

        # 2. Control horizontal spread (array/object width)
        if symbol in ["<members>", "<elements>"]:
            if current_depth > 15:
                # Cutoff: Force lists to terminate if we are too deep
                short_options = [opt for opt in options if "," not in opt]
                if short_options:
                    options = short_options
            elif current_depth < 5:
                # Expansion: Multiply recursive choices (75% chance) to force wide structures
                recursive_options = [opt for opt in options if "," in opt]
                if recursive_options:
                    options = options + recursive_options * 3

        expansion = random.choice(options)

        # 4. AST EXPANSION
        node = ASTNode(symbol=symbol)
        # Tokenize the expansion properly. 
        # This regex isolates tags <tag> and captures all literal characters in between.
        tokens = re.findall(r'<[^>]+>|[^<]+', expansion)
        
        for token in tokens:
            if token.startswith("<") and token.endswith(">"):
                # Only increment depth for structural tokens
                next_depth = current_depth + 1 if token in ["<object>", "<array>"] else current_depth
                child_node = self.generate(token, next_depth)
                node.children.append(child_node)
            else:
                # Add terminal characters (like {, }, :, ,) as leaf nodes
                # We strip spaces here to organically prevent the weird spacing issues you had before
                clean_token = token.strip()
                if clean_token: 
                    node.children.append(ASTNode(symbol="TERMINAL", value=clean_token))

        return node
    
# ******************** Validation Block  ********************
if __name__ == "__main__":
    generator = JSONGenerator(JSON_GRAMMAR, max_depth=30)
    print("--- Generating Massive & Valid JSON ---")
    for i in range(10):
        ast_root = generator.generate()
        raw_json = ast_root.to_string() # Collapse the tree into a string
        print(f"\n[Sample {i+1}]: {raw_json}")
        try:
            import json
            json.loads(raw_json)
            print("Status: VALID JSON")
        except json.JSONDecodeError as e:
            print(f"Status: INVALID JSON (Error: {e})")

import random
import copy
from generator import ASTNode

class JSONMutator:
    """
    A semantic mutator that iterates an AST to apply targeted
    stress-testing heuristics before string serialization.
    """
    def __init__(self):
        # 1. Extreme boundary values to test integer overflows and precision loss
        self.boundary_numbers = [
            "999999999999999999999999999999", 
            "-999999999999999999999999999999",
            "2.2250738585072011e-308", 
            "NaN", 
            "Infinity"
        ]
        # 2. Very weird data to test memory corruption or logic flaws
        self.string_anomalies = [
            "\"%s%n%x%d\"",           # Format string
            "\"" + "A"*5000 + "\"",   # Buffer overflow simulation
            "\"\\u0000\\u0001\"",     # Null byte injection
            "null",
            "undefined"
        ]

    def _get_nodes(self, node: ASTNode, symbol: str):
        """Recursively finds all nodes matching a specific grammar symbol."""
        found = []
        if node.symbol == symbol:
            found.append(node)
        for child in node.children:
            found.extend(self._get_nodes(child, symbol))
        return found

    def mutate(self, ast_og: ASTNode) -> str:
        """Applies one mutation strategy to the AST or serialized string."""
        ast_root = copy.deepcopy(ast_og)
        strategies = ["numbers", "strings", "structure", "nesting"]
        chosen_strategy = random.choice(strategies)

        # 1. Semantic Mutations (AST-Level)
        if chosen_strategy == "numbers":
            number_nodes = self._get_nodes(ast_root, "<number>")
            if number_nodes:
                target = random.choice(number_nodes)
                # Mutate the terminal value inside the <number> node
                if target.children:
                    target.children[0].value = random.choice(self.boundary_numbers)

        elif chosen_strategy == "strings":
            string_nodes = self._get_nodes(ast_root, "<string>")
            if string_nodes:
                target = random.choice(string_nodes)
                if target.children:
                    target.children[0].value = random.choice(self.string_anomalies)

        # Serialize the AST into a string for the remaining string-level strategies
        json_str = ast_root.to_string()

        # 2. Syntax/Structural Mutations (String-Level)
        if chosen_strategy == "structure":
            tokens_to_corrupt = [",", "{", "}", "[", "]", ":"]
            target = random.choice(tokens_to_corrupt)
            if target in json_str:
                json_str = json_str.replace(target, "", 1)

        elif chosen_strategy == "nesting":
            depth = random.randint(500, 1500)
            if random.choice([True, False]):
                prefix = '{"nested_key": ' * depth
                suffix = '}' * depth
            else:
                prefix = '[' * depth
                suffix = ']' * depth
            json_str = f"{prefix}{json_str}{suffix}"

        return json_str
# --- Quick Test Block ---
if __name__ == "__main__":
    from generator import JSONGenerator, JSON_GRAMMAR # Need these to generate an AST
    
    # 1. Setup
    generator = JSONGenerator(JSON_GRAMMAR)
    mutator = JSONMutator()
    
    # 2. Generate a valid ASTNode instead of a raw string
    ast_root = generator.generate()
    original_json = ast_root.to_string()
    
    print("Original AST Serialization:", original_json)
    
    # 3. Test the unified mutation method
    print("\n--- Testing Mutation Pipeline ---")
    mutated_result = mutator.mutate(ast_root)
    print("Mutated Result:", mutated_result)
    
    # Verify if it's still a valid string (unless it was a structure/nesting mutation)
    print("\nNote: Valid JSON status depends on whether a 'structure' or 'nesting' mutation was chosen.")
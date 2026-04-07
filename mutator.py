# import random
# import re

# class JSONMutator:
#     """
#     A deterministic mutator designed to apply specific stress-testing 
#     heuristics to valid JSON strings.
#     """
#     def __init__(self):
#         # 1. Extreme boundary values to test integer overflows and precision loss
#         self.boundary_numbers = [
#             "999999999999999999999999999999", 
#             "-999999999999999999999999999999", 
#             "2.2250738585072011e-308",  # Float min
#             "NaN", 
#             "Infinity"
#         ]
#         # 2. Malicious payloads to test memory corruption or logic flaws
#         self.string_anomalies = [
#             "\"%s%n%x%d\"",          # Format string vulnerabilities
#             "\"" + "A" * 50000 + "\"", # Buffer overflow simulation
#             "\"\\u0000\\u0001\"",    # Null byte injection
#             "null",
#             "undefined"
#         ]

#     def mutate(self, valid_json: str) -> str:
#         """Applies one random mutation strategy to the JSON string."""
#         strategies = [
#             self._mutate_numbers,
#             self._mutate_strings,
#             self._corrupt_structure,
#             self._force_nesting
#         ]
        
#         # Pick a random strategy and execute
#         chosen_strategy = random.choice(strategies)
#         return chosen_strategy(valid_json)

#     def _mutate_numbers(self, json_str: str) -> str:
#         """Finds numbers in the JSON and replaces them with extreme boundaries."""
#         # Matches standalone digits/numbers in JSON values
#         number_pattern = re.compile(r'(?<=: )\d+(?=[,\n} ])|(?<=\[ )\d+(?=[,\n\] ])')
#         matches = number_pattern.findall(json_str)
        
#         if not matches:
#             # Fallback to structure corruption if no numbers exist
#             return self._corrupt_structure(json_str)
            
#         target = random.choice(matches)
#         anomaly = random.choice(self.boundary_numbers)
#         return json_str.replace(target, anomaly, 1)

#     def _mutate_strings(self, json_str: str) -> str:
#         """Replaces valid string values with malicious payloads."""
#         # Matches string values (not keys)
#         string_pattern = re.compile(r'(?<=: )"[^"]*"(?=[,\n} ])|(?<=\[ )"[^"]*"(?=[,\n\] ])')
#         matches = string_pattern.findall(json_str)
        
#         if not matches:
#             # Fallback to nesting if no strings exist
#             return self._force_nesting(json_str)
            
#         target = random.choice(matches)
#         anomaly = random.choice(self.string_anomalies)
#         return json_str.replace(target, anomaly, 1)

#     def _corrupt_structure(self, json_str: str) -> str:
#         """Randomly deletes crucial structural tokens like commas or brackets (Empty Productions)."""
#         tokens_to_corrupt = [",", "{", "}", "[", "]", ":"]
#         target = random.choice(tokens_to_corrupt)
        
#         # If the token exists, remove the first occurrence we find
#         if target in json_str:
#             return json_str.replace(target, "", 1)
#         return json_str

#     def _force_nesting(self, json_str: str) -> str:
#         """Wraps the JSON in an extreme number of arrays/objects to test recursion limits."""
#         # This will trigger RecursionError or Stack Overflow
#         depth = random.randint(500, 1500) 
        
#         if random.choice([True, False]):
#             prefix = '{"nested_key": ' * depth
#             suffix = '}' * depth
#             return f"{prefix}{json_str}{suffix}"
#         else:
#             prefix = '[' * depth
#             suffix = ']' * depth
#             return f"{prefix}{json_str}{suffix}"

# # --- Quick Test Block ---
# if __name__ == "__main__":
#     mutator = JSONMutator()
#     sample_json = '{"key": 100, "data": "test"}'
    
#     print("Original:", sample_json)
#     print("\n--- Testing All 4 Strategies ---")
#     print("Numbers Mutated:", mutator._mutate_numbers(sample_json))
#     print("Strings Mutated:", mutator._mutate_strings(sample_json))
#     print("Structure Corrupted:", mutator._corrupt_structure(sample_json))
    
#     # Just printing a snippet of the massive nested string so it doesn't flood your terminal
#     nested = mutator._force_nesting(sample_json)
#     print(f"Massive Nesting (Length: {len(nested)} chars):", nested[:50] + " ... " + nested[-50:])
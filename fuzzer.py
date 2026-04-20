import json
import os
import sys
import time
import hashlib
from generator import JSONGenerator
from mutator import JSONMutator
from grammar import JSON_GRAMMAR

class JSONFuzzer:
    """
    The core orchestrator. Runs the generation-mutation-execution loop,
    logs unhandled exceptions, and deduplicates crashes using hashing.
    """
    def __init__(self, iterations: int = 5000, max_depth: int = 30):
        self.iterations = iterations
        self.max_valid_length = 0
        self.longest_payload = ""
        # Generator: AST-based
        self.generator = JSONGenerator(JSON_GRAMMAR, max_depth=max_depth)
        self.mutator = JSONMutator()
        self.crash_dir = "crashes"
        if not os.path.exists(self.crash_dir):
            os.makedirs(self.crash_dir)
            
        # To track unique crashes
        self.seen_crashes = set()
        
        self.metrics = {
            "total_executed": 0,
            "syntactically_valid": 0,
            "caught_by_parser": 0,
            "unique_crashes": 0,
            "duplicate_crashes": 0
        }

    def _log_crash(self, payload: str, error_type: str, error_msg: str):
        """Hashes the error to prevent duplicate logging, then dumps to disk."""
        # 1. Create a unique signature (hash) for this crash type
        crash_signature = f"{error_type}:{error_msg}".encode('utf-8')
        crash_hash = hashlib.md5(crash_signature).hexdigest()

        # 2. Check for duplication
        if crash_hash in self.seen_crashes:
            self.metrics["duplicate_crashes"] += 1
            return # Don't save if we've seen this exact error before

        # 3. New unique crash found
        self.seen_crashes.add(crash_hash)
        self.metrics["unique_crashes"] += 1
        
        timestamp = int(time.time() * 1000)
        filename = os.path.join(self.crash_dir, f"crash_{error_type}_{timestamp}.json")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"/* ERROR TYPE: {error_type} */\n")
            f.write(f"/* MESSAGE: {error_msg} */\n")
            f.write("/* PAYLOAD BELOW */\n")
            f.write(payload)

    def start_fuzzing(self):
        print(f"[*] Starting Grammar-based Fuzzing Campaign...")
        print(f"[*] Target Iterations: {self.iterations}\n")
        
        start_time = time.time()
        for i in range(self.iterations):
            self.metrics["total_executed"] += 1
            
            # 1. Generate AST
            ast_root = self.generator.generate()
            
            # 2. Mutate AST -> String
            mutated_input = self.mutator.mutate(ast_root)
            
            # 3. Execution
            try:
                json.loads(mutated_input)
                self.metrics["syntactically_valid"] += 1
                
                # Check if this is the biggest valid payload we've seen
                if len(mutated_input) > self.max_valid_length:
                    self.max_valid_length = len(mutated_input)
                    self.longest_payload = mutated_input
                    
            except json.JSONDecodeError:
                self.metrics["caught_by_parser"] += 1
            except Exception as e:
                # Log critical crashes (Recursion, Memory, etc.)
                self._log_crash(mutated_input, type(e).__name__, str(e))

            # Live Telemetry
            if (i + 1) % 500 == 0:
                sys.stdout.write(f"\r[~] Executed: {i + 1}/{self.iterations} | Unique Crashes: {self.metrics['unique_crashes']} | Duplicates: {self.metrics['duplicate_crashes']}")
                sys.stdout.flush()

        self._print_summary(time.time() - start_time)

    def _print_summary(self, elapsed_time: float):
        print("\n\n" + "="*45)
        print("           CAMPAIGN SUMMARY")
        print("="*45)
        print(f"Time Elapsed       : {elapsed_time:.2f} seconds")
        print(f"Total Payloads     : {self.metrics['total_executed']}")
        print(f"Valid Parsed       : {self.metrics['syntactically_valid']}")
        print(f"Rejected Safely    : {self.metrics['caught_by_parser']}")
        print(f"Unique Crashes     : {self.metrics['unique_crashes']}")
        print(f"Duplicate Crashes  : {self.metrics['duplicate_crashes']}")
        print("="*45)
        print(f"Longest Valid Payload: {self.max_valid_length} characters")
        
        if self.metrics['unique_crashes'] > 0:
            print(f"[*] Check the '{self.crash_dir}' directory for unique vulnerability payloads.")

if __name__ == "__main__":
    engine = JSONFuzzer(iterations=5000)
    engine.start_fuzzing()
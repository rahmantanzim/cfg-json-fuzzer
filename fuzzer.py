# import json
# import os
# import sys
# import time
# from generator import JSONGenerator
# from mutator import JSONMutator
# from grammar import JSON_GRAMMAR

# class JSONFuzzer:
#     """
#     The core orchestrator. Runs the generation-mutation-execution loop
#     and logs unhandled exceptions.
#     """
#     def __init__(self, iterations: int = 5000, max_depth: int = 8):
#         self.iterations = iterations
#         self.generator = JSONGenerator(JSON_GRAMMAR, max_depth=max_depth)
#         self.mutator = JSONMutator()
#         self.crash_dir = "crashes"
        
#         if not os.path.exists(self.crash_dir):
#             os.makedirs(self.crash_dir)
            
#         self.metrics = {
#             "total_executed": 0,
#             "syntactically_valid": 0, # Passed without errors
#             "caught_by_parser": 0,    # standard JSONDecodeError
#             "critical_crashes": 0     # MemoryError, RecursionError, etc.
#         }

#     def _log_crash(self, payload: str, error_type: str, error_msg: str):
#         """Dumps the crash payload to disk for later analysis."""
#         timestamp = int(time.time() * 1000)
#         filename = os.path.join(self.crash_dir, f"crash_{error_type}_{timestamp}.json")
        
#         with open(filename, "w", encoding="utf-8") as f:
#             f.write(f"/* ERROR TYPE: {error_type} */\n")
#             f.write(f"/* MESSAGE: {error_msg} */\n")
#             f.write("/* PAYLOAD BELOW */\n")
#             f.write(payload)
            
#         return filename

#     def start_fuzzing(self):
#         print(f"[*] Starting Grammar-based Fuzzing Campaign...")
#         print(f"[*] Target Iterations: {self.iterations}\n")
        
#         start_time = time.time()

#         for i in range(self.iterations):
#             self.metrics["total_executed"] += 1
            
#             # 1. Generate deep, valid JSON
#             base_input = self.generator.generate()
            
#             # 2. Corrupt it strategically
#             mutated_input = self.mutator.mutate(base_input)

#             # 3. Execution Engine (Targeting Python's built-in JSON module)
#             try:
#                 json.loads(mutated_input)
#                 self.metrics["syntactically_valid"] += 1
                
#             except json.JSONDecodeError:
#                 # The parser worked correctly and blocked the bad syntax
#                 self.metrics["caught_by_parser"] += 1
                
#             except RecursionError as e:
#                 self.metrics["critical_crashes"] += 1
#                 self._log_crash(mutated_input, "RecursionError", str(e))
#                 print(f"\n[!] Recursion Limit Hit at iteration {i+1}!")
                
#             except MemoryError as e:
#                 self.metrics["critical_crashes"] += 1
#                 self._log_crash(mutated_input, "MemoryError", str(e))
#                 print(f"\n[!] Memory Exhaustion at iteration {i+1}!")
                
#             except Exception as e:
#                 # Catch-all for unexpected Zero-Days or weird logic flaws
#                 self.metrics["critical_crashes"] += 1
#                 self._log_crash(mutated_input, type(e).__name__, str(e))
#                 print(f"\n[!] Unhandled Exception ({type(e).__name__}) at iteration {i+1}!")

#             # Live CLI Telemetry
#             if (i + 1) % 500 == 0:
#                 sys.stdout.write(f"\r[~] Executed: {i + 1}/{self.iterations} | Crashes: {self.metrics['critical_crashes']}")
#                 sys.stdout.flush()

#         self._print_summary(time.time() - start_time)

#     def _print_summary(self, elapsed_time: float):
#         print("\n\n" + "="*40)
#         print("          CAMPAIGN SUMMARY")
#         print("="*40)
#         print(f"Time Elapsed      : {elapsed_time:.2f} seconds")
#         print(f"Total Payloads    : {self.metrics['total_executed']}")
#         print(f"Valid Parsed      : {self.metrics['syntactically_valid']}")
#         print(f"Rejected Safely   : {self.metrics['caught_by_parser']}")
#         print(f"Critical Crashes  : {self.metrics['critical_crashes']}")
#         print("="*40)
#         if self.metrics['critical_crashes'] > 0:
#             print(f"[*] Check the '{self.crash_dir}' directory for vulnerability payloads.")

# if __name__ == "__main__":
#     # Running 5000 iterations to stress test the pipeline
#     engine = JSONFuzzer(iterations=5000)
#     engine.start_fuzzing()
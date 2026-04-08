# A Complete Context-Free Grammar (CFG) for JSON 
# This follows the official JSON structural standards (RFC 8259).
# NON-TERMINALS: Represented by <tags>. These are structural rules that expand further.
# TERMINALS: Plain strings, numbers, or symbols (e.g., "{", ":", "true"). 
JSON_GRAMMAR = {
    # starting symbol of the grammar
    "<start>": ["<json>"],
    
    # A JSON structure can be either an Object or an Array
    "<json>": ["<object>", "<array>"],
    
    # Object can be empty {} or contain key-value pairs { members }
    "<object>": [
        "{}", 
        "{ <members> }"
    ],
    # Members are recursive to allow multiple key-value pairs separated by commas
    "<members>": [
        "<pair>", 
        "<pair> , <members>"
    ],
    # A pair consists of a string key, a colon, and a value
    "<pair>": [
        "<string> : <value>"
    ],
    
    # Array definition: can be empty [] or contain elements [ elements ]
    "<array>": [
        "[]", 
        "[ <elements> ]"
    ],
    # Elements are recursive to allow multiple values separated by commas
    "<elements>": [
        "<value>", 
        "<value> , <elements>"
    ],
    
    # Supported JSON value types
    "<value>": [
        "<string>", 
        "<number>", 
        "<object>", 
        "<array>", 
        "true", 
        "false", 
        "null"
    ],
    
    # Basic string definitions including empty strings and special characters
    "<string>": [
        "\"\"", 
        "\"fuzz_test\"", 
        "\"json_data\"", 
        "\"!@#$%^&*()\"", 
        "\"1234567890\""
    ],
    
    # Numeric definitions covering integers, floats, and scientific notation
    "<number>": [
        "0", 
        "1", 
        "-1", 
        "3.14159", 
        "1.0e10", 
        "-0.0001", 
        "999999"
    ]
}
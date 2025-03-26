import sys
import json
import copy

from pipeline import fetch_and_decode
from pipeline import rename_and_dispatch

def main():
    if len(sys.argv) != 3:
        print("Error use the following command: python simulator.py input.json output.json")
        return

    input = sys.argv[1]
    output = sys.argv[2]

    # Load input 
    with open(input) as f:
        instructions = json.load(f)

    # Initialize processor state
    state = {
        "ActiveList" : [],
        "BusyBitTable": [False]*64,
        "DecodedPCs": [], 
        "Exception": False,
        "ExceptionPC": 0,
        "FreeList": list(range(32, 64)),
        "IntegerQueue": [],
        "PC": 0,
        "PhysicalRegisterFile": [0]*64,
        "RegisterMapTable": list(range(32))
    }

    trace = []

    # Initial state 
    trace.append(copy.deepcopy(state))

    DIR = [] # Decoded Instruction Register

    # Parse input.json
    while state["PC"] < len(instructions):
        decoded = fetch_and_decode(state, instructions)

        if DIR:
            rename_and_dispatch(state, DIR)
            DIR = []

        DIR.extend(decoded)

        

        # trace changes its "PC" and "DecodedPCs"
        trace.append(copy.deepcopy(state))

    # Write output
    with open(output, "w") as f:
        json.dump(trace, f, indent=2)

if __name__ == "__main__":
    main()

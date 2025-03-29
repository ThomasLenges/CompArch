import sys
import json
import copy

from pipeline.pipeline import pipeline
from exception_handling.exception_handler import exception_handler

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

    # Go through pipeline
    pipeline(state, instructions, trace)

    # Exception handling 
    if(state["Exception"]):
        exception_handler(state, trace)
        
    # End of simulation
    if(state["Exception"]):
        state["Exception"] = False
        trace.append(copy.deepcopy(state))
    print("end of simulation")

    # Write output
    with open(output, "w") as f:
        json.dump(trace, f, indent=2)

if __name__ == "__main__":
    main()

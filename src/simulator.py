import sys
import json
import copy

from pipeline import fetch_and_decode
from pipeline import rename_and_dispatch
from pipeline import issue
from pipeline import execute
from pipeline import commit

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
    ExecuteBuffer = [[],[]] # From issue → execute

    counter = 0

    # Parse input.json
    while (
        state["PC"] < len(instructions)
        or state["ActiveList"] 
    ):
        # === Stage 5: Commit
        exception = commit(state)
        if exception:
            break

        # === Stage 3 & 4: Execute
        execute(state, ExecuteBuffer[1])
        ExecuteBuffer.pop()  # shift pipeline
        ExecuteBuffer.insert(0, []) # make room for next exec0


        # === Stage 2: Issue
        issued = issue(state)
        ExecuteBuffer[0].extend(issued)



        # === Stage 1: Rename & Dispacth
        rename_and_dispatch(state, DIR)
        DIR = [] # consumed

        # === Stage 0: Fetch & Decode 
        decoded = fetch_and_decode(state, instructions)
        DIR.extend(decoded)

        # add new cycle to ouput
        trace.append(copy.deepcopy(state))

        print(f"Cycle: {counter}")
        counter += 1
    
    # === Exception handling 
    while (state["ActiveList"]):
        print("Handling exception")

        state["IntegerQueue"].clear()

        # add new cycle to output
        trace.append(copy.deepcopy(state))

        for _ in range(4):
            entry = state["ActiveList"].pop()

            old_dest = entry["OldDestination"]
            state["FreeList"].append(old_dest)
        

    # === End of exception handling
    print("End of sim")

    trace.append(copy.deepcopy(state))

    state["Exception"] = False

    trace.append(copy.deepcopy(state))


    # Write output
    with open(output, "w") as f:
        json.dump(trace, f, indent=2)

if __name__ == "__main__":
    main()

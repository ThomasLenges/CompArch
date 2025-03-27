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
        or any(ExecuteBuffer) 
    ):
        # === Stage 5: Commit
        commit(state)

        # === Stage 3 & 4: Execute
        execute(state, ExecuteBuffer[1])
        ExecuteBuffer.pop()  # shift pipeline
        ExecuteBuffer.insert(0, []) # make room for next exec0

        for inst in ExecuteBuffer[1]:
            print(f"[Cycle {counter}] ⚙️  Executed: PC={inst['PC']}, Dest=P{inst['DestRegister']}, Op={inst['OpCode']}")

        # === Stage 2: Issue
        issued = issue(state)
        ExecuteBuffer[0].extend(issued)

        for inst in issued:
            print(f"[Cycle {counter}] 🔁 Issued: PC={inst['PC']}, Dest=P{inst['DestRegister']}, Op={inst['OpCode']}")


        # === Stage 1: Rename & Dispacth
        rename_and_dispatch(state, DIR)
        DIR = [] # consumed

        # === Stage 0: Fetch & Decode 
        decoded = fetch_and_decode(state, instructions)
        DIR.extend(decoded)

        # trace changes its "PC" and "DecodedPCs"
        trace.append(copy.deepcopy(state))

        print(f"Cycle: {counter}")
        counter += 1


    # Write output
    with open(output, "w") as f:
        json.dump(trace, f, indent=2)

if __name__ == "__main__":
    main()

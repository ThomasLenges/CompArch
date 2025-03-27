from isa import parse_instruction

def fetch_and_decode(state, instructions):
    """
    Simulates stage 0 of the pipeline
    Fethes and decodes up to 4 instructions 
    Updates:
    - PC
    - DecodedPCs
    """
    decoded_instructions = []
    decoded_pcs = []

    for i in range(4):  # Fetch up to 4 instructions
        instr_index = state["PC"] + i

        if instr_index >= len(instructions):
            break  # no more instructions to fetch

        inst_str = instructions[instr_index]
        inst = parse_instruction(inst_str)

        # (f"[Cycle] FETCH @PC={instr_index}: {inst_str}")
        # print(f"[Cycle] DECODE → Parsed: {inst}")

        # Keep the PC for the active list
        inst["PC"] = instr_index

        decoded_instructions.append(inst)
        decoded_pcs.append(instr_index)

    # Update state
    state["DecodedPCs"] = decoded_pcs
    state["PC"] += len(decoded_instructions)  # advance PC by # of fetched instructions

    return decoded_instructions

def rename_and_dispatch(state, decoded_instructions):
    """
    Simulates stage 1 of the pipeline
    Renames and dispatches up to 4 instructions.
    Updates:
    - ActiveList
    - BusyBitTable (BBT)
    - FreeList
    - IntegerQueue
    - RegisterMapTable (RMT)
    """

    for inst in decoded_instructions:
        opcode = inst["opcode"]
        rd = inst["rd"]
        rs1 = inst["rs1"]
        rs2 = inst.get("rs2") # Fail-safe for instruction without opB (gets None)
        imm = inst.get("imm") # Fail-safe for instruction without imm (gets None)
        pc = inst["PC"]

        # Fetch source operand physical registers 
        physical_rs1 = state["RegisterMapTable"][rs1]
        physical_rs2 = state["RegisterMapTable"][rs2] if rs2 is not None else None # Fail-safe for instruction without opB (gets None) 

        # Verify readiness and get source operand value
        opA_ready = True
        opA_ready = not state["BusyBitTable"][physical_rs1]

        opA_value = state["PhysicalRegisterFile"][physical_rs1]

        if imm is not None:
            opB_ready = True
            opB_value = imm
        else:
            opB_ready = not state["BusyBitTable"][physical_rs2]
            opB_value = state["PhysicalRegisterFile"][physical_rs2]

        # Allocate a new physical register for destination register
        if not state["FreeList"]:
            print("FreeList is empty! Stalling.")
            continue  # Could stall here, for now we skip

        physical_rd = state["FreeList"].pop(0)
        old_dest = state["RegisterMapTable"][rd] # For active list
        state["RegisterMapTable"][rd] = physical_rd # Update RMT after saving old value
        state["BusyBitTable"][physical_rd] = True # Update BBT for newly used physical register

        # Update Active List
        active_entry = {
            "Done": False,
            "Exception": False,
            "LogicalDestination": rd,
            "OldDestination": old_dest,
            "PC": pc
        }
        state["ActiveList"].append(active_entry)

        # Update Integer Queue
        iq_entry = {
            "DestRegister": physical_rd,
            "OpAIsReady": opA_ready,
            "OpARegTag": physical_rs1 if not opA_ready else 0,
            "OpAValue": opA_value if opA_ready else 0,
            "OpBIsReady": opB_ready,
            "OpBRegTag": physical_rs2 if (imm is None or not opB_ready) else 0,
            "OpBValue": opB_value if opB_ready else 0,
            "OpCode": opcode,
            "PC": pc
        }
 
        state["IntegerQueue"].append(iq_entry)

        # print(f"[Cycle] RENAMED: {opcode} → P{physical_rd} | rs1 → P{physical_rs1} ({opA_ready}), rs2 → P{physical_rs2} ({opB_ready})")

def issue(state): # Need to add forwarding paths!
    """
    Simulates stage 2 of the pipeline
    Issues up to 4 instrucationsfrom the Integer Queue.
    Updates:
    - IntegerQueue
    """
    ready_to_issue = []

    new_queue = []

    for entry in state["IntegerQueue"]:
        if entry["OpAIsReady"] and entry["OpBIsReady"] and len(ready_to_issue) < 4:
            ready_to_issue.append(entry)
            # print(f"[Cycle] ISSUED: {entry['OpCode']} @PC={entry['PC']}")
        else:
            new_queue.append(entry)

    # Update Integer Queue with unissued instructions only
    state["IntegerQueue"] = new_queue

    return ready_to_issue


def execute(state, issued_instructions):
    """
    Simulates stage 3 & 4 of the pipeline
    Executes up to 4 instructions.

    Updates:
    - ActiveList
    - BusyBitTable
    - PhysicalRegisterFile
    - IntegerQueue
    """
    executed = []

    for inst in issued_instructions[:4]:  # Limit to 4 executions per cycle
        op = inst["OpCode"]
        a = inst.get("OpAValue")
        b = inst.get("OpBValue")
        dest = inst["DestRegister"]
        pc = inst["PC"]

        exception = False

        # Basic ALU
        if op == "add":
            result = a + b
        elif op == "sub":
            result = a - b
        elif op == "mul":
            result = a * b
        elif op == "divu":
            if b == 0:
                result = 0
                exception = True
            else:
                result = a // b
        elif op == "remu":
            if b == 0:
                result = 0
                exception = True
            else:
                result = a % b

        for entry in state["ActiveList"]:
            if entry["PC"] == pc:
                entry["Done"] = True
                if exception:
                    entry["Exception"] = True
                break
        
        state["BusyBitTable"][dest] = False
        state["PhysicalRegisterFile"][dest] = result

        # Forwarding path
        for iq_entry in state["IntegerQueue"]:
            if (not iq_entry["OpAIsReady"]) and iq_entry["OpARegTag"] == dest:
                iq_entry["OpAIsReady"] = True
                iq_entry["OpAValue"] = result
                iq_entry["OpARegTag"] = 0
            if (not iq_entry["OpBIsReady"]) and iq_entry["OpBRegTag"] == dest:
                iq_entry["OpBIsReady"] = True
                iq_entry["OpBValue"] = result
                iq_entry["OpBRegTag"] = 0

 

def commit(state):
    """
    Simulates stage 5 of the pipeline
    Commits instructions in order from the ActiveList.

    Updates:
    ActiveList
    FreeList
    """

    while state["ActiveList"]:
        entry = state["ActiveList"][0]

        # Handle exception
        if entry["Exception"]:
            print(f"[Commit] 🚨 Exception at PC={entry['PC']} → Jumping to 0x10000")
            state["ExceptionPC"] = entry["PC"]
            state["PC"] = 65536
            state["Exception"] = True
            break

        # Handle commit
        if entry["Done"]:
            state["ActiveList"].pop(0)
            old_dest = entry["OldDestination"]
            state["FreeList"].append(old_dest)
        else:
            break


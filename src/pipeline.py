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

        print(f"[Cycle] FETCH @PC={instr_index}: {inst_str}")
        print(f"[Cycle] DECODE → Parsed: {inst}")

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
            "OpARegTag": physical_rs1,
            "OpAValue": opA_value if opA_ready else 0,
            "OpBIsReady": opB_ready,
            "OpBRegTag": physical_rs2 if imm is None else 0,
            "OpBValue": opB_value if opB_ready else 0,
            "OpCode": opcode,
            "PC": pc
        }
 
        state["IntegerQueue"].append(iq_entry)

        print(f"[Cycle] RENAMED: {opcode} → P{physical_rd} | rs1 → P{physical_rs1} ({opA_ready}), rs2 → P{physical_rs2} ({opB_ready})")

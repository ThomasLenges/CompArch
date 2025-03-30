def rename_and_dispatch(state, decoded_instructions):
    """
    Simulates stage 1 of the pipeline
    Renames and dispatches up to 4 instructions.
    Checks for availability to rename_and_dispatch and if need be apply backpressure
    Updates:
    - ActiveList
    - BusyBitTable (BBT)
    - FreeList
    - IntegerQueue
    - RegisterMapTable (RMT)
    """

    leftovers = []

    for inst in decoded_instructions:
        if (
            len(state["ActiveList"]) >= 32
            or len(state["FreeList"]) == 0
            or len(state["IntegerQueue"]) >= 32
        ):
            leftovers.append(inst)
            continue

    
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

    return leftovers
       
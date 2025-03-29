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

        # Keep the PC for the active list
        inst["PC"] = instr_index

        decoded_instructions.append(inst)
        decoded_pcs.append(instr_index)

    # Update state
    state["DecodedPCs"] = decoded_pcs
    state["PC"] += len(decoded_instructions)  # advance PC by # of fetched instructions

    return decoded_instructions

def parse_instruction(inst_str):
    """
    Parses assembly instructions and returns dictionnary
    """
    
    parts = inst_str.replace(",", "").split()
    opcode = parts[0]

    if opcode == "add":
        return {
            "opcode": "add",
            "rd": int(parts[1][1:]),
            "rs1": int(parts[2][1:]),
            "rs2": int(parts[3][1:])
        }

    elif opcode == "addi":
        return {
            "opcode": "add", # When looking at tests. OpCode for addi is "add"
            "rd": int(parts[1][1:]),
            "rs1": int(parts[2][1:]),
            "imm": int(parts[3])
        }

    elif opcode == "sub":
        return {
            "opcode": "sub",
            "rd": int(parts[1][1:]),
            "rs1": int(parts[2][1:]),
            "rs2": int(parts[3][1:])
        }

    elif opcode == "mulu":
        return {
            "opcode": "mulu",
            "rd": int(parts[1][1:]),
            "rs1": int(parts[2][1:]),
            "rs2": int(parts[3][1:])
        }

    elif opcode == "divu":
        return {
            "opcode": "divu",
            "rd": int(parts[1][1:]),
            "rs1": int(parts[2][1:]),
            "rs2": int(parts[3][1:])
        }

    elif opcode == "remu":
        return {
            "opcode": "remu",
            "rd": int(parts[1][1:]),
            "rs1": int(parts[2][1:]),
            "rs2": int(parts[3][1:])
        }

    else:
        raise ValueError(f"Unknown instruction : {inst_str}")

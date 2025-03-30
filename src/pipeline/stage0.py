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
            "rd": validate_register(parts[1]),
            "rs1": validate_register(parts[2]),
            "rs2": validate_register(parts[3])
        }

    elif opcode == "addi":
        return {
            "opcode": "add",  # still using 'add' for addi
            "rd": validate_register(parts[1]),
            "rs1": validate_register(parts[2]),
            "imm": validate_immediate(parts[3])
        }

    elif opcode == "sub":
        return {
            "opcode": "sub",
            "rd": validate_register(parts[1]),
            "rs1": validate_register(parts[2]),
            "rs2": validate_register(parts[3])
        }

    elif opcode == "mulu":
        return {
            "opcode": "mulu",
            "rd": validate_register(parts[1]),
            "rs1": validate_register(parts[2]),
            "rs2": validate_register(parts[3])
        }

    elif opcode == "divu":
        return {
            "opcode": "divu",
            "rd": validate_register(parts[1]),
            "rs1": validate_register(parts[2]),
            "rs2": validate_register(parts[3])
        }

    elif opcode == "remu":
        return {
            "opcode": "remu",
            "rd": validate_register(parts[1]),
            "rs1": validate_register(parts[2]),
            "rs2": validate_register(parts[3])
        }

    else:
        raise ValueError(f"Unknown instruction : {inst_str}")

def validate_register(reg_str):
    if not reg_str.startswith('x') or not reg_str[1:].isdigit():
        raise ValueError(f"Invalid register name: {reg_str}")
    
    reg_num = int(reg_str[1:])
    if not (0 <= reg_num <= 31):
        raise ValueError(f"Register out of bounds: {reg_str}")

    return reg_num

def validate_immediate(imm_str):
    try:
        imm = int(imm_str)
    except ValueError:
        raise ValueError(f"Invalid immediate value: {imm_str}")

    if not (-2**63 <= imm <= 2**63 - 1):
        raise ValueError(f"Immediate out of signed 64-bit range: {imm}")


    return imm

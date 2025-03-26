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

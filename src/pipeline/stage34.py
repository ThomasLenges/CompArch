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

    for inst in issued_instructions:  
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
        elif op == "mulu":
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
        
        if not exception:
            state["BusyBitTable"][dest] = False

        result = u64(result)
        state["PhysicalRegisterFile"][dest] = result

        # Forwarding path
        for iq_entry in state["IntegerQueue"]:
            if (not iq_entry["OpAIsReady"]) and iq_entry["OpARegTag"] == dest and not exception:
                iq_entry["OpAIsReady"] = True
                iq_entry["OpAValue"] = result
                iq_entry["OpARegTag"] = 0
            if (not iq_entry["OpBIsReady"]) and iq_entry["OpBRegTag"] == dest and not exception:
                iq_entry["OpBIsReady"] = True
                iq_entry["OpBValue"] = result
                iq_entry["OpBRegTag"] = 0 

def u64(val):
    return val & 0xFFFFFFFFFFFFFFFF

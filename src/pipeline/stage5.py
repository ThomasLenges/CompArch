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
            return True

        # Handle commit
        if entry["Done"]:
            state["ActiveList"].pop(0)
            old_dest = entry["OldDestination"]
            state["FreeList"].append(old_dest)
        else:
            break
    return False 

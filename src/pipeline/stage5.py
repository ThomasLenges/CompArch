def commit(state):
    """
    Simulates stage 5 of the pipeline
    Commits up to 4 instructions in order from the ActiveList.

    Updates:
    ActiveList
    FreeList
    """

    committed = 0
    max_commit = 4

    while state["ActiveList"] and committed < max_commit:
        entry = state["ActiveList"][0]

        # Handle exception
        if entry["Exception"]:
            print(f"[Commit] Exception at PC={entry['PC']} → Jumping to 0x10000")
            state["ExceptionPC"] = entry["PC"]
            state["PC"] = 65536
            state["Exception"] = True
            return True

        # Handle commit
        if entry["Done"]:
            state["ActiveList"].pop(0)
            old_dest = entry["OldDestination"]
            state["FreeList"].append(old_dest)
            committed += 1
        else:
            break
    return False 

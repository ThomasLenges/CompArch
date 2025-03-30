import copy

def exception_handler(state, trace):
    while (state["ActiveList"]):
        print("Handling exception")
        
        state["IntegerQueue"].clear()

        # add new cycle to output
        trace.append(copy.deepcopy(state))

        last_entries = list(reversed(state["ActiveList"][-4:]))
    
        # clear active list and restore BBT and RMT
        for entry in last_entries:

            log_reg = entry["LogicalDestination"]
            phys_dest = entry["OldDestination"]

            old_mapping = state["RegisterMapTable"][log_reg]
            if old_mapping is not None:
                    state["FreeList"].append(old_mapping)
                    state["BusyBitTable"][old_mapping] = False
            state["RegisterMapTable"][log_reg] = phys_dest

        del state["ActiveList"][-4:]
    
    trace.append(copy.deepcopy(state))
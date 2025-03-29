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

 

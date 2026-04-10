from typing import TypedDict, List
from langgraph.graph import StateGraph
from datetime import datetime


# ---------- STATE ---------- #
class AgentState(TypedDict):
    query: str
    medications: List[dict]
    response: str


# ---------- INTENT DETECTION ---------- #
def detect_intent(query):

    query = query.lower()

    if any(word in query for word in ["adherence", "progress", "percentage"]):
        return "adherence"

    if any(word in query for word in ["miss", "pending", "left", "remaining"]):
        return "pending"

    if any(word in query for word in ["taken", "completed"]):
        return "taken"

    if any(word in query for word in ["highest", "best", "most"]):
        return "best_med"

    if any(word in query for word in ["all", "complete", "done"]):
        return "completion"

    return "unknown"


# ---------- CORE LOGIC ---------- #
def process_agent(state: AgentState):

    query = state["query"].lower()
    intent = detect_intent(query)

    meds = state["medications"]
    today = datetime.now().strftime("%Y-%m-%d")

    pending_map = {}
    taken_map = {}

    total_doses = 0
    total_taken = 0

    for med in meds:
        name = med.get("name", "").strip()

        for dose in med.get("schedule", []):

            total_doses += 1

            is_taken = (
                dose.get("taken", False)
                and dose.get("last_taken_date") == today
            )

            if is_taken:
                total_taken += 1
                taken_map[name] = taken_map.get(name, 0) + 1
            else:
                pending_map[name] = pending_map.get(name, 0) + 1

    # ---------- SPECIFIC MED ---------- #
    for med in meds:
        name = med.get("name", "")
        if name.lower() in query:
            pending = pending_map.get(name, 0)
            taken = taken_map.get(name, 0)
            state["response"] = f"{name}: {taken} taken, {pending} pending"
            return state

    # ---------- BEST MEDICINE ---------- #
    if intent == "best_med":

        best_med = None
        best_ratio = -1

        for med in meds:
            name = med.get("name", "")
            schedule = med.get("schedule", [])

            total = len(schedule)
            taken = 0

            for dose in schedule:
                if dose.get("taken") and dose.get("last_taken_date") == today:
                    taken += 1

            if total > 0:
                ratio = taken / total
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_med = name

        if best_med:
            percent = round(best_ratio * 100, 2)
            state["response"] = f"🏆 {best_med} has highest adherence ({percent}%)"
        else:
            state["response"] = "No data available"

        return state

    # ---------- ADHERENCE ---------- #
    if intent == "adherence":
        if total_doses == 0:
            state["response"] = "No data available"
        else:
            percent = round((total_taken / total_doses) * 100, 2)
            state["response"] = f"📊 Adherence: {percent}% ({total_taken}/{total_doses})"
        return state

    # ---------- PENDING ---------- #
    if intent == "pending":
        if not pending_map:
            state["response"] = "✅ No pending medications"
        else:
            msg = "⚠️ Pending:\n"
            for name, count in pending_map.items():
                msg += f"- {name} → {count}\n"
            state["response"] = msg
        return state

    # ---------- TAKEN ---------- #
    if intent == "taken":
        if not taken_map:
            state["response"] = "❌ Nothing taken yet"
        else:
            msg = "✅ Taken:\n"
            for name, count in taken_map.items():
                msg += f"- {name} → {count}\n"
            state["response"] = msg
        return state

    # ---------- COMPLETION ---------- #
    if intent == "completion":
        if total_doses == total_taken:
            state["response"] = "🎉 All medications taken today"
        else:
            remaining = total_doses - total_taken
            state["response"] = f"⚠️ {remaining} doses still pending"
        return state

    # ---------- DEFAULT ---------- #
    state["response"] = "🤖 Ask about adherence, pending, taken, or best medicine"
    return state


# ---------- GRAPH ---------- #
def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("process", process_agent)

    graph.set_entry_point("process")
    graph.set_finish_point("process")

    return graph.compile()


agent = build_agent()
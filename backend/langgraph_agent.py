from typing import TypedDict, List
from langgraph.graph import StateGraph
from datetime import datetime
from rapidfuzz import fuzz


# ---------- STATE ---------- #
class AgentState(TypedDict):
    query: str
    medications: List[dict]
    response: str
    user_id: str  # for memory


# ---------- MEMORY STORE ---------- #
memory_store = {}

# ---------- INTENT DETECTION ---------- #
from rapidfuzz import fuzz


def fuzzy_match(query, keywords, threshold=70):
    for word in keywords:
        if fuzz.partial_ratio(query, word) >= threshold:
            return True
    return False


def detect_intent(query):

    query = query.lower()

    if fuzzy_match(query, ["adherence", "progress", "percentage"]):
        return "adherence"

    if fuzzy_match(query, ["miss", "pending", "left", "remaining"]):
        return "pending"

    if fuzzy_match(query, ["taken", "completed"]):
        return "taken"

    if fuzzy_match(query, ["highest", "best", "most"]):
        return "best_med"

    if fuzzy_match(query, ["all", "complete", "done"]):
        return "completion"

    return "unknown"

# ---------- CORE LOGIC ---------- #
def process_agent(state: AgentState):

    query = state["query"].lower()
    intent = detect_intent(query)

    meds = state["medications"]
    today = datetime.now().strftime("%Y-%m-%d")

    # ---------- MEMORY INIT ---------- #
    user_id = state.get("user_id", "default")

    if user_id not in memory_store:
        memory_store[user_id] = []

    history = memory_store[user_id]

    # ---------- DATA PROCESS ---------- #
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

    # ---------- CONTEXT FOLLOW-UP ---------- #
    if query in ["which one", "which", "what ones", "tell me"] and history:
        last = history[-1]["response"]

        if "Pending" in last:
            state["response"] = last
            return state

    # ---------- SPECIFIC MED ---------- #
    for med in meds:
        name = med.get("name", "")
        if fuzz.partial_ratio(name.lower(), query) > 70:
            pending = pending_map.get(name, 0)
            taken = taken_map.get(name, 0)
            state["response"] = f"{name}: {taken} taken, {pending} pending"

            history.append({"query": query, "response": state["response"]})
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

        history.append({"query": query, "response": state["response"]})
        return state

    # ---------- ADHERENCE ---------- #
    if intent == "adherence":
        if total_doses == 0:
            state["response"] = "No data available"
        else:
            percent = round((total_taken / total_doses) * 100, 2)
            state["response"] = f"📊 Adherence: {percent}% ({total_taken}/{total_doses})"

        history.append({"query": query, "response": state["response"]})
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

        history.append({"query": query, "response": state["response"]})
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

        history.append({"query": query, "response": state["response"]})
        return state

    # ---------- COMPLETION ---------- #
    if intent == "completion":
        if total_doses == total_taken:
            state["response"] = "🎉 All medications taken today"
        else:
            remaining = total_doses - total_taken
            state["response"] = f"⚠️ {remaining} doses still pending"

        history.append({"query": query, "response": state["response"]})
        return state

    # ---------- DEFAULT ---------- #
    state["response"] = "🤖 Ask about adherence, pending, taken, or best medicine"

    history.append({"query": query, "response": state["response"]})
    return state


# ---------- GRAPH ---------- #
def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("process", process_agent)

    graph.set_entry_point("process")
    graph.set_finish_point("process")

    return graph.compile()


agent = build_agent()
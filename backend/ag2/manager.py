"""
ag2/manager.py — Raw DB data return, no response_agent formatting
"""
import autogen
import threading
import time
from ag2.agents import (
    make_triage_agent, make_clarification_agent,
    make_sql_agent, llm_config,
)
from ag2.tools import find_company, get_quarters, get_sectors, run_query, get_schema_info


def run_stock_query(user_message: str, human_input_mode: str = "NEVER") -> dict:

    triage_agent        = make_triage_agent()
    clarification_agent = make_clarification_agent()
    sql_agent           = make_sql_agent()

    user_proxy = autogen.UserProxyAgent(
        name="user",
        human_input_mode=human_input_mode,
        max_consecutive_auto_reply=10,
        code_execution_config=False,
    )

    _raw_result = {"data": None, "sql": None}
    _result_lock = threading.Lock()

    def intercepted_run_query(sql: str):
        result = run_query(sql)
        with _result_lock:
            _raw_result["data"] = result
            _raw_result["sql"] = sql
        print(f"[CAPTURED] {len(result)} rows captured!")
        return result

    autogen.register_function(find_company,
        caller=triage_agent, executor=user_proxy,
        name="find_company", description="Fuzzy match company name from DB.")
    autogen.register_function(get_quarters,
        caller=triage_agent, executor=user_proxy,
        name="get_quarters", description="Get all available quarters.")
    autogen.register_function(get_sectors,
        caller=triage_agent, executor=user_proxy,
        name="get_sectors", description="Get all available sectors.")
    autogen.register_function(intercepted_run_query,
        caller=sql_agent, executor=user_proxy,
        name="run_query", description="Run a PostgreSQL SQL query.")
    autogen.register_function(get_schema_info,
        caller=sql_agent, executor=user_proxy,
        name="get_schema_info", description="Get DB schema info.")

    def speaker_selection_fn(last_speaker, groupchat):
        messages = groupchat.messages
        if not messages:
            return triage_agent

        last_msg    = (messages[-1].get("content") or "").strip()
        sender_name = last_speaker.name if last_speaker else ""
        last_full   = messages[-1]

        if "ROUTE_TO_SQL" in last_msg:
            return sql_agent
        if "ROUTE_TO_CLARIFICATION" in last_msg:
            return clarification_agent
        if "ROUTE_TO_RESPONSE" in last_msg:
            return None

        if last_full.get("tool_calls"):
            return user_proxy

        if sender_name == "user" and last_full.get("role") == "tool":
            for msg in reversed(messages[:-1]):
                n = msg.get("name", "")
                if n == "triage_agent":
                    return triage_agent
                if n == "sql_agent":
                    return sql_agent
            return triage_agent

        if sender_name == "user":
            for msg in reversed(messages[:-1]):
                n = msg.get("name", "")
                if n in ("triage_agent", "sql_agent"):
                    return triage_agent if n == "triage_agent" else sql_agent
            return triage_agent

        if sender_name == "sql_agent":
            return None

        if sender_name == "clarification_agent":
            return None

        return triage_agent

    groupchat = autogen.GroupChat(
        agents=[user_proxy, triage_agent, clarification_agent, sql_agent],
        messages=[],
        max_round=25,
        speaker_selection_method=speaker_selection_fn,
    )

    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
    )

    ag2_done = threading.Event()

    def run_ag2():
        try:
            user_proxy.initiate_chat(manager, message=user_message, clear_history=True)
        except Exception as e:
            print(f"[AG2 Error] {e}")
        finally:
            ag2_done.set()

    ag2_thread = threading.Thread(target=run_ag2, daemon=True)
    ag2_thread.start()

    def get_raw():
        with _result_lock:
            return _raw_result["data"], _raw_result["sql"]

    def check_messages():
        msgs = groupchat.messages

        data, sql = get_raw()
        if data is not None:
            return {"status": "answer", "data": data, "sql": sql}

        # 2. Clarification needed - clarification_agent se
        for msg in reversed(msgs):
            name    = msg.get("name", "")
            content = (msg.get("content") or "").strip()
            if name == "clarification_agent" and content:
                return {"status": "clarification_needed", "question": content}

        # 3. Triage ka ROUTE_TO_CLARIFICATION
        for msg in reversed(msgs):
            name    = msg.get("name", "")
            content = (msg.get("content") or "").strip()
            if name == "triage_agent" and "ROUTE_TO_CLARIFICATION:" in content:
                question = content.split("ROUTE_TO_CLARIFICATION:")[-1].strip()
                if question:
                    return {"status": "clarification_needed", "question": question}

        # 4. Out of scope
        for msg in reversed(msgs):
            name    = msg.get("name", "")
            content = (msg.get("content") or "").strip()
            if name == "triage_agent" and "ROUTE_TO_RESPONSE:" in content:
                message = content.split("ROUTE_TO_RESPONSE:")[-1].strip()
                return {"status": "out_of_scope", "data": [], "message": message}

        return None

    start = time.time()
    while time.time() - start < 60:
        time.sleep(0.1)

        data, sql = get_raw()
        if data is not None:
            print(f"[FAST] Answer in {time.time()-start:.1f}s")
            return {"status": "answer", "data": data, "sql": sql}

        result = check_messages()
        if result:
            print(f"[FAST] Answer in {time.time()-start:.1f}s")
            return result

        if ag2_done.is_set():
            # Extra 1 second wait — intercepted_run_query finish hone do
            for _ in range(10):
                time.sleep(0.1)
                data, sql = get_raw()
                if data is not None:
                    print(f"[DONE+WAIT] Answer found!")
                    return {"status": "answer", "data": data, "sql": sql}
            result = check_messages()
            if result:
                return result
            break

    return {"status": "error", "data": [], "message": "Kuch problem aayi. Please try again."}


if __name__ == "__main__":
    print("\n=== Stock Market Assistant ===\n'exit' type karo\n")
    ctx = ""
    while True:
        q = input("Aap: ").strip()
        if q.lower() in ("exit", "quit"):
            break
        if not q:
            continue
        full_q = f"{ctx} {q}".strip() if ctx else q
        t = time.time()
        result = run_stock_query(full_q)
        print(f"Time: {time.time()-t:.1f}s | Result: {result}")
        if result["status"] == "clarification_needed":
            print(f"\n {result['question']}\n")
            ctx = full_q
        else:
            print(f"\n {result}\n")
            ctx = ""
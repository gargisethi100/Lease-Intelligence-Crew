"""Streamlit demo UI for the Lease Intelligence Crew.

Run:  .venv/Scripts/streamlit run app.py

Approval state is read from the graph's persisted checkpoint (not memory), so
it survives Streamlit's rerun-on-every-click model.
"""

import sqlite3

import streamlit as st
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from lease_crew.graph import build_graph

st.set_page_config(page_title="Lease Intelligence Crew", page_icon="🏢")


@st.cache_resource
def get_graph():
    # check_same_thread=False so Streamlit's rerun threads can share the connection.
    conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
    return build_graph(SqliteSaver(conn))


graph = get_graph()

if "session_n" not in st.session_state:
    st.session_state.session_n = 0
config = {"configurable": {"thread_id": f"ui-{st.session_state.session_n}"}}

st.title("🏢 Lease Intelligence Crew")
st.caption("Multi-agent lease assistant: RAG, market research, and a human-approved analyst.")

with st.sidebar:
    st.subheader("The crew")
    st.markdown(
        "- **Lease Expert** - grounded RAG over lease PDFs\n"
        "- **Market Researcher** - live web search (Tavily)\n"
        "- **Analyst** - writes Python, runs it *after your approval*"
    )
    if st.button("New conversation"):
        st.session_state.session_n += 1
        st.rerun()

snapshot = graph.get_state(config)

# Render the conversation so far (from the checkpointer).
for msg in snapshot.values.get("messages", []):
    if msg.type in ("human", "ai") and msg.content:
        with st.chat_message("user" if msg.type == "human" else "assistant"):
            st.markdown(msg.content)

# Is the Analyst paused, waiting for approval?
pending = next((t.interrupts[0].value for t in snapshot.tasks if t.interrupts), None)

if pending:
    st.warning("The Analyst wants to run this code. Approve to continue:")
    st.code(pending.get("code", ""), language="python")
    left, right = st.columns(2)
    if left.button("Approve", use_container_width=True):
        with st.spinner("Running..."):
            graph.invoke(Command(resume="yes"), config)
        st.rerun()
    if right.button("Reject", use_container_width=True):
        graph.invoke(Command(resume="no"), config)
        st.rerun()
elif prompt := st.chat_input("Ask about your leases, the market, or rent math..."):
    with st.spinner("The crew is working..."):
        graph.invoke({"messages": [{"role": "user", "content": prompt}]}, config)
    st.rerun()

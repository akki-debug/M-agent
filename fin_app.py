import os
import streamlit as st
import sys
from datetime import datetime
from crewai import Crew, Process
from fin_agents import FinAgents, StreamToExpander
from fin_tasks import FinTasks
from template.fin_template import fin_template

# Fix ChromaDB SQLite issue by forcing DuckDB
os.environ["CHROMA_DB_IMPL"] = "duckdb"

st.set_page_config(page_icon="📝", page_title="ZeeFinReporter", layout="wide")

# Class TravelCrew
class TravelCrew:
    def __init__(self, ticker):
        self.ticker = ticker
        self.output_placeholder = st.empty()

    def run(self):
        agents = FinAgents()
        tasks = FinTasks()

        fin_agent = agents.fin_agent()
        news_agent = agents.news_agent()
        reporter_agent = agents.reporter_agent()

        fin_task = tasks.fin_task(fin_agent, self.ticker)
        news_task = tasks.news_task(news_agent, self.ticker)
        reporter_task = tasks.reporter_task(
            [fin_task, news_task],
            reporter_agent,
            self.ticker,
        )

        crew = Crew(
            agents=[fin_agent, news_agent, reporter_agent],
            tasks=[fin_task, news_task, reporter_task],
            process=Process.sequential,
            full_output=True,
            share_crew=False,
            verbose=True
        )

        result = crew.kickoff()
        self.output_placeholder.markdown(result)

        return result


st.header("🏛️ Financial Reporter :orange[Ai]gent 📊", divider="orange")

# Sidebar
with st.sidebar:
    st.caption("Financial Agent")
    st.markdown(
        """
        # 🏛️ Financial Reporter 📈
            1. Pick your stock ticker
            2. Click generate report
            3. View detailed analysis
        """
    )
    st.divider()
    st.caption("Created by @0xZee")

st.session_state.plan_pressed = False

# User Inputs
ticker = st.text_input("📈 Enter Stock Ticker:", placeholder="AAPL, TSLA...")

if ticker:
    st.caption("👌 Generating your Financial Report:")
    st.write(f":sparkles: 🎫 Financial Report for: {ticker} 📈")

    if st.button("💫 Generate Report", use_container_width=True, key="plan"):
        with st.spinner(text="🤖 Agents working on the report 🔍 ..."):
            with st.status("🤖 **Processing...**", state="running", expanded=True) as status:
                with st.container(height=300, border=False):
                    sys.stdout = StreamToExpander(st)
                    travel_crew = TravelCrew(ticker)
                    result = travel_crew.run()
                status.update(label="✅ Financial Report Ready! 📊", state="complete", expanded=False)

        st.subheader(f"📊 {ticker} Financial Report 📰", anchor=False, divider="rainbow")
        st.markdown(result["final_output"])
        st.divider()

        # Display usage metrics
        st.json(result['usage_metrics'])
        st.divider()

        # Expander for detailed task outputs
        for i, task in enumerate(result['tasks_outputs']):
            with st.expander(f"Agent Report {i+1}:", expanded=False):
                st.markdown(task)
        st.divider()











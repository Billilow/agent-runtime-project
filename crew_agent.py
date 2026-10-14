from dotenv import load_dotenv

from crewai import Agent, LLM, Task, Crew, Process, TaskOutput
from crew_tools import calculator_tool, crypto_price_tool, websearch_tool, CALCULATOR_CALLS

load_dotenv()

def required_calculator_use(output: TaskOutput):
    if not CALCULATOR_CALLS:
        return (False, "You did not call the Calculator tool. Call it for every numeric comparison, then rewrite the analysis using only the values it returned.")
    return (True, output)

llm = LLM(model="gemini/gemini-3.1-flash-lite")

researcher = Agent(
    role="Crypto Market Researcher",       # Role of this agent
    goal="Collect accurate, up-to-date price data and news about a given cryptocurrency",       # goals the agent should achieve
    backstory="You are a high-speed crypto investigative journalist and news archivist. Your primary focus is capturing breaking news, regulatory changes, protocol upgrades, and macroeconomic shifts impacting the crypto market. You cross-check multiple authoritative web sources, prioritize the absolute newest information, and explicitly flag the timestamp or source reliability of each piece of data.",  # 배경 설정 (역할에 맞게 행동하도록 유도하는 설명)
    tools=[crypto_price_tool, websearch_tool],      # tools that the agent could use
    llm=llm,
    verbose=True
)

research_task = Task(
    description="Use the Crypto_Price tool for the current price and the Web_Search tool for recent news about {topic}. I want you to only research about the facts. The current price of the crypto, contents of the news, sources (URLs), and the absolute dates. No opinions nor analytical thinking. Convey only the written truths. If there is an unknown fact that you could not find, do not guess, just say not available. For the date, copy the time text exactly as it appears in the source (e.g. \"about 2 hours ago\" or \"Sep 25, 2026\"). Never convert it into a calendar date yourself. If no time is shown, write \"not available\".",      # 구체적인 작업. {topic}처럼 변수를 넣을 수 있어요
    expected_output="I want you to clearly state the current crypto price first at the top. "
                    "And the organized results should be organized as in the numbered list order. Expecting up to 3 results."
                    " e.g.) 1. [headline or short summary] — Source: [URL] — Date: [time text as shown in the source, or \"not available\"]",  # 결과물이 어떤 형태여야 하는지
    agent=researcher
)

analyst = Agent(
    role="Crypto Market Analyst",
    goal="Turn the researcher's facts into a clear, evidence-based analysis and flag claims with weak support.",
    backstory="""You are a meticulous analyst with a keen eye for detail. 
    You have a proven track record of turning complex, chaotic data into clear, 
    concise, and highly strategic executive summaries. You never assume; you rely 
    strictly on hard evidence and facts.""",
    tools=[calculator_tool],
    llm=llm,
    verbose=True
)

calc_task = Task(
    description="From the research, take the current price and every dollar price level mentioned in the headlines. "
                "For EACH level, call the Calculator tool with the expression '<current price> - <level>'. "
                "Report each expression and the exact value the tool returned.",
    expected_output="A list: one line per level with the expression sent to the tool and the returned value.",
    agent=analyst,
    context=[research_task],
    guardrail=required_calculator_use,
    guardrail_max_retries=3
)

analysis_task = Task(
    description="Using the research results and the calculation results provided, group the news by common theme "
             "and classify each claim as certain or uncertain. "
             "Use only numbers that appear in the calculation results; do NOT calculate anything yourself. "
             "Do not add facts that are not in the inputs. "
             "Mark any item whose time is relative (e.g. 'about 2 hours ago') or 'not available' as time-uncertain. "
             "Flag claims with weak support and say why.",
    expected_output="1. Price Comparison: The difference between the current price and each price point mentioned in the news (calculated via Calculator). \n 2. News Grouping: Items categorized and grouped by common themes. \n 3. Certainty Status: For uncertain items, include the reasoning (e.g., Missing date)",
    agent=analyst,
    context=[research_task, calc_task]   # Researcher의 결과를 이 Task의 입력으로 연결
)

reporter = Agent(
    role="Crypto Market Report Writer",
    goal="Turn the analysis into a clear markdown report without adding any new facts or numbers",
    backstory="You are an editor who writes concise, well-structured reports. You never add information that is not in your inputs.",
    tools=[],
    llm=llm,
    verbose=True
)

reporting_task = Task(
    description="Write the final report in markdown using only the provided inputs. "
                "Numbers and certainty judgments come from the analysis only. "
                "Source URLs and time text come from the research only, copied exactly as written (e.g. 'about 2 hours ago'). "
                "Do not add facts, do not calculate anything, and keep 'Uncertain' items marked as uncertain.",
    expected_output="A markdown report with these sections: Summary (max 3 sentences), Current Price, Price Comparison, Key News (grouped, with source URLs), Certainty Table, Caveats.",
    agent=reporter,
    context=[analysis_task, research_task]
)



crew = Crew(
    agents=[researcher, analyst, reporter],
    tasks=[research_task, calc_task, analysis_task, reporting_task],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    CALCULATOR_CALLS.clear()
    result = crew.kickoff(inputs={"topic": "bitcoin"})
    print(result)
    print("Actual record of calling the Calculator: ", CALCULATOR_CALLS)
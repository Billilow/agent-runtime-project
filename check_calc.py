from dotenv import load_dotenv
from crewai import Agent, LLM, Task, Crew
from crew_tools import calculator_tool, CALCULATOR_CALLS

load_dotenv()
llm = LLM(model="gemini/gemini-3.1-flash-lite")

agent = Agent(
    role="Calculator Operator",
    goal="Compute numbers with the Calculator tool",
    backstory="You always use the Calculator tool for arithmetic.",
    tools=[calculator_tool],
    llm=llm,
    verbose=True
)

task = Task(
    description="Call the Calculator tool with the expression '82199 - 83000' and report the value it returns.",
    expected_output="The number returned by the tool.",
    agent=agent
)

crew = Crew(agents=[agent], tasks=[task], verbose=True)

if __name__ == "__main__":
    crew.kickoff()
    print("Calling Rec:", CALCULATOR_CALLS)
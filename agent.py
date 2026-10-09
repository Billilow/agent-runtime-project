from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from calculator import calculator_declaration, calculator, ToolExecutionError
from crypto_price import get_crypto_price, crypto_declaration
from websearch import web_search, websearch_declaration
from circuit_breaker import CircuitBreaker

import time

TOOL_REGISTRY = {
    "calculator_tool": calculator,
    "crypto_price_tool": get_crypto_price,
    "web_search_tool": web_search
}


client = genai.Client()

tool = types.Tool(function_declarations=[calculator_declaration, crypto_declaration, websearch_declaration])
config = types.GenerateContentConfig(tools=[tool])

circuit_breaker = CircuitBreaker()

contents = []

MAX_TOOL_TURNS = 3

while True:
    user_input = input("You: ")
    if user_input == "exit":
        break

    contents.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

    for _ in range(MAX_TOOL_TURNS):
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=contents,
            config=config
        )
        part = response.candidates[0].content.parts[0]
        contents.append(response.candidates[0].content)

        if part.function_call is None:
            print(f"Agent: {part.text}")
            break

        tool_name = part.function_call.name
        tool_args = dict(part.function_call.args)

        if circuit_breaker.is_open(tool_name):
            print(f"[circuit breaker is opend: {part.function_call.name}] is currently unavailable")  # To check whether the tool has been called or not
            result = f"'{tool_name}'is currently unavailable due to repeated failures"
        else:
            print(f"[circuit breaker is closed: {part.function_call.name}]")  # To check whether the tool has been called or not

            try:
                func = TOOL_REGISTRY[tool_name]
                result = func(**tool_args)
                circuit_breaker.record_success(tool_name)
            except ToolExecutionError as e:
                result = str(e)
                circuit_breaker.record_failure(tool_name)

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_function_response(name=tool_name, response={"result": result})]
            )
        )

    else:
        print("Agent: Sorry, there is a problem handling your request.")


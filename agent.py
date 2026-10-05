from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from calculator import calculator_declaration, calculator
from crypto_price import get_crypto_price, crypto_declaration
from websearch import web_search, websearch_declaration

TOOL_REGISTRY = {
    "calculator_tool": calculator,
    "crypto_price_tool": get_crypto_price,
    "web_search_tool": web_search
}


client = genai.Client()

tool = types.Tool(function_declarations=[calculator_declaration, crypto_declaration, websearch_declaration])
config = types.GenerateContentConfig(tools=[tool])

contents = [
    types.Content(role="user", parts=[types.Part(text="오늘 비트코인 관련 최신 뉴스 헤드라인 알려줘")])
]


while True:
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=contents,
        config=config
    )
    part = response.candidates[0].content.parts[0]

    if part.function_call is None:
        print(part.text)
        break

    elif part.function_call is not None:
        print(f"[tool has called: {part.function_call.name}]")  # To check whether the tool has been called or not
        tool_name = part.function_call.name
        tool_args = dict(part.function_call.args)

        func = TOOL_REGISTRY[tool_name]
        result = func(**tool_args)

        contents.append(response.candidates[0].content)
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_function_response(name=tool_name, response={"result": result})]
            )
        )



# before the while loop
# response = client.models.generate_content(
#     model="gemini-3.1-flash-lite",
#     contents=contents,
#     config=config
# )
#
# part = response.candidates[0].content.parts[0]
# print(part)
#
# tool_name = part.function_call.name
# tool_args = dict(part.function_call.args)
#
# func = TOOL_REGISTRY[tool_name]
# result = func(**tool_args)
#
# print(result)
#
# contents.append(response.candidates[0].content)
#
# contents.append(
#     types.Content(
#         role="user",
#         parts=[types.Part.from_function_response(name=tool_name, response={"result": result})]
#     )
# )
#
# final_response = client.models.generate_content(
#     model="gemini-3.1-flash-lite",
#     contents=contents,
#     config=config
# )
#
# print(final_response)
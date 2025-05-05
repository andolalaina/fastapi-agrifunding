import uuid
from fastapi import APIRouter, HTTPException
from geojson_pydantic import Feature
from sqlmodel import Session
import asyncio
import json
import os
from datetime import datetime
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.api.deps import SessionDep
from app.models import Item
from app.core.config import settings


router = APIRouter()

@router.post("/evaluate")
async def get_ai_evaluation(session: SessionDep, item_id: uuid.UUID) -> dict:
    """
    Get AI evaluation for an item.
    """
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    # item_geo_data = {
    #     "type": "Feature",
    #     "properties": {},
    #     "geometry": {
    #         "coordinates": [
    #         item.longitude,
    #         item.latitude
    #         ],
    #         "type": "Point"
    #     }
    # }
    item_geo_data = {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              48.530741152546625,
              -15.672368795927028
            ],
            [
              48.530741152546625,
              -15.972315917326839
            ],
            [
              48.951234100395624,
              -15.972315917326839
            ],
            [
              48.951234100395624,
              -15.672368795927028
            ],
            [
              48.530741152546625,
              -15.672368795927028
            ]
          ]
        ],
        "type": "Polygon"
      }
    }
    item_description = item.description
    item_title = item.title
    item_summary = item.summary
    return await interpret(item_geo_data, item_description)


async def interpret(geo_data: dict, mock_project_description: str):
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    mock_response = {
        "spei": "L'indice SPEI est à -0.7458 sur 48 mois, indiquant une légère sécheresse chronique.",
        "rai": "L'indice 'accessibilité est de 0.552. Cela représente un niveau favorable pour les opérations logistiques.",
        "recommandations": [
            "Prévoir un système d'irrigation adapté.",
            "Installer un ombrage artificiel ou naturel.",
            "Faire une étude de sol avant plantation."

        ],
        "pertinence": {
            "note": 3.5,
            "commentaire": "Projet faisable avec précautions hydriques."
        }
    }

    preprompts = [
        "You are an expert in agriculture with deep knowledge in agronomy, statistics and remote sensing.", 
        "All your responses will be in french, no matter what language I use",
        "Your goal is to help me to understand remote sensing data and to give me the best agricultural recommendations.",
        "You are a remote sensing expert and you are able to give the best recommendations",
        "Say Ready if you are ready to answer my questions",
        "If you don't have enough information to answer after searching in all of your available tools, say which information is needed"
    ]

    main_prompts = [
        "I have an agricultural project in Madagascar and you will be in charge of evaluating the pertinence of the project and giving me the best recommendations.",
        f"Here is a description of the project : {mock_project_description}",
        f"Here is the area of interest in GeoJSON Feature format : {geo_data}",
        "From the GeoJSON Feature, get the drought data (SPEI) and the accessibility data (RAI) using the tools you have. THen, give me recommandations by completing a JSON structure with the following attributes : 'drought_data_interpretation (string)', 'zone_accessibility_interpretation (string)', 'agricultural_advices (list of string)' and 'pertinence (dictionnary with a 'note (float) 0 to 5' and 'comment (string)' attributes)'.",
        "Return only the JSON data that must be serializable with python json.loads",
        # "Now, determine the type of culture based on the description i gave you",
        # "Then, based on your expertise and the data you have, you will have to give agricultural recommendations.",
        # "Remember, as an expert, you must give recommandations based on the type of culture and the data in the area.",
        # "Your answer must be in french.",
        # "your only answer will be in JSON format with the following attributes : 'drought_data_interpretation (string)', 'zone_accessibility_interpretation (string)', 'agricultural_advices (list of string)' and 'pertinence (dictionnary with a 'note (float) 0 to 5' and 'comment (string)' attributes)'.",
        # "Evaluate my project based on drought and accessibility data and description i gave",
    ]

    output_prompts = [
        "I gave you a zone where I want to implement an agricultural project and you will be in charge of evaluating the pertinence of the project and giving me the best recommendations.",
        f"Here is a description of the project : {mock_project_description}",
        "Now, determine the type of culture based on the description i gave you",
        "Then, based on your expertise and the data you have, you will have to give agricultural recommendations.",
        "Remember, as an expert, you must give recommandations based on the type of culture and the data in the area.",
        "Your answer must be in french.",
        "your only answer will be in JSON format with the following attributes : 'drought_data_interpretation (string)', 'zone_accessibility_interpretation (string)', 'agricultural_advices (list of string)' and 'pertinence (dictionnary with a 'note (float) 0 to 5' and 'comment (string)' attributes)'."
    ]

    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="uv",  # Executable
        args=["run", "--with", "fastmcp", "fastmcp", "run", "/agrifunding-backend/mcp/server.py"],
        # args=["--with",  "fastmcp", "fastmcp", "run", r"C:\Users\m.randriajaoson\Desktop\DEV\Privé RANDRIAJAOSON Michaël\mcp-agrifunding\server.py"],  # Weather MCP Server
        env=None,  # Optional environment variables
    )

    async def run(geo_data: dict):
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Prompt to get the weather for the current day in London.
                
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(
                                text=f"I want you to use external tools and retry with some changes if it fails. How is the drought index and accessibility index in the following area ? {geo_data}",
                                # text=preprompt,
                                function_call=None,
                            )
                        # for preprompt in preprompts
                        ],
                    )
                ]

                # Initialize the connection between client and server
                await session.initialize()

                # Get tools from MCP session and convert to Gemini Tool objects
                mcp_tools = await session.list_tools()

                tools = [
                    types.Tool(
                        function_declarations=[
                            {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": {
                                    k: v
                                    for k, v in tool.inputSchema.items()
                                    if k not in ["additionalProperties", "$schema"]
                                },
                            }
                        ]
                    )
                    for tool in mcp_tools.tools
                ]
                print("TOOLS")
                print(tools)

                config = types.GenerateContentConfig(
                    temperature=0,
                    tools=tools,
                    # automatic_function_calling={"disable": True},
                    # Force the model to call 'any' function, instead of chatting.
                    # tool_config={"function_calling_config": {"mode": "any"}}
                )
                # Send request to the model with MCP function declarations
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=config,
                )
                # print("PRELIMINARY RESPONSE")
                # print(response.text)
                # contents.append(
                #     types.Content(
                #         role="user",
                #         parts=[
                #             types.Part(
                #                 text=prompt,
                #                 function_call=None,
                #             ) for prompt in main_prompts
                #         ],
                #     )
                # )
                # response = client.models.generate_content(
                #     model="gemini-2.0-flash",
                #     contents=contents,
                #     config=config,
                # )
                # print("MAIN RESPONSE")
                # print(response.text)
                print("#################################################################################")
                print("RESPONSE")
                print(response.candidates[0].content.parts[0])
                print("#################################################################################")
                # Check for a function call
                if response.candidates[0].content.parts[0].function_call:
                    function_call = response.candidates[0].content.parts[0].function_call
                    print(function_call)
                    # Call the MCP server with the predicted tool
                    result = await session.call_tool(
                        function_call.name, arguments=function_call.args
                    )
                    print(result.content[0].text)

                    # Create a function response part
                    function_response_part = types.Part.from_function_response(
                        name=function_call.name,
                        response={"result": result},
                    )

                    # Append function call and result of the function execution to contents
                    contents.append(types.Content(role="model", parts=[types.Part(function_call=function_call)])) # Append the model's function call message
                    contents.append(types.Content(role="user", parts=[function_response_part])) # Append the function response
                    
                    # contents.append(types.Content(role="user", parts=[types.Part(text=f"Based on the analysis and your general knowledge, give a json representation of the result. ")])) # Append the user message
                    # contents.append(types.Content(role="user", parts=[types.Part(text="Your final answer must be a json object with the following attributes : 'drought_data_interpretation (string)', 'zone_accessibility_interpretation (string)', 'agricultural_advices (list of string)' and 'pertinence (dictionnary with a 'note (float)' and 'comment (string)' attributes)'.")]))
                    
                    for prompt in output_prompts:
                        contents.append(
                            types.Content(
                                role="user",
                                parts=[
                                    types.Part(
                                        text=prompt,
                                        # function_call=None,
                                    )
                                ],
                            )
                        )
                    
                    final_response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        config=config,
                        contents=contents,
                    )

                    sanitized = final_response.text.replace("```json\n", '').replace("```", '')
                    return json.loads(sanitized)
                    # Continue as shown in step 4 of "How Function Calling Works"
                    # and create a user friendly response
                else:
                    print("No function call found in the response.")
                    return response.text

    return await run(geo_data)
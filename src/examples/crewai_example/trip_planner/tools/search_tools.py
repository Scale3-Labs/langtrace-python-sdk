import json
import os

import requests
from langchain.tools import tool


class SearchTools:

    @tool("Search the internet")
    def search_internet(self, query):
        """Useful to search the internet
        about a a given topic and return relevant results"""
        top_result_to_return = 4
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            "X-API-KEY": os.environ["SERPER_API_KEY"],
            "content-type": "application/json",
        }
        response = requests.request(
            "POST", url, headers=headers, data=payload, timeout=2000
        )
        # check if there is an organic key
        if "organic" not in response.json():
            return "Sorry, I couldn't find anything about that, there could be an error with you serper api key."
        else:
            results = response.json()["organic"]
            string = []
            for result in results[:top_result_to_return]:
                try:
                    string.append(
                        "\n".join(
                            [
                                f"Title: {result['title']}",
                                f"Link: {result['link']}",
                                f"Snippet: {result['snippet']}",
                                "\n-----------------",
                            ]
                        )
                    )
                except KeyError:
                    next

            return "\n".join(string)


# from pydantic import BaseModel, Field
# from langchain.tools import tool

# # Define a Pydantic model for the tool's input parameters
# class CalculationInput(BaseModel):
#     operation: str = Field(..., description="The mathematical operation to perform")
#     factor: float = Field(..., description="A factor by which to multiply the result of the operation")

# # Use the tool decorator with the args_schema parameter pointing to the Pydantic model
# @tool("perform_calculation", args_schema=CalculationInput, return_direct=True)
# def perform_calculation(operation: str, factor: float) -> str:
#     """
#     Performs a specified mathematical operation and multiplies the result by a given factor.

#     Parameters:
#     - operation (str): A string representing a mathematical operation (e.g., "10 + 5").
#     - factor (float): A factor by which to multiply the result of the operation.

#     Returns:
#     - A string representation of the calculation result.
#     """
#     # Perform the calculation
#     result = eval(operation) * factor

#     # Return the result as a string
#     return f"The result of '{operation}' multiplied by {factor} is {result}."

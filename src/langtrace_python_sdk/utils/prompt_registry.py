import os
import requests
from urllib.parse import urlencode
from typing import Optional, TypedDict, Dict, List


class LangtracePrompt(TypedDict):
    id: str
    value: str
    variables: List[str]
    model: str
    modelSettings: Dict[str, object]
    version: int
    live: bool
    tags: List[str]
    note: str
    promptsetId: str
    createdAt: str
    updatedAt: str


class FetchOptions(TypedDict, total=False):
    prompt_version: int
    variables: Dict[str, str]


def get_prompt_from_registry(
    prompt_registry_id: str,
    options: Optional[FetchOptions] = None,
    api_key: Optional[str] = None,
) -> LangtracePrompt:
    """Fetches a prompt from the registry.

    Args:
        prompt_registry_id (str): The ID of the prompt registry.
        options (dict, optional): Configuration options for fetching the prompt:
            - prompt_version (int): Fetches the prompt with the specified version.
            - variables (dict): Replaces variables in the prompt with provided values.

    Returns:
        dict: The fetched prompt with variables replaced as specified.

    Raises:
        Exception: If the fetch operation fails or returns an error.
    """
    try:
        query_params = {"promptset_id": prompt_registry_id}
        if options:
            if "prompt_version" in options:
                query_params["version"] = options["prompt_version"]
            if "variables" in options:
                for key, value in options["variables"].items():
                    query_params[f"variables.{key}"] = value
        # Encode the query parameters
        query_string = urlencode(query_params, doseq=True)
        headers = {"x-api-key": api_key or os.environ["LANGTRACE_API_KEY"]}

        # Make the GET request to the API
        response = requests.get(
            f"{os.environ['LANGTRACE_API_HOST']}/api/promptset?{query_string}",
            headers=headers,
            timeout=None,
        )
        response.raise_for_status()

        # Extract the prompt data from the response
        prompt_data = response.json()["prompts"][0]
        return prompt_data

    except requests.RequestException as err:
        # Handle specific HTTP errors or general request exceptions
        error_msg = str(err)
        if err.response:
            try:
                # Try to extract server-provided error message
                error_msg = err.response.json().get("error", error_msg)
            except ValueError:
                # Fallback if response is not JSON
                error_msg = err.response.text
        raise Exception(f"API error: {error_msg}") from err

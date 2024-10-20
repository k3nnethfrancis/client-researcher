"""
Client Profiler Module

This module generates and saves detailed client profiles using the phi library.
It uses an AI agent to build the profile based on input information and saves
the result as a JSON file.

Usage:
    python -m client_profiler

The script will prompt for client information and generate a profile.
"""

import os
import json
import logging
import re
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.model.ollama import Ollama
from phi.tools.duckduckgo import DuckDuckGo
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
import argparse

from dotenv import load_dotenv; load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsItem(BaseModel):
    title: str
    url: Optional[str] = None

class ClientProfile(BaseModel):
    """Model representing a client profile."""
    name: str = Field(..., description="Full name of the client")
    bio: str = Field(..., description="Bio of the client")
    expertise: List[str] = Field(default_factory=list, description="List of areas of expertise")
    current_goals: List[str] = Field(default_factory=list, description="List of current professional goals")
    company_news: List[NewsItem] = Field(default_factory=list, description="Recent news related to the client's company")
    additional_info: Optional[Dict[str, Union[str, List[str]]]] = Field(None, description="Additional information about the client")

client_profile_builder = Agent(
    name="Client Profile Builder",
    role="Build detailed profiles of clients",
    model=OpenAIChat(id="gpt-4o-mini"),  # or "gpt-3.5-turbo"
    tools=[DuckDuckGo()],
    response_model=ClientProfile,
)

def save_client_profile(profile: ClientProfile):
    """Save the client profile to a JSON file."""
    filename = f"profiles/{profile.name.replace(' ', '_').lower()}.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(profile.dict(), f, indent=2, default=str)
    logger.info(f"Profile saved to {filename}")

def extract_json_from_text(text: str) -> dict:
    """
    Extract a JSON object from a text string.

    Args:
        text (str): The text containing a JSON object.

    Returns:
        dict: The extracted JSON object as a dictionary.
    """
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from the extracted text")
    return {}

def main(client_name: str, context: str = ""):
    """
    Generate and save a client profile.

    Args:
        client_name (str): The name of the client.
        context (str, optional): Additional context about the client. Defaults to "".
    """
    logger.info(f"Generating profile for: {client_name}")
    prompt = f"Generate a detailed profile for {client_name}. "
    if context:
        prompt += f"Additional context: {context}"
    
    try:
        run_response = client_profile_builder.run(prompt)
        logger.debug(f"Run response: {run_response}")
        
        if hasattr(run_response, 'content'):
            if isinstance(run_response.content, ClientProfile):
                profile = run_response.content
            elif isinstance(run_response.content, dict):
                # Convert company_news to NewsItem objects if necessary
                if 'company_news' in run_response.content:
                    run_response.content['company_news'] = [
                        NewsItem(**item) if isinstance(item, dict) else NewsItem(title=item)
                        for item in run_response.content['company_news']
                    ]
                # Handle additional_info
                if 'additional_info' in run_response.content:
                    for key, value in run_response.content['additional_info'].items():
                        if isinstance(value, list):
                            run_response.content['additional_info'][key] = ', '.join(value)
                profile = ClientProfile(**run_response.content)
            elif isinstance(run_response.content, str):
                json_data = extract_json_from_text(run_response.content)
                if json_data:
                    # Convert company_news to NewsItem objects if necessary
                    if 'company_news' in json_data:
                        json_data['company_news'] = [
                            NewsItem(**item) if isinstance(item, dict) else NewsItem(title=item)
                            for item in json_data['company_news']
                        ]
                    # Handle additional_info
                    if 'additional_info' in json_data:
                        for key, value in json_data['additional_info'].items():
                            if isinstance(value, list):
                                json_data['additional_info'][key] = ', '.join(value)
                    profile = ClientProfile(**json_data)
                else:
                    raise ValueError("Could not extract valid JSON from the response")
            else:
                raise TypeError(f"Unexpected content type: {type(run_response.content)}")
            
            save_client_profile(profile)
            return profile
        else:
            logger.error("Run response does not have a 'content' attribute")
            raise ValueError("Invalid response from client profile builder")
    except Exception as e:
        logger.error(f"An error occurred while generating the profile: {str(e)}")
        logger.debug("Error details:", exc_info=True)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a client profile.")
    parser.add_argument("client_name", help="Name of the client")
    parser.add_argument("--context", help="Additional context about the client", default="")
    args = parser.parse_args()
    
    main(args.client_name, args.context)

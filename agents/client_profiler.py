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
from typing import List, Optional

from dotenv import load_dotenv; load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClientProfile(BaseModel):
    """Model representing a client profile."""
    name: str = Field(..., description="Full name of the client")
    current_position: str = Field(..., description="Current job position of the client")
    company: str = Field(..., description="Company where the client works")
    expertise: List[str] = Field(..., description="List of areas of expertise")
    education: Optional[str] = Field(None, description="Educational background of the client")
    recent_activities: List[str] = Field(..., description="List of recent professional activities or achievements")
    linkedin_profile: Optional[str] = Field(None, description="LinkedIn profile URL if available")
    company_news: List[str] = Field(..., description="Recent news related to the client's company")
    current_goals: List[str] = Field(..., description="List of current professional goals")

client_profile_builder = Agent(
    name="Client Profile Builder",
    role="Build detailed profiles of clients",
    model=OpenAIChat(id="gpt-4o"),
    # model=Ollama(id="llama3.1:70b"),
    tools=[DuckDuckGo()],
    response_model=ClientProfile,
    # structured_outputs=True,
    # stream=True,
)

def save_client_profile(profile: ClientProfile):
    """
    Save the client profile as a JSON file.

    Args:
        profile (ClientProfile): The client profile to save.
    """
    os.makedirs('profiles', exist_ok=True)
    filename = f"profiles/{profile.name.replace(' ', '_').lower()}.json"
    with open(filename, 'w') as f:
        json.dump(profile.dict(), f, indent=2)
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

def main(client_name: str):
    """
    Generate and save a client profile.

    Args:
        client_name (str): The name and additional information about the client.
    """
    logger.info(f"Generating profile for: {client_name}")
    try:
        run_response = client_profile_builder.run(client_name)
        logger.debug(f"Run response: {run_response}")
        
        if hasattr(run_response, 'content'):
            if isinstance(run_response.content, ClientProfile):
                profile = run_response.content
            elif isinstance(run_response.content, dict):
                profile = ClientProfile(**run_response.content)
            elif isinstance(run_response.content, str):
                json_data = extract_json_from_text(run_response.content)
                if json_data:
                    profile = ClientProfile(**json_data)
                else:
                    raise ValueError("Could not extract valid JSON from the response")
            else:
                raise TypeError(f"Unexpected content type: {type(run_response.content)}")
            
            save_client_profile(profile)
        else:
            logger.error("Run response does not have a 'content' attribute")
    except Exception as e:
        logger.error(f"An error occurred while generating the profile: {str(e)}")
        logger.debug("Error details:", exc_info=True)

if __name__ == "__main__":
    client_name = input("Enter the client's name, relevant info, and social profiles for scraping: ")
    main(client_name)

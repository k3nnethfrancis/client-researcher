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
import argparse

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
    model=OpenAIChat(id="gpt-4o-mini"),  # or "gpt-3.5-turbo"
    tools=[DuckDuckGo()],
    response_model=ClientProfile,
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

def load_client_profile(client_name: str) -> ClientProfile:
    """Load a client profile from the profiles directory."""
    filename = f"profiles/{client_name.replace(' ', '_').lower()}.json"
    if not os.path.exists(filename):
        raise FileNotFoundError(f"No profile found for {client_name}.")
    
    with open(filename, 'r') as f:
        profile_data = json.load(f)
    return ClientProfile(**profile_data)

def main(client_name: str, create_new: bool = True):
    """
    Generate and save a client profile or load an existing one.

    Args:
        client_name (str): The name and additional information about the client.
        create_new (bool): Whether to create a new profile or load an existing one.
    """
    if create_new:
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
    else:
        try:
            profile = load_client_profile(client_name)
            logger.info(f"Loaded existing profile for: {client_name}")
        except FileNotFoundError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(f"An error occurred while loading the profile: {str(e)}")
            logger.debug("Error details:", exc_info=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate or load a client profile.")
    parser.add_argument("client_name", help="Name and additional information about the client")
    parser.add_argument("--load", action="store_true", help="Load an existing profile instead of creating a new one")
    args = parser.parse_args()
    main(args.client_name, create_new=not args.load)

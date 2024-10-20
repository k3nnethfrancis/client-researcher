"""
Content Researcher Module

This module provides functionality to research and find relevant content
based on a given client profile using OpenAI's GPT model, DuckDuckGo search, and Hacker News.

The main components are:
1. SearchResult: A model for storing detailed search results.
2. ContentResearcherResults: A model for storing a list of search results and metadata.
3. research_content: A function to research content based on a client profile.
4. save_results: A function to save the research results to a file.

Usage:
    python -m content_researcher <client_name>

Note: Make sure to set the OPENAI_API_KEY in your .env file.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.hackernews import HackerNews
from dotenv import load_dotenv
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class SearchResult(BaseModel):
    """Model for storing a single search result."""
    title: str = Field(..., description="Title of the search result")
    url: Optional[str] = Field(None, description="URL of the search result")
    summary: str = Field(..., description="Brief summary of the content")
    relevance: str = Field(..., description="Explanation of how this is relevant to the client")

class ContentResearcherResults(BaseModel):
    """Model for storing a list of search results."""
    results: List[SearchResult] = Field(..., description="List of search results")
    client_name: Optional[str] = Field(None, description="Name of the client for whom the research was conducted")

content_researcher = Agent(
    name="Content Researcher",
    role="Research content based on client profile and additional context",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGo(), HackerNews()],
    response_model=ContentResearcherResults,
    structured=True,
)

def load_client_profile(client_name: str) -> Dict[str, Any]:
    """Load a client profile from the profiles directory."""
    filename = f"profiles/{client_name.replace(' ', '_').lower()}.json"
    if not os.path.exists(filename):
        raise FileNotFoundError(f"No profile found for {client_name}. Please run the client profiler first.")
    
    with open(filename, 'r') as f:
        profile_data = json.load(f)
    return profile_data

def research_content(client_profile: Dict[str, Any], additional_context: str = "") -> ContentResearcherResults:
    """
    Research content based on a client profile and additional context.

    Args:
        client_profile (Dict[str, Any]): The client profile dictionary.
        additional_context (str, optional): Additional context to guide the search. Defaults to "".

    Returns:
        ContentResearcherResults: The research results.
    """
    logger.info("Starting content research")
    prompt = f"""
    Research and find relevant content based on the following client profile and additional context:

    Client Profile:
    {json.dumps(client_profile, indent=2)}

    Additional Context:
    {additional_context}

    Please provide a list of relevant articles, news, or resources that would be valuable for this client.
    For each piece of content, include:
    1. Title
    2. URL (if available)
    3. Brief summary
    4. Relevance to the client's interests or goals

    Aim to provide a diverse set of results that cover different aspects of the client's interests and the additional context provided.
    """

    try:
        logger.info("Sending request to content researcher agent")
        result = content_researcher.run(prompt)
        logger.info(f"Received response from content researcher agent: {result.content}")
        
        # The result.content is already a ContentResearcherResults object
        return result.content
    except Exception as e:
        logger.error(f"An error occurred while researching content: {str(e)}")
        logger.debug("Error details:", exc_info=True)
        return ContentResearcherResults(results=[], client_name=client_profile.get('name'))

# Update the save_results function to handle ContentResearcherResults directly
def save_results(results: ContentResearcherResults, filename: str = 'content_researcher_results.json', append: bool = False):
    """
    Save research results to a JSON file.

    Args:
        results (ContentResearcherResults): The research results to save.
        filename (str): The name of the file to save results to.
        append (bool): Whether to append to existing results or overwrite.
    """
    logger.info(f"Saving results to {filename}")
    os.makedirs('content', exist_ok=True)
    file_path = f'content/{filename}'
    
    results_dict = results.dict()
    
    if append and os.path.exists(file_path):
        logger.info("Appending to existing file")
        with open(file_path, 'r') as f:
            existing_data = json.load(f)
        existing_data['results'].extend(results_dict['results'])
        results_dict = existing_data
    else:
        logger.info("Creating new file or overwriting existing file")
    
    with open(file_path, 'w') as f:
        json.dump(results_dict, f, indent=2)
    logger.info("Results saved successfully")

def main(client_name: str):
    """Main function to run the content researcher."""
    logger.info(f"Starting content researcher for client: {client_name}")
    client_profile = load_client_profile(client_name)
    research_results = research_content(client_profile)
    save_results(research_results)
    logger.info("Content researcher completed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run content research for a client.")
    parser.add_argument("client_name", help="Name of the client to research")
    args = parser.parse_args()
    main(args.client_name)

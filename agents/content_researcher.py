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
    """Model for storing a list of search results and metadata."""
    results: List[SearchResult] = Field(..., description="List of search results")
    client_name: Optional[str] = Field(None, description="Name of the client for whom the research was conducted")
    queries: List[str] = Field(default_factory=list, description="List of queries used to produce the results")

content_researcher = Agent(
    name="Content Researcher",
    role="Research content based on client profile and additional context",
    model=OpenAIChat(id="gpt-4o-mini"),  # Make sure this is a valid model
    tools=[DuckDuckGo(), HackerNews()],
    response_model=ContentResearcherResults,
    structured=False,
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

    Please provide:
    1. A list of search queries you would use to find relevant information for this client.
    2. A list of relevant articles, news, or resources that would be valuable for this client.

    For each piece of content, include:
    a. Title
    b. URL (if available)
    c. Brief summary
    d. Relevance to the client's interests or goals
    """

    try:
        result = content_researcher.run(prompt)
        logger.info(f"Raw response from content researcher agent: {result}")
        
        if isinstance(result.content, ContentResearcherResults):
            research_results = result.content
        elif isinstance(result.content, dict):
            research_results = ContentResearcherResults(**result.content)
        elif isinstance(result.content, str):
            # If the response is a string, try to parse it as JSON
            content_dict = json.loads(result.content)
            research_results = ContentResearcherResults(**content_dict)
        else:
            logger.warning(f"Unexpected response format from content researcher agent: {type(result.content)}")
            research_results = ContentResearcherResults(
                results=[],
                client_name=client_profile.get('name'),
                queries=[]
            )

        # Save the results
        save_results(research_results, client_name=client_profile.get('name'))

        return research_results
    except Exception as e:
        logger.error(f"An error occurred while researching content: {str(e)}")
        logger.debug("Error details:", exc_info=True)
        return ContentResearcherResults(
            results=[],
            client_name=client_profile.get('name'),
            queries=["Error occurred during research"]
        )

def save_results(results: ContentResearcherResults, client_name: str, filename: str = 'content_researcher_results.json'):
    logger.info(f"Saving results for {client_name}")
    os.makedirs('content', exist_ok=True)
    file_path = f'content/{client_name.replace(" ", "_").lower()}_{filename}'
    
    with open(file_path, 'w') as f:
        json.dump(results.dict(), f, indent=2)
    logger.info(f"Results saved to {file_path}")

def main(client_name: str, additional_context: str = ""):
    """Main function to run the content researcher."""
    logger.info(f"Starting content research for client: {client_name}")
    
    # Load the client profile
    profile_path = f"profiles/{client_name.replace(' ', '_').lower()}.json"
    if not os.path.exists(profile_path):
        logger.error(f"No profile found for {client_name}. Please create a profile first.")
        return
    
    with open(profile_path, 'r') as f:
        client_profile = json.load(f)
    
    # Perform content research
    research_results = research_content(client_profile, additional_context)
    
    # Save results
    save_results(research_results, client_name)
    
    logger.info(f"Content research completed for {client_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform content research for a client.")
    parser.add_argument("client_name", help="Name of the client")
    parser.add_argument("--context", default="", help="Additional context for the research")
    
    args = parser.parse_args()
    
    main(args.client_name, args.context)

    test_profile = {
        "name": "Sam Altman",
        "expertise": ["Artificial Intelligence", "Startups", "Clean Energy"],
        "current_goals": ["Build AGI rapidly", "Ensure AI benefits all of humanity", "Expand Worldcoin's reach"]
    }
    results = research_content(test_profile)
    print(json.dumps(results.dict(), indent=2))

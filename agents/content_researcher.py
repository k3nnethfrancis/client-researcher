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

    Format your response as a JSON object with two keys: 'queries' (a list of strings) and 'results' (a list of content objects).
    """

    try:
        logger.info("Sending request to content researcher agent")
        result = content_researcher.run(prompt)
        logger.info(f"Raw response from content researcher agent: {result}")
        
        if isinstance(result.content, ContentResearcherResults):
            # If the result is already a ContentResearcherResults object, use it directly
            return result.content
        elif isinstance(result.content, str):
            # If the response is a string, try to parse it as JSON
            try:
                content_dict = json.loads(result.content)
            except json.JSONDecodeError:
                logger.warning("Failed to parse response as JSON. Using fallback parsing.")
                # Fallback: try to extract JSON-like content from the string
                import re
                json_match = re.search(r'\{[\s\S]*\}', result.content)
                if json_match:
                    content_dict = json.loads(json_match.group())
                else:
                    raise ValueError("Could not extract valid JSON from the response")
        else:
            raise TypeError(f"Unexpected content type: {type(result.content)}")

        queries = content_dict.get('queries', [])
        results = [SearchResult(**item) for item in content_dict.get('results', [])]

        logger.info(f"Extracted queries: {queries}")
        logger.info(f"Extracted results: {results}")

        return ContentResearcherResults(
            results=results,
            client_name=client_profile.get('name'),
            queries=queries
        )
    except Exception as e:
        logger.error(f"An error occurred while researching content: {str(e)}")
        logger.debug("Error details:", exc_info=True)
        return ContentResearcherResults(
            results=[],
            client_name=client_profile.get('name'),
            queries=["Error occurred during research"]
        )

# Update the save_results function to handle ContentResearcherResults directly
def save_results(results: ContentResearcherResults, filename: str = 'content_researcher_results.json', append: bool = False):
    logger.info(f"Saving results to {filename}")
    os.makedirs('content', exist_ok=True)
    file_path = f'content/{filename}'
    
    results_dict = {
        "results": [result.dict() for result in results.results],
        "client_name": results.client_name,
        "queries": results.queries
    }
    
    if append and os.path.exists(file_path):
        logger.info("Appending to existing file")
        with open(file_path, 'r') as f:
            existing_data = json.load(f)
        existing_data['results'].extend(results_dict['results'])
        existing_data['queries'].extend(results_dict['queries'])
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

    test_profile = {
        "name": "Kenneth Francis Cavanagh",
        "expertise": ["AI Chatbots", "Business Analysis", "Data Science"],
        "current_goals": ["Explore the intersection of AI and psychology"]
    }
    results = research_content(test_profile)
    print(json.dumps(results.dict(), indent=2))

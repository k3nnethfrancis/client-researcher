"""
Content Researcher Module

This module provides functionality to research and find relevant content
based on a given client profile using OpenAI's GPT model, Perplexity API,
DuckDuckGo search, and Hacker News.

The main components are:
1. SearchResult: A model for storing detailed search results.
2. ContentResearcherResults: A model for storing a list of search results and metadata.
3. query_perplexity: A function to query the Perplexity API.
4. research_content: A function to research content based on a client profile.
5. save_results: A function to save the research results to a file.

Usage:
    python -m content_researcher

Note: Make sure to set the OPENAI_API_KEY and PERPLEXITY_API_KEY in your .env file.
"""

import os
import json
import requests
import logging
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.hackernews import HackerNews
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
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

def query_perplexity(profile: str) -> str:
    """
    Query the Perplexity API for relevant content based on a client profile.

    Args:
        profile (str): Client profile to base the search on.

    Returns:
        str: Content of the search result.
    """
    logger.info("Querying Perplexity API")
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": f"Find content that might be relevant to the following person: {profile}"}
        ],
        "temperature": 0.2,
        "top_p": 0.9,
        "return_citations": "true",
        "search_domain_filter": ["perplexity.ai"],
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": "day",
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()
    
    logger.info("Received response from Perplexity API")
    return result['choices'][0]['message']['content']

content_researcher = Agent(
    name="Content Researcher",
    role="Research content based on client profile",
    model=OpenAIChat(api_key=OPENAI_API_KEY),
    tools=[DuckDuckGo(), HackerNews()],
    # tools=[query_perplexity, HackerNews()],
    response_model=ContentResearcherResults,
    structured=True,
    # stream=True,
)

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
    content_researcher = Agent(
        name="Content Researcher",
        role="Research content based on client profile and additional context",
        model=OpenAIChat(id="gpt-4"),
        tools=[DuckDuckGo(), HackerNews()],
    )

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

    Format your response as a JSON array of objects, where each object represents a search result with the following structure:
    {{
        "title": "Article Title",
        "url": "https://example.com/article",
        "summary": "Brief summary of the content",
        "relevance": "Explanation of how this is relevant to the client"
    }}

    If a URL is not available, use null for the url field.

    Aim to provide a diverse set of results that cover different aspects of the client's interests and the additional context provided.
    """

    result = content_researcher.run(prompt)
    
    try:
        search_results = json.loads(result.content)
        validated_results = [SearchResult(**item) for item in search_results]
        return ContentResearcherResults(results=validated_results, client_name=client_profile.get('name'))
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON from the research results")
        return ContentResearcherResults(results=[], client_name=client_profile.get('name'))

def save_results(results: ContentResearcherResults, filename: str = 'content_researcher_results.json', append: bool = False):
    """
    Save research results to a JSON file.

    Args:
        results (ContentResearcherResults): The research results to save.
        filename (str): The name of the file to save results to.
        append (bool): Whether to append to existing results or overwrite.
    """
    logger.info(f"Saving results to {filename}")
    os.makedirs('data', exist_ok=True)
    file_path = f'data/{filename}'
    
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

def main():
    """Main function to run the content researcher."""
    logger.info("Starting content researcher")
    # Example client profile
    test_profile = {
        "name": "Kenneth Francis Cavanagh",
        "expertise": [
            "AI Chatbots", "Business Analysis", "Business Strategy", "Data Science",
            "HTML + CSS", "JavaScript", "Psychometrics", "Python", "SQL", "Writing"
        ],
        "education": "Master's in Industrial Psychology from CUNY Brooklyn College",
        "recent_activities": [
            "Built project LION AI for talentDAO.",
            "Published thought on LLMs and the engineering paradigms that take models like GPT-4 \"out of the box\" and into the world."
        ],
        "current_goals": [
            "Learn about the latest advancements in AI and machine learning.",
            "Explore the intersection of AI and psychology.",
            "Build an AI consulting business.",
            "Develop a custom AI agent system to help him automate his research and business operations."
        ],
        "linkedin_profile": "https://mw.linkedin.com/k3nneth",
    }

    research_results = research_content(test_profile)
    save_results(research_results)
    logger.info("Content researcher completed")

if __name__ == "__main__":
    main()

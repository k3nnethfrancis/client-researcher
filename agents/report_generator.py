"""
Report Generator Agent

This module contains the ReportGenerator class, which is responsible for generating
insightful reports based on research results and client profiles.
"""

import json
from typing import Dict

from phi.agent import Agent
from phi.model.openai import OpenAIChat

from agents.content_researcher import ContentResearcherResults
from agents.client_profiler import ClientProfile

class ReportGenerator:
    def __init__(self):
        self.agent = Agent(
            name="Report Generator",
            role="Generate insightful reports based on research results",
            model=OpenAIChat(id="gpt-4-turbo-preview"),
        )

    def generate_report(self, research_results: ContentResearcherResults, client_profile: ClientProfile, additional_context: str = "") -> str:
        """Generate a markdown report based on the research results and client profile."""
        prompt = f"""
        Generate a markdown report for our client based on the following information:

        Client Profile:
        {json.dumps(client_profile.dict(), indent=2)}

        Research Results:
        {json.dumps(research_results.dict(), indent=2)}

        Additional Context:
        {additional_context}

        The report should include:
        1. A brief summary of the most relevant and interesting findings
        2. How these findings relate to the client's expertise and goals
        3. Any actionable insights or recommendations
        4. A section highlighting the most relevant news or developments in the client's industry

        Format the report in markdown, with appropriate headers, bullet points, and emphasis where needed.
        """

        response = self.agent.run(prompt)
        return response.content

def generate_report(research_results: ContentResearcherResults, client_profile: ClientProfile, additional_context: str = "") -> str:
    """Convenience function to generate a report without instantiating the ReportGenerator class."""
    report_generator = ReportGenerator()
    return report_generator.generate_report(research_results, client_profile, additional_context)
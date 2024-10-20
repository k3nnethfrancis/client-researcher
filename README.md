# client-researcher

client-researcher is an AI-powered content research and reporting tool designed to generate personalized reports for clients based on their profiles and interests.

## Overview

This project consists of several components:

1. **Client Profiler**: Generates detailed client profiles based on input information.
2. **Content Researcher**: Searches for relevant content based on client profiles and additional context.
3. **Report Generator**: Creates markdown reports summarizing the research findings.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/client-researcher.git
   cd client-researcher
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   Create a `.env` file in the project root and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### 1. Generate a Client Profile

Run the client profiler to create a new client profile:

```
python -m agents.client_profiler "Client Name"
```

This will generate a profile for the specified client and save it in the `profiles` directory.

### 2. Run the Content Researcher

To research content for a specific client:

```
python -m agents.content_researcher "Client Name"
```

This will perform content research based on the client's profile and save the results in the `content` directory.

### 3. Generate a Report

To generate a report for a client:

```
python agent_executor.py --client "Client Name" [--context "Additional context"]
```

This will run the entire workflow, including profile loading (or generation if it doesn't exist), content research, and report generation. The generated report will be saved in the `reports` directory.

### 4. Context flag and modular execution

The context flag allows you to add additional context to the research process. This can be useful to build more accurate profiles (e.g., when you have a clients name and an affiliation such as their company the search can more reliably find the exact person you are researching) and to add additional context to the research process (e.g., when you want to add a specific question you want to answer about or for the client).

You can also run the individual agents by calling them directly, with or without the context flag. For example:

```
python -m agents.client_profiler "Client Name" --context "Additional context"
```

## Example Outputs

See example outputs in their respective directories:

- [profiles](/profiles/example.json)
- [content](/content/example.json)
- [reports](/reports/example.md)

### Example Profile

```json
{
  "name": "Sam Altman",
  "bio": "Samuel Harris Altman (born April 22, 1985) is an American entrepreneur and investor best known as the CEO of OpenAI since 2019. He briefly experienced being fired and reinstated in November 2023. He is also the chairman of clean energy companies Oklo Inc. and Helion Energy. Altman is regarded as a leading figure in the AI technology boom, driving advancements and discussions around Artificial General Intelligence (AGI). He is recognized for his vision of aligning AI development with societal benefits.",
  "expertise": [
    "Artificial Intelligence",
    "Entrepreneurship",
    "Investment",
    "Clean Energy",
    "Technology Trends"
  ],
  "current_goals": [
    "Build AGI rapidly",
    "Ensure AI benefits all of humanity",
    "Expand Worldcoin's reach",
    "Promote clean energy initiatives",
    "Engage in policy discussions regarding AI and energy"
  ],
  "company_news": [
    {
      "title": "Sam Altman's Worldcoin becomes World and shows new iris-scanning Orb to prove your humanity",
      "url": "https://techcrunch.com/2024/10/17/sam-altmans-worldcoin-becomes-world-and-shows-new-iris-scanning-orb-to-prove-your-humanity/"
    },
    {
      "title": "This is OpenAI CEO Sam Altman's favorite question about AGI",
      "url": "https://www.msn.com/en-us/news/technology/this-is-openai-ceo-sam-altman-s-favorite-question-about-agi/ar-AA1synEV"
    },
    {
      "title": "Sam Altman risks spreading himself too thin at OpenAI",
      "url": "https://www.msn.com/en-us/money/companies/sam-altman-risks-spreading-himself-too-thin-at-openai/ar-AA1st8zu"
    },
    {
      "title": "WLD Price Forecast: Sam Altman's Worldcoin Targets 1B Users with Ethereum L2 Launch",
      "url": "https://www.fxempire.com/forecasts/article/wld-price-forecast-sam-altmans-worldcoin-targets-1b-users-with-ethereum-l2-launch-1469559"
    },
    {
      "title": "Sam Altman's Energy 'New Deal' Is Good for AI. What About Americans?",
      "url": "https://www.bloomberg.com/news/articles/2024-10-17/sam-altman-s-energy-new-deal-is-good-for-openai-and-ai-what-about-americans"
    }
  ],
  "additional_info": {
    "notable_projects": [
      "OpenAI",
      "Worldcoin",
      "Oklo Inc.",
      "Helion Energy"
    ],
    "interests": [
      "Ethical AI",
      "Public Policy",
      "Transformative Technologies"
    ]
  }
}
```


## Viewing Reports

To view a generated report rendered in your browser, you can use the `grip` tool. First, make sure you have `grip` installed:

```
pip install grip
```

Then, to view a specific report, run:

```
grip reports/<report_name>.md
```

Replace `<report_name>` with the actual name of the report file you want to view. This will start a local server, and you can view the rendered report by opening a web browser and navigating to the URL provided by grip (usually http://localhost:6419).


## Project Structure

- `agents/`: Directory containing the agent modules
  - `client_profiler.py`: Handles the creation and storage of client profiles.
  - `content_researcher.py`: Performs content research based on client profiles and additional context.
  - `report_generator.py`: Generates the final report based on research results.
- `agent_executor.py`: The main script that orchestrates the entire workflow.
- `profiles/`: Directory containing saved client profiles.
- `content/`: Directory containing raw research results.
- `reports/`: Directory containing generated markdown reports.

## Customization

You can customize the behavior of the AI agents by modifying the prompts and configurations in the respective agent files within the `agents/` directory.

## Dependencies

- phi: A library for building AI agents.
- pydantic: Data validation and settings management using Python type annotations.
- python-dotenv: Loads environment variables from a .env file.

## Troubleshooting

If you encounter any issues while running the scripts, check the following:

1. Ensure all dependencies are correctly installed.
2. Verify that your `.env` file contains the correct API keys.
3. Check the console output for any error messages or logs that might indicate the problem.

If you're still having trouble, please open an issue on the GitHub repository with a detailed description of the problem and any relevant error messages.

## Potential Improvements

1. Add perplexity integration
2. Add better validation to allow open source models to be used more reliably
3. Integration with additional data sources for more comprehensive research.
4. Prompt engineering for better content relevance scoring.å

## Contributing

Contributions to client-researcher are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

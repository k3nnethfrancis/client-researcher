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
python -m client_profiler
```

Follow the prompts to enter the client's information. The profile will be saved in the `profiles` directory.

### 2. Run the Content Researcher

To research content for a specific client:

```
python agent_executor.py --client "Client Name" --context "Additional context for search"
```

This will generate a research report based on the client's profile and the provided context.

### 3. View the Generated Report

After running the agent_executor.py script, you can find the generated report in the `reports` directory. The filename will include the client's name and a timestamp.

## Project Structure

- `client_profiler.py`: Handles the creation and storage of client profiles.
- `content_researcher.py`: Performs content research based on client profiles and additional context.
- `agent_executor.py`: The main script that orchestrates the workflow, including content research and report generation.
- `profiles/`: Directory containing saved client profiles.
- `data/`: Directory containing raw research results.
- `reports/`: Directory containing generated markdown reports.

## Customization

You can customize the behavior of the AI agents by modifying the prompts in `content_researcher.py` and `agent_executor.py`. Adjust the search queries, result formatting, or report structure to better suit your needs.

## Dependencies

- phi: A library for building AI agents.
- pydantic: Data validation and settings management using Python type annotations.
- python-dotenv: Loads environment variables from a .env file.

## Contributing

Contributions to client-researcher are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

If you encounter any issues while running the scripts, check the following:

1. Ensure all dependencies are correctly installed.
2. Verify that your `.env` file contains the correct API keys.
3. Check the console output for any error messages or logs that might indicate the problem.

If you're still having trouble, please open an issue on the GitHub repository with a detailed description of the problem and any relevant error messages.

## Potential Improvements

1. Integration with additional data sources for more comprehensive research.
2. Prompt engineering for better content relevance scoring.
3. A web interface for easier interaction with the tool.

We hope you find client-researcher useful for your content research needs. If you have any questions or feedback, please don't hesitate to reach out or open an issue on GitHub.

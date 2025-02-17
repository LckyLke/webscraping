# Web-aware LLM Chat

An AI chat application using LLMs with custom web-scraped context.

## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Create a conda environment and install dependencies:
   ```bash
   conda create -n webai-chat python=3.10.14
   conda activate webai-chat
   pip install -e .
   ```
3. Add OpenAI API key to `.env`:
   ```env
   OPENAI_API_KEY=your-api-key
   ```

## Usage
Run with:
```bash
webai-chat --url https://tentris.io --api_key your-api-key
```
- `--url`: Starting URL for context (default: https://tentris.io).
- `--api_key`: OpenAI API key (default from `.env`).

Type queries in the chat interface, exit with `exit` or `quit`.



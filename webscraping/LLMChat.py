from openai import OpenAI

import argparse
from scraper.scraper.spiders.domain_text_spider import ScrapyManager, LLMContextManager

class OpenAIChatHandler:
    def __init__(self, llm_context_manager: LLMContextManager, api_key: str):
        self.context_manager = llm_context_manager
        self.chat_history = []
        self.client = OpenAI(api_key=api_key)

    def _format_context(self, max_length: int = 16000) -> str:
        """Prepare context ensuring it doesn't exceed token limits"""
        full_context = self.context_manager.get_context()
        return full_context[:max_length]

    def query_llm(self, user_input: str, temperature: float = 0.7) -> str:
        """Send query to OpenAI with context"""
        context = self._format_context()

        messages = [
            {"role": "system", "content": f"You are a knowledgeable assistant. Use this context to answer questions:\n{context}"},
            *self.chat_history[-6:],  # Keep last 3 exchanges
            {"role": "user", "content": user_input}
        ]

        response = self.client.chat.completions.create(model="gpt-3.5-turbo",
        messages=messages,
        temperature=temperature,
        max_tokens=1000)

        assistant_response = response.choices[0].message.content
        self.chat_history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": assistant_response}
        ])
        return assistant_response

def main():
    parser = argparse.ArgumentParser(description='Web-aware AI Chat')
    parser.add_argument('--url', type=str, required=True, help='Starting URL for context gathering')
    parser.add_argument('--api_key', type=str, required=True, help='OpenAI API key')
    args = parser.parse_args()

    # Initialize components
    scrapy_manager = ScrapyManager()
    llm_manager = LLMContextManager(scrapy_manager)
    llm_manager.build_context(args.url)

    chat_handler = OpenAIChatHandler(llm_manager, args.api_key)

    print("Context loaded. Start chatting (type 'exit' to quit)!")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                break

            response = chat_handler.query_llm(user_input)
            print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
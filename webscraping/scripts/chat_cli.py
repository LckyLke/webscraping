import argparse
from webscraping.scraper.spiders.domain_text_spider import ScrapyManager, LLMContextManager
from webscraping.LLMChat import OpenAIChatHandler  
from dotenv import load_dotenv
import os

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description='Web-aware AI Chat')
    parser.add_argument('--url', type=str, default='https://tentris.io', help='Starting URL for context gathering')
    parser.add_argument('--api_key', type=str, default=os.getenv('OPENAI_API_KEY'), help='OpenAI API key')
    args = parser.parse_args()

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

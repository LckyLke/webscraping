from setuptools import setup, find_packages

setup(
    name="Web-Scraper and LLM Chat",
    version="0.1.0",
    description="Web scraper and LLM chatbot",
    author="Luke Friedrichs",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-dotenv",
		"openai",
		"scrapy",
		"scrapy-playwright",
    ],
    entry_points={
        'console_scripts': [
        ],
    },
)

"""
AMD Token Factory Smoke Test
Reads LLM_BASE_URL, LLM_API_KEY, LLM_MODEL from .env
Sends a one-sentence greeting prompt and measures response time and token count.
"""

import os
import sys
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from openai import OpenAI

def main():
    # Load environment variables from .env
    load_dotenv()

    base_url = os.getenv("LLM_BASE_URL")
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")

    if not base_url or not api_key or not model:
        print("ERROR: Missing configuration in .env file!")
        print("Please ensure LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL are all defined.")
        sys.exit(1)

    print(f"Connecting to AMD Token Factory at: {base_url}")
    print(f"Target Model: {model}")
    print("Sending test prompt: 'Say hello in one sentence' ...\n")

    try:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=30.0
        )

        start_time = time.perf_counter()

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Say hello in one sentence."}
            ],
            temperature=0.2,
            max_tokens=100
        )

        elapsed_time = time.perf_counter() - start_time

        reply = response.choices[0].message.content.strip()
        completion_tokens = response.usage.completion_tokens if response.usage else "N/A"

        print("=== AMD TOKEN FACTORY RESPONSE ===")
        print(f"Reply:             {reply}")
        print(f"Time Taken:        {elapsed_time:.2f} seconds")
        print(f"Completion Tokens: {completion_tokens}")
        print("==================================")
        print("SUCCESS: AMD Token Factory is working properly!")

    except Exception as e:
        print("ERROR: Failed to connect or receive response from AMD Token Factory.")
        print(f"Full Error Details:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

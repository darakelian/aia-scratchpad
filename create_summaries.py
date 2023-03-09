import os
import sys
from argparse import ArgumentParser

import httpx
import openai
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from dvids_apps.helpers import path
from dvids_apps.models.db_models import Product


SM_API_KEY = os.environ.get('SM_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')


def summarize_product(product: Product) -> str:
    body_text = product.body.replace("\r\n", "\n")
    with httpx.Client() as client:
        resp = client.post(f"https://api.smmry.com?SM_API_KEY={SM_API_KEY}",
                           data={'sm_api_input': body_text}, timeout=30).json()
        return resp["sm_api_content"]


def gpt_summarize_product(product: Product, model_type: str) -> str:
    completion = openai.Completion.create(
        model=model_type,
        prompt=f"Summarize the following article in 5-7 sentences with more sentences being preferred: {product.body}",
        max_tokens=3000,
        temperature=0.2
    )
    return '\n'.join([choice.text for choice in completion.choices])


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument("--db-path", type=path, help="Path to database", required=True)
    parser.add_argument("--model-type", type=str, help="OpenAI model to use. Default=%(default)s",
                        default="text-davinci-003")
    args = parser.parse_args()
    if SM_API_KEY is None:
        print("Error: must set the environment variable SM_API_KEY", file=sys.stderr)
        return 1
    if OPENAI_API_KEY is None:
        print("Error: must set the environment variable OPENAI_API_KEY", file=sys.stderr)
        return 1
    openai.api_key = OPENAI_API_KEY
    # Connect to database
    engine = create_engine(f"sqlite:///{args.db_path}")
    session = sessionmaker(bind=engine)

    with session() as session:
        # Retrieve N articles
        for product in session.query(Product).filter(text("length(body)>=2000 and length(body)<=3000"))[0:20]:
            # Create summaries with SMMRY
            golden_summary = summarize_product(product)
            # Send articles to GPT
            gpt_summary = gpt_summarize_product(product, args.model_type)
            print(golden_summary)
            print(gpt_summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())

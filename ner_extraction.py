import sys
from argparse import ArgumentParser

import openai
import spacy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from dvids_apps.helpers import path
from dvids_apps.models.db_models import Product


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument("--db-path", type=path, help="Path to database", required=True)
    args = parser.parse_args()
    nlp = spacy.load("en_core_web_lg")
    engine = create_engine(f"sqlite:///{args.db_path}")
    session = sessionmaker(bind=engine)

    with session() as session:
        # Retrieve N articles
        for product in session.query(Product).filter(Product.body.is_not(None))[0:10]:
            product_doc = nlp(product.description)
            spacy_ner_values = set()
            for word in product_doc.ents:
                if word.label_ != "CARDINAL":
                    spacy_ner_values.add(word.text)
            # Use GPT to get a list
            gpt_ner_values = set()
            completion = openai.Completion.create(
                model='text-davinci-003',
                prompt=f"Provide a list of all named entities separated by semi-colons in the following text: {product.description}",
                max_tokens=3000,
                temperature=0.2
            )
            for entity in completion.choices[0].text.split(';'):
                gpt_ner_values.add(entity.strip())
            not_in_spacy = gpt_ner_values - spacy_ner_values
            not_in_gpt = spacy_ner_values - gpt_ner_values
            num_spacy = len(spacy_ner_values)
            num_gpt = len(gpt_ner_values)
            print(spacy_ner_values)
            print(gpt_ner_values)
            print(f"Spacy found {num_spacy} entities, GPT found {num_gpt}, not_in_spacy {not_in_spacy}, not_in_gpt {not_in_gpt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

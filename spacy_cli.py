import argparse

import spacy
import sys

from spacy.lang.en.stop_words import STOP_WORDS


def main() -> int:
    parser = argparse.ArgumentParser()

    nlp = spacy.load("en")
    return 0


if __name__ == "__main__":
    sys.exit(main())

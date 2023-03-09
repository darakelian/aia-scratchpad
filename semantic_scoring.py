import argparse
import sys
from statistics import median, mean, stdev
from pathlib import Path

import spacy

from dvids_apps.helpers import path


def load_sentence_pairs(sentence_pair_filepath: Path) -> list[tuple[str, str]]:
    with open(sentence_pair_filepath, encoding="utf-8") as file:
        lines = [line.strip() for line in file.readlines() if line != "\n"]
        return [(lines[i], lines[i + 1]) for i in range(0, len(lines) - 1, 2)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sentence-pairs", type=path, help="Path to file containing summary sentence pairs (each "
                                                            "pair will be separated by a newline, first sentence "
                                                            "should be smmry, second gpt)")
    args = parser.parse_args()
    nlp = spacy.load("en_core_web_lg")
    sentence_pairs = load_sentence_pairs(args.sentence_pairs)
    similarity_scores: list[float] = []
    for smmry_summary, gpt_summary in sentence_pairs:
        smmry_doc = nlp(smmry_summary)
        gpt_doc = nlp(gpt_summary)
        similarity_scores.append(smmry_doc.similarity(gpt_doc))
    print(similarity_scores)
    print(len(similarity_scores))
    score_mean = mean(similarity_scores)
    score_median = median(similarity_scores)
    score_stdev = stdev(similarity_scores)
    print(f"mean: {score_mean}, median: {score_median}, stdev: {score_stdev}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

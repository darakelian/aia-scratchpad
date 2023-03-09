#!/usr/bin/env python
import os
import pathlib

import openai
import sys
from argparse import ArgumentParser

from dvids_apps.helpers import eprint

DEFAULT_PROMPTS = {
    'names': 'Provide a list of every person mentioned in the following paragraphs',
    'dates': 'Provide a list of dates mentioned in the following paragraphs'
}


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument("--type", type=str, help="Type of prompt to use",
                        choices=["names", "dates", "custom"], required=True)
    parser.add_argument("--prompt", type=str, help="Custom prompt to use for sending to GPT model")
    parser.add_argument("--input", type=str, help="Input for the model. Can either be a file name or raw string",
                        required=True)
    parser.add_argument("--api-key", type=str,
                        help="API key for OpenAI. Script defaults to os.environ['OPENAI_API_KEY']")
    parser.add_argument("--model-type", type=str, help="Name of OpenAI model to use. Default=%(default)s",
                        default="text-curie-001")
    parser.add_argument("--dry-run", action="store_true",
                        help="Flag enabling dry-run mode (no requests will be made to the API)")
    args = parser.parse_args()
    api_key = os.environ.get('OPENAI_API_KEY', args.api_key)
    if not api_key:
        eprint("Error: no API key specified (did you forget to set OPENAI_API_KEY or --api-key?)")
        return 1
    prompt_prefix = DEFAULT_PROMPTS.get(args.type, args.prompt)
    if not prompt_prefix:
        eprint("Error: custom prompt was specified but no prompt was given, must specify --prompt if --type is custom")
        return 1
    input_file = pathlib.Path(args.input)
    if input_file.exists():
        # Assume that this is a file
        with open(input_file) as f:
            lines = f.readlines()
            prompt = '\n'.join([line.replace('\n\r', '').strip('\n') for line in lines])
    else:
        prompt = args.input
    full_prompt = prompt_prefix + "\n" + prompt.strip('\n')
    if args.dry_run:
        print(full_prompt)
        return 0
    openai.api_key = api_key
    x = openai.Completion.create(
        model=args.model_type,
        prompt=full_prompt,
        max_tokens=1024,
        temperature=0.2
    )
    for choice in x.choices:
        print(choice.text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

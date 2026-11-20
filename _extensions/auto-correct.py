# Improve copywriting, correct spaces, words, and punctuations between CJK and English with AutoCorrect

# Copyright: © 2024–Present Tom Ben
# License: MIT License

import autocorrect_py as autocorrect
import json
import panflute as pf


def load_config():
    # yaml-language-server: $schema=https://huacnlee.github.io/autocorrect/schema.json
    config = {
        # 0 - off, 1 - error, 2 - warning
        "rules": {
            # Add space between some punctuations
            "space-punctuation": 0,
            # Add space between brackets (), [] when near the CJK
            "space-bracket": 0,
            # Add space between ``, when near the CJK
            "space-backticks": 0,
            # Add space between dash `-`
            "space-dash": 0,
            # Convert to fullwidth
            "fullwidth": 0,
            # To remove space arouned the fullwidth quotes “”, ‘’
            "no-space-fullwidth-quote": 0,
            # Fullwidth alphanumeric characters to halfwidth
            "halfwidth-word": 1,
            # Fullwidth punctuations to halfwidth in English
            "halfwidth-punctuation": 1,
            # Spellcheck
            "spellcheck": 0
        }
    }
    config_str = json.dumps(config)
    # load_config 运行时存在，但包的 __init__.pyi 存根漏声明
    autocorrect.load_config(config_str)  # pyright: ignore[reportAttributeAccessIssue]


def correct_text(elem, doc):
    if isinstance(elem, pf.Str):
        # Apply autocorrect formatting to each text node
        corrected_text = autocorrect.format(elem.text)
        return pf.Str(corrected_text)


def main(doc=None):
    # Load autocorrect configuration
    load_config()
    return pf.run_filter(correct_text, doc=doc)


if __name__ == "__main__":
    main()

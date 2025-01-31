from openai import OpenAI
from autophenotype.prompts import (
    EXTRACTOR_SYSTEM,
    EXTRACTOR_USER,
    SELECTOR_SYSTEM,
    SELECTOR_USER,
)
from dotenv import load_dotenv
import os
import json

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chat(messages):

    return openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={"type": "json_object"},
    )


def extractor(clinical_case):

    messages = [
        {"role": "system", "content": EXTRACTOR_SYSTEM},
        {"role": "user", "content": EXTRACTOR_USER.format(clinical_case=clinical_case)},
    ]

    return json.loads(chat(messages).choices[0].message.content)


def selector(database_response, symptom):

    messages = [
        {"role": "system", "content": SELECTOR_SYSTEM},
        {
            "role": "user",
            "content": SELECTOR_USER.format(
                database_response=database_response, symptom=symptom
            ),
        },
    ]

    return json.loads(chat(messages).choices[0].message.content)

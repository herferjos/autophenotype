from .model import extractor, selector
from .database import search_database
import pandas as pd
import concurrent.futures


def get_phenotypes(description):
    # Extract symptoms from the clinical description
    dictionary = extractor(description)
    english_symptoms_list = dictionary["symptoms_english"]
    original_symptoms_list = dictionary["original_symptoms"]

    def process_symptom(symptom_en, symptom_original):
        # Select the correct symptom based on the search results
        symptom_dict = selector(search_database(symptom_en), symptom_original)
        symptom_code = symptom_dict["ID"]
        symptom_name = symptom_dict["Name"]
        return symptom_code, symptom_name

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(
            executor.map(
                lambda args: process_symptom(*args),
                zip(english_symptoms_list, original_symptoms_list),
            )
        )

    symptom_code_list, symptom_name_list = zip(*results)

    # Create a DataFrame to organize the symptoms
    df = pd.DataFrame(
        {
            "Original Symptom": original_symptoms_list,
            "ID": symptom_code_list,
            "ID Name": symptom_name_list,
        }
    )
    df["Original Symptom"] = df["Original Symptom"].str.capitalize()
    return df

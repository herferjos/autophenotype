# 🌟 Symptom Phenotyping

This repository contains the code necessary to phenotype symptoms from a clinical description. It uses artificial intelligence to extract symptoms and a trained embedding model to perform searches in a database. Finally, another AI selects the most appropriate symptom for each case and returns a DataFrame with the results.

## 📦 Installation

To install the necessary dependencies, make sure you have `pip` installed and run:

1. **Clone the repository** to your local machine:

   ```bash
   git clone https://github.com/herferjos/autophenotype.git
   cd autophenotype
   ```

2. **Install the required packages**:

   ```bash
   pip install -r requirements.txt
   ```

## 🛠️ Usage

You can use the symptom phenotyping functionality in two ways:

1. **🔧 Importing the function in your code:**

   You can import the `get_phenotypes` function from the `autophenotype` module:

   ```python
   from autophenotype import get_phenotypes

   results = get_phenotypes("Clinical description here")
   ```

   Make sure to replace `"Clinical description here"` with the actual description you want to analyze.

2. **🌐 Using the Streamlit application:**

   If you prefer to use the user interface, you can run the Streamlit application with the following command:

   ```bash
   streamlit run app.py
   ```

   This will open a browser window where you can enter the clinical description and see the results interactively.

## 📁 Project Structure

- `autophenotype/`: Contains the source code for symptom extraction and the AI model.
- `app.py`: Main file to run the Streamlit application.
- `.gitignore`: Files and directories that should be ignored by Git.
- `.env`: Environment variables necessary for project configuration.

## 🤝 Contributions

Contributions are welcome! If you would like to contribute, please open an issue or submit a pull request.
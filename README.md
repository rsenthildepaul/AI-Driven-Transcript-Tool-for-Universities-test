

```markdown
# 🎓 AI Transcript Extraction Assistant

A **Streamlit-based web application** powered by **Google Gemini AI** for automatically extracting, cleaning, and structuring student transcript data from **PDFs or image files**.  
Built to support transcript evaluation workflows (like at DePaul University) and simplify integration with systems such as **TES (CollegeSource)** or **Campus Connect**.

---

## 🚀 Features

- 🧾 **Upload and Process PDFs or Images**
  - Automatically extract all course records (Year, Term, Subject, Code, Title, Units, Grade).
  - Works for single or multiple transcript files.
  
- 🔒 **Sensitive Information Redaction**
  - Automatically redacts SSNs and other identifiable fields (e.g., `XXX-XXXXXX`).

- 🧠 **AI-Powered Extraction**
  - Uses **Google Gemini** (configurable models: `gemini-2.0-flash`, `gemini-2.5-pro`, etc.)
  - Custom prompts for consistent, structured tabular output.

- 🏫 **University Mapping**
  - Reads `EXT_ORG_IDs.xlsx` to link transcript data with university metadata:
    - **Org ID**
    - **City**
    - **State**

- 📊 **CSV Export**
  - Automatically converts AI responses to a downloadable `.csv`.
  - Cleans Markdown tables and parses them into structured DataFrames.

- 🖼️ **Dual Media Mode**
  - Supports **PDF text extraction** and **image uploads** (for scanned transcripts).

---

## 🏗️ Project Structure

```
```
gemini_transcript_app/
│
├── app.py                     # Main Streamlit application
├── EXT_ORG_IDs.xlsx           # University metadata (Org ID, City, State)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (API keys)
├── README.md                  # This file
└── data/                      # Optional folder for testing transcripts
```

````

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/ai-transcript-extraction.git
cd ai-transcript-extraction
````

### 2️⃣ Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # (macOS/Linux)
.venv\Scripts\activate      # (Windows)
```

### 3️⃣ Install Requirements

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables

Create a `.env` file in the project root:

```
GOOGLE_API_KEY_NEW=your_google_api_key_here
```

---

## 🧩 Run the App

```bash
streamlit run app.py
```

Then open your browser at:
👉 [http://localhost:8501](http://localhost:8501)

---

## 🧰 Configuration Options

### 🔹 Model Settings (in sidebar)

* **Model:** Choose between `gemini-2.0-flash`, `gemini-2.5-pro`, etc.
* **Temperature:** Controls creativity vs. precision.
* **Top P:** Controls diversity in sampling.
* **Max Tokens:** Sets output length.

### 🔹 Prompts

* **Default Prompt:**
  Extracts course rows in `Year | Term | Subject | Code | Title | Units | Grade` format.
* **Special Prompt:**
  Adjusts parsing for schools like *Waubonsee Community College* (`102.981 → 102`).

---

## 🧾 Example Output

| Year | Term   | Subject | Code    | Title                     | Units | Grade |
| ---- | ------ | ------- | ------- | ------------------------- | ----- | ----- |
| 2022 | Spring | HUM     | 102.981 | The Global Village        | 3.00  | A     |
| 2022 | Fall   | AST     | 100.921 | Introduction to Astronomy | 3.00  | A     |
| 2023 | Spring | ENG     | 101.062 | First-Year Composition I  | 3.00  | A     |

---

## 🛡️ Error Handling

* Handles **missing university data** gracefully.
* Automatically retries image uploads if Gemini is still processing.
* Cleans malformed AI output (Markdown → CSV).

---

## 🧠 Powered By

* [Streamlit](https://streamlit.io/) – UI Framework
* [Google Gemini API](https://ai.google.dev/) – Generative AI for text extraction
* [PyPDF](https://pypi.org/project/pypdf/) – PDF text extraction
* [Pandas](https://pandas.pydata.org/) – Data wrangling & CSV export

---

## 📈 Roadmap

* [ ] Add support for **direct TES API upload**
* [ ] Improve **table recognition** for scanned PDFs
* [ ] Add **database (SQLite/PostgreSQL)** backend for student-level history
* [ ] Support **batch mode** extraction with progress tracking

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes and open a PR

---

## 🧾 License

MIT License © 2025 Rakul Senthilkumar

---

## 💬 Contact

For questions or collaboration:
**Rakul Senthilkumar**
📧 [rakulsenthilkumar@gmail.com](mailto:rakulsenthilkumar@gmail.com)
🔗 [LinkedIn](https://linkedin.com/in/rakulsenthilkumar)


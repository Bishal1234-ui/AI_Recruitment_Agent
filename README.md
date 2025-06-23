
# 🤖 AI Recruitment Agent

An intelligent recruitment assistant that automates resume screening using a local LLM via **Ollama** and offers both CLI and web-based interaction.

<p align="center">
  <img src="https://img.shields.io/badge/LLM-Gemma%204b-blueviolet?style=for-the-badge&logo=OpenAI&logoColor=white"/>
  <img src="https://img.shields.io/badge/Framework-LangChain-green?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Local%20LLM-Ollama-4B0082?style=for-the-badge&logoColor=white"/>
  <img src="https://img.shields.io/badge/Framework-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=black"/>
  <img src="https://img.shields.io/badge/Vector%20DB-FAISS-0044CC?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
</p>

---

## ✨ Features

- ⚡ **AI-Powered Analysis**: Leverages **Gemma 3:4b** via Ollama for deep resume-job fit evaluation.
- 📊 **Vector-Based Context Matching**: Uses **FAISS** to store and retrieve job description vectors.
- 📦 **Structured Output**: LLM output is parsed into JSON for decision, compatibility score, and justification.
- 💾 **Persistent Storage**: Stores all results in an **SQLite** database for audit and analysis.
- 🧰 **Dual Interface**: Available as a **CLI tool** or through a **React + FastAPI web UI**.

---

## 🧠 How It Works

1. **📥 Job Description Embedding**
   - Converts job text into vectors using `nomic-embed-text` via `OllamaEmbeddings`
   - Stored in **FAISS** for fast retrieval

2. **📄 Resume Parsing**
   - Extracts text from uploaded **PDF** resumes using `PyPDF`.

3. **🔍 AI Analysis via LangChain**
   - Uses:
     - 🔁 **Retriever** (FAISS)
     - 🧠 **LLM**: `gemma3:4b` via Ollama
     - ✏️ **Prompt Template** with strict rules
     - 📦 **PydanticOutputParser** for structured JSON

4. **💾 Store Results**
   - Data is persisted in `recruitment_results.db` via a custom database function.

---

## 🧰 Tech Stack

| Category    | Tools |
|-------------|-------|
| 💡 **AI/LLM** | `LangChain`, `Gemma`, `Ollama`, `nomic-embed-text` |
| ⚙️ **Backend** | `FastAPI`, `pydantic`, `faiss-cpu`, `PyPDF` |
| 🖥️ **Frontend** | `React`, `Vite`, `TailwindCSS` (optional) |
| 🛢️ **Database** | `SQLite` |
| 🧠 **Vector DB** | `FAISS` |
| 📦 **Package Managers** | `pip`, `npm` |

---

## 🚀 Getting Started

### ✅ Prerequisites

- Python `3.9+`
- Node.js & npm
- [Ollama](https://ollama.com/) installed and running

---

### ⚙️ Setup Guide

#### 🔹 Pull LLM and Embed Models

```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

#### 🔹 Backend Setup

```bash
cd MainAPI
# Create this requirements.txt file:
```

<details>
<summary>📄 MainAPI/requirements.txt</summary>

```txt
fastapi
uvicorn[standard]
langchain
langchain-community
langchain-ollama
pydantic
pypdf
faiss-cpu
python-dotenv
python-multipart
```

</details>

```bash
pip install -r requirements.txt
```

#### 🔹 Frontend Setup (Optional)

```bash
cd frontend-react
npm install
```

---

## 🧪 Usage

### 💻 Command-Line Mode

```bash
python recruitmentagent.py
```

Follow the prompts to upload a resume and see results in the console.

---

### 🌐 Web Interface Mode

#### 1. Start the Backend API

```bash
cd MainAPI
uvicorn main:app --reload
```

API accessible at `http://127.0.0.1:8000`

#### 2. Start the React Frontend

```bash
cd frontend-react
npm run dev
```

Open `http://localhost:5173` in your browser.

---


## 🧑‍💼 Use Case

Perfect for **HR teams**, **recruitment firms**, or **tech hiring platforms** looking to automate and scale their screening process with **AI-driven insights**.

---

## 🛠️ Future Improvements

- ✅ Resume ranking
- ✅ Multi-role analysis
- ⏳ Email integration
- ⏳ Feedback loop learning

---

## 📬 Contact

For collaboration or questions, feel free to reach out!

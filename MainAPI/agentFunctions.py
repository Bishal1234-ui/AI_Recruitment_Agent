from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings
from pypdf import PdfReader
from pydantic import BaseModel, Field
import os

# ollama server
OLLAMA_SERVER = "http://localhost:11434"

# ---------- Pydantic Schema ----------
class AnalysisResultFormat(BaseModel):
    decision: str = Field(description="SELECTED or REJECTED")
    compatibility_score: int = Field(description="Score from 0 to 100")
    justification: str = Field(description="Justification in 4 sentences")


def create_vector_store_job_details(job_text: str):
    embeddings = OllamaEmbeddings(model="nomic-embed-text:latest", base_url=OLLAMA_SERVER)
    documents = [Document(page_content=job_text)]
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store

def get_resume_text(resume_path: str) -> str:
    reader = PdfReader(resume_path)
    return "\n".join([page.extract_text() for page in reader.pages])

def decision_maker_chain(vector_store):
    llm = ChatOllama(model="gemma3:4b", base_url=OLLAMA_SERVER)
    retriever = vector_store.as_retriever()
    parser = PydanticOutputParser(pydantic_object=AnalysisResultFormat)

    prompt_template = """
    You are an expert and very strict AI Recruitment Agent. Your task is to analyze a candidate's resume against a specific job description.

    Here is the relevant context from the job description:
    {context}

    Here is the candidate's resume:
    {resume_text}

    **Evaluation Rules (Follow these strictly):**
    1.  **Mandatory Requirements Check**: The candidate MUST meet the requirements specified in the job description. If they do not meet the requirements, they must be 'REJECTED' regardless of other factors.
    2.  **Skills Check**: The candidate MUST possess at least half of the skills listed in the job description. If they do not, they must be 'REJECTED'.
    3.  **Scoring and Final Decision**:
        - If the candidate fails the Mandatory Requirements or Skills Check, the decision is 'REJECTED'.
        - If the candidate passes both checks, evaluate their overall profile (experience, projects, etc.) to assign a compatibility score from 0 to 100.
        - A candidate is 'SELECTED' only if they pass both checks AND their compatibility score is 80 or higher. Otherwise, they are 'REJECTED'.
    4. **Project**: Candidate must have atleast two projects that are matching the tech skill requirements.

    **Your Tasks:**
    1.  Provide a decision: 'SELECTED' or 'REJECTED'.
    2.  Provide a compatibility score (0-100).
    3.  Provide a concise, professional justification for your decision in four sentences, explaining how you applied the rules.
    
    {format_instructions}
    """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "resume_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    return (
        {"context": retriever, "resume_text": RunnablePassthrough()}
        | prompt
        | llm
        | parser
    )
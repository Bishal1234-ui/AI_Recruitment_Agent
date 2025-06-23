# 1. Initial setup
import os
import sqlite3
from dotenv import load_dotenv
from pypdf import PdfReader
from pydantic import BaseModel, Field

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings

# Load environment variables from .env file
load_dotenv()
OLLAMA_SERVER = "http://localhost:11434"


# 2. HR JOB DETAILS FUNCTION TO EMBED THE DETAILS AND STORE IN VECTOR FORM
def create_vector_store_job_details(job_text):
    """
    Creates a FAISS vector store from the job description text.
    """
    embeddings = OllamaEmbeddings(model="nomic-embed-text:latest", base_url=OLLAMA_SERVER)
    documents = [Document(page_content=job_text)]
    vector_store = FAISS.from_documents(documents, embeddings)
    print("Job description processed and stored in vector store.")
    return vector_store


# 3. Student Details and resume
def get_resume_text(resume_path):
    """
    Extracts text from a PDF resume file.
    """
    reader = PdfReader(resume_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


# 4. Create the main analysis chain
# Pydantic model for structured output
class AnalysisResultFormat(BaseModel):
    decision: str = Field(description="The decision, either 'SELECTED' or 'REJECTED'")
    compatibility_score: int = Field(description="The compatibility score from 0 to 100.")
    justification: str = Field(description="The justification for the decision.")


def decision_maker_chain(vector_store):
    """
    Creates a LangChain chain to analyze a resume against a job description.
    """
    # Initialize the LLM
    llm = ChatOllama(model="gemma3:4b", base_url=OLLAMA_SERVER)
    
    # Retrieve data from vector store
    retriever = vector_store.as_retriever()
    
    # Set up the Pydantic parser for structured output
    parser = PydanticOutputParser(pydantic_object=AnalysisResultFormat)

    prompt_template = """
    You are an expert AI Recruitment Agent. Your task is to analyze a candidate's resume against a specific job description.

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

    # Define the processing chain
    chain = (
        {"context": retriever, "resume_text": RunnablePassthrough()}
        | prompt
        | llm
        | parser
    )

    return chain


# 5. Save candidate info and result to database
def save_result_to_db(candidate_name, candidate_email, resume_path, decision, compatibility_score, justification):
    """
    Saves the analysis result to an SQLite database.
    """
    conn = sqlite3.connect("recruitment_results.db")
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT,
            candidate_email TEXT,
            resume_path TEXT,
            decision TEXT,
            compatibility_score INTEGER,
            justification TEXT
        )
    """)
    
    # Insert the new result
    cursor.execute("""
        INSERT INTO results (candidate_name, candidate_email, resume_path, decision, compatibility_score, justification)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (candidate_name, candidate_email, resume_path, decision, compatibility_score, justification))
    
    conn.commit()
    conn.close()


# 6. Run the main function to start the agent
def main():
    """
    The main function to run the recruitment agent.
    """
    # --- HR INPUT SECTION ---
    job_title = "Tecnician"
    job_details = "We are looking for Embedded system technician."
    requirements = "Must have compulsory skills on vlsi and embedded systems. Must have knowledge of x64 architecture"
    experience = "0-1 years of experience."
    skills = "x64, embedded systems, matlab,C#"

    # Combine job details into a single text block
    job_text = (
        f"job_title: {job_title}\n"
        f"job_details: {job_details}\n"
        f"requirements: {requirements}\n"
        f"experience: {experience}\n"
        f"skills: {skills}"
    )

    # --- Candidate Application Section ---
    print("\n--- Please provide the candidate details ---")
    candidate_name = input("Candidate Name: ")
    candidate_email = input("Candidate Email: ")
    resume_path = input("Path to Resume PDF: ")

    # Validate resume path
    while not os.path.exists(resume_path):
        print("Error: The specified resume file does not exist.")
        resume_path = input("Please enter a valid path to the Resume PDF: ")


    print("\n--- Starting AI Recruitment Agent ---")

    # Step 1: Create vector store from job description
    vector_store = create_vector_store_job_details(job_text)
    
    # Step 2: Extract text from the candidate's resume
    try:
        resume_text = get_resume_text(resume_path)
    except Exception as e:
        print(f"Error reading resume file: {e}")
        return
    
    # Step 3: Create the analysis chain
    analysis_chain = decision_maker_chain(vector_store)

    # Step 4: Invoke the chain to get the analysis result
    result = analysis_chain.invoke(resume_text)
    decision = result.decision
    compatibility_score = result.compatibility_score
    justification = result.justification

    # Step 5: Save the result to the database
    save_result_to_db(candidate_name, candidate_email, resume_path, decision, compatibility_score, justification)

    # --- Display Results ---
    print("\n--- Analysis Complete ---")
    print(f"Decision: {decision}")
    print(f"Compatibility Score: {compatibility_score}")
    print(f"Justification:\n{justification}")


if __name__ == "__main__":
    main()
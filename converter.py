import pdfplumber
from bs4 import BeautifulSoup
import markdown
import os
import math
from openai import OpenAI
import json
import random

# ----------------------------
# 1. Extract text from manuals
# ----------------------------
def extract_text(file_path):
    if file_path.endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif file_path.endswith('.html'):
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            return soup.get_text(separator='\n')
    elif file_path.endswith('.md'):
        with open(file_path, 'r', encoding='utf-8') as f:
            html = markdown.markdown(f.read())
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator='\n')
    else:
        raise ValueError("Unsupported file type: " + file_path)

# ----------------------------
# 2. Split text into chunks
# ----------------------------
def split_text(text, chunk_size=1000, overlap=100):
    """
    Splits text into overlapping chunks of chunk_size characters.
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # move start forward, keep overlap
    
    return chunks

# ----------------------------
# 3. Extract policies using OpenAI LLM
# ----------------------------
def extract_policies_from_chunk(chunk_text, client):
    prompt = f"""
Extract configuration policies from the following text. 
For each policy, provide:
- policy_id (number)
- description
- target_config
- expected_value
- notes

Text:
{chunk_text}
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def extract_policies_from_chunk_mock(chunk_text):
    """
    Simulates LLM output for testing.
    Returns a JSON string with random or example policies.
    """
    # Example fixed policies for testing
    mock_policies = [
        {
            "policy_id": 1,
            "description": "SSH root login must be disabled",
            "target_config": "sshd_config PermitRootLogin",
            "expected_value": "no",
            "notes": "Test policy extracted"
        },
        {
            "policy_id": 2,
            "description": "Password authentication must be disabled",
            "target_config": "sshd_config PasswordAuthentication",
            "expected_value": "no",
            "notes": ""
        }
    ]
    
    # Optionally, randomly pick 1-2 policies for variety
    selected = random.sample(mock_policies, k=random.randint(1, 2))
    
    return json.dumps(selected)

# ----------------------------
# 4. Parse LLM output as JSON
# ----------------------------
def parse_llm_output(output_text):
    try:
        policies = json.loads(output_text)
        return policies
    except json.JSONDecodeError:
        print("Warning: Could not parse JSON. Returning empty list.")
        return []

# ----------------------------
# 5. Process all manuals
# ----------------------------
def process_manuals(manual_folder, client):
    all_policies = []
    
    for filename in os.listdir(manual_folder):
        file_path = os.path.join(manual_folder, filename)
        print(f"Processing {filename}...")
        
        try:
            text = extract_text(file_path)
            chunks = split_text(text, chunk_size=1000, overlap=100)
            
            for chunk in chunks:
                # llm_output = extract_policies_from_chunk(chunk, client)
                llm_output = extract_policies_from_chunk_mock(chunk)
                structured = parse_llm_output(llm_output)
                all_policies.extend(structured)
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    # Save structured policies to JSON
    with open('structured_policies.json', 'w') as f:
        json.dump(all_policies, f, indent=2)
    
    print(f"Extraction complete! {len(all_policies)} policies saved.")
    return all_policies

# ----------------------------
# 6. Example usage
# ----------------------------
if __name__ == "__main__":
    import os
    openai_api_key = os.getenv("OPENAI_API_KEY")  # make sure your API key is set
    client = OpenAI(api_key=openai_api_key)
    
    manual_folder = "./manuals"  # put PDFs/HTML/Markdown here
    policies = process_manuals(manual_folder, client)

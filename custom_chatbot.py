import json
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
from huggingface_hub import InferenceClient

# =============================
# Load API Key
# =============================
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
client = InferenceClient(HF_TOKEN)

# =============================
# Load Q&A Dataset
# =============================
qa_file = "custom_qa.json"

if not os.path.exists(qa_file):
    raise FileNotFoundError(f"{qa_file} not found! Please create it in your project folder.")

with open(qa_file, "r") as f:
    qa_data = json.load(f)

# =============================
# Initialize Sentence Transformer
# =============================
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

# ✅ Precompute embeddings for all questions
qa_embeddings = embed_model.encode([item["question"] for item in qa_data], convert_to_tensor=True)

# =============================
# Function to Get Answer
# =============================
def get_answer(user_question):
    """
    Returns the chatbot's answer to a user question using:
    1. Precomputed embeddings for similarity search
    2. Granite/GPT-Neo model via Hugging Face API for natural responses
    """
    # 1️⃣ Encode user question
    user_emb = embed_model.encode(user_question, convert_to_tensor=True)

    # 2️⃣ Compute similarity with preloaded embeddings
    similarities = util.cos_sim(user_emb, qa_embeddings)[0]
    best_idx = int(similarities.argmax().item())
    matched_answer = qa_data[best_idx]["answer"]

    # 3️⃣ Prepare prompt for Granite/GPT-Neo
    prompt = f"Answer the user question based on this info:\n{matched_answer}\nQ: {user_question}\nA:"

    # 4️⃣ Call Hugging Face API
    response = client.text_generation(
        model="EleutherAI/gpt-neo-1.3B",   # Granite/GPT-Neo model
        inputs=prompt,
        parameters={
            "max_new_tokens": 150,
            "temperature": 0.7,
            "top_p": 0.9
        }
    )

    # 5️⃣ Return refined answer
    return response[0]["generated_text"].split("A:")[-1].strip()

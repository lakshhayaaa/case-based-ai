import ollama

def generate_answer(query, chunks):

    context = "\n\n".join(chunks)

    prompt = f"""
Use ONLY the context below.
Do not use outside knowledge.
If the answer is not in the context say:
"The answer is not available in the provided context."

Context:
{context}

Question:
{query}
"""

    response = ollama.chat(
        model="llama3:8b",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]
import ollama

response = ollama.chat(
    model="qwen2.5:3b",
    messages=[
        {
            "role": "user",
            "content": "Explain what a resume is in one simple sentence."
        }
    ]
)

print(response["message"]["content"])
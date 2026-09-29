import os
import json
import faiss
from sentence_transformers import SentenceTransformer

# Caminhos locais
input_dir = "../docs/books"
output_dir = "../docs/books/faiss"
os.makedirs(output_dir, exist_ok=True)

# Modelo de embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# Gerar FAISS para cada ficheiro _books.json
for filename in os.listdir(input_dir):
    if filename.endswith("_books.json"):
        input_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]

        with open(input_path, "r", encoding="utf-8") as f:
            books = json.load(f)

        texts = [f"{book['title']}. {book.get('author', '')}" for book in books if 'title' in book]

        if not texts:
            print(f"Nenhum texto válido em {filename}")
            continue

        embeddings = model.encode(texts, convert_to_numpy=True)
        dim = embeddings.shape[1]

        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)

        faiss.write_index(index, os.path.join(output_dir, f"{base_name}.faiss"))
        with open(os.path.join(output_dir, f"{base_name}_texts.json"), "w", encoding="utf-8") as f:
            json.dump(texts, f, ensure_ascii=False, indent=2)

        print(f"✅ Guardado: {base_name}.faiss e {base_name}_texts.json")

print("🏁 Todos os índices FAISS foram gerados.")

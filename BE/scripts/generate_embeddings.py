from sentence_transformers import SentenceTransformer
import faiss
import json
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

input_dir = "docs"
output_dir = "docs/faiss"
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.endswith(".json") and not filename.endswith("_texts.json"):
        input_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]

        print(f"🔄 A processar: {input_path}")
        with open(input_path, "r", encoding="utf-8") as f:
            try:
                docs = json.load(f)
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao ler {filename}: {e}")
                continue

        if not isinstance(docs, list):
            print(f"⚠️  Formato inesperado em {filename}. Esperado: lista de dicionários.")
            continue

        texts = [doc.get("text", "") for doc in docs if "text" in doc]
        if not texts:
            print(f"⚠️  Nenhum campo 'text' encontrado em {filename}")
            continue

        print(f"📝 {len(texts)} textos encontrados.")

        embeddings = model.encode(texts, convert_to_numpy=True)

        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)

        faiss.write_index(index, os.path.join(output_dir, f"{base_name}.faiss"))
        with open(os.path.join(output_dir, f"{base_name}_texts.json"), "w", encoding="utf-8") as f:
            json.dump(texts, f, ensure_ascii=False, indent=2)

        print(f"✅ Embeddings e textos guardados para: {base_name}")


print("🏁 Fim do processo. Todos os ficheiros foram processados.")

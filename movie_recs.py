import pymongo
import requests
import time

# Conexão com MongoDB
client = pymongo.MongoClient(
    "mongodb+srv://beau:bngeFBqJJoEWqRNd@cluster0.svcxhgj.mongodb.net/?retryWrites=true&w=majority")
db = client.sample_mflix
collection = db.movies

# API Hugging Face
hf_token = "Your Token"
embedding_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"


def generate_embedding(text: str) -> list[float]:
    """Gera embedding via API Hugging Face"""
    response = requests.post(
        embedding_url,
        headers={"Authorization": f"Bearer {hf_token}"},
        json={"inputs": text}
    )

    if response.status_code == 503:
        print("Modelo ainda está carregando... aguardando 10s.")
        time.sleep(10)
        return generate_embedding(text)
    elif response.status_code != 200:
        raise ValueError(f"Erro: {response.status_code} - {response.text}")

    return response.json()[0]  # retorna o vetor de embeddings


# Indexação (descomente quando quiser rodar)
# for doc in collection.find({'plot': {"$exists": True}}).limit(50):
#     try:
#         embedding = generate_embedding(doc['plot'])
#         collection.update_one(
#             {'_id': doc['_id']},
#             {'$set': {'plot_embedding_hf': embedding}}
#         )
#         print(f"Embedding salvo para: {doc['title']}")
#     except Exception as e:
#         print(f"Erro no doc {doc['_id']}: {e}")

# Consulta vetorial
query = "imaginary characters from outer space at war"
query_vector = generate_embedding(query)

results = collection.aggregate([
    {
        "$vectorSearch": {
            "queryVector": query_vector,
            "path": "plot_embedding_hf",
            "numCandidates": 100,
            "limit": 4,
            "index": "PlotSemanticSearch"
        }
    }
])

for doc in results:
    print(f"\n🎬 Movie: {doc['title']}\n📝 Plot: {doc['plot']}\n")

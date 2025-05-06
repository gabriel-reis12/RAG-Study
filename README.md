
# Projeto de Consulta Vetorial com MongoDB e Hugging Face

Este projeto realiza a integração entre o MongoDB e a API da Hugging Face para gerar embeddings a partir dos resumos de filmes e realizar consultas vetoriais para encontrar filmes semelhantes.

## Dependências

Certifique-se de ter as bibliotecas necessárias instaladas:

```bash
pip install pymongo requests
```

## Descrição do Código

### 1. Conexão com o MongoDB

A primeira parte do código realiza a conexão com um banco de dados MongoDB hospedado na nuvem.

```python
client = pymongo.MongoClient(
    "mongodb+srv://beau:bngeFBqJJoEWqRNd@cluster0.svcxhgj.mongodb.net/?retryWrites=true&w=majority")
db = client.sample_mflix
collection = db.movies
```

### 2. API Hugging Face

A API da Hugging Face é usada para gerar embeddings (representações vetoriais) a partir dos textos dos filmes. A função `generate_embedding` envia uma solicitação para a API para obter o embedding de uma string de entrada.

```python
hf_token = "Your Token"
embedding_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
```

### 3. Função `generate_embedding`

A função `generate_embedding` envia um texto para a API da Hugging Face e retorna o embedding correspondente. Caso o modelo ainda não esteja carregado, o código aguarda 10 segundos antes de tentar novamente.

```python
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
```

### 4. Indexação dos Documentos (Comentado)

Para indexar os embeddings, a parte do código abaixo (comentada) percorre os filmes da coleção e salva o embedding de cada resumo de filme no banco de dados MongoDB.

```python
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
```

### 5. Consulta Vetorial

A consulta vetorial é realizada utilizando o vetor de consulta `query_vector`, que é gerado a partir de uma string de consulta. A função `aggregate` do MongoDB é utilizada para realizar a busca vetorial, retornando os documentos mais semelhantes à consulta.

```python
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
    print(f"
🎬 Movie: {doc['title']}
📝 Plot: {doc['plot']}
")
```

## Conclusão

Este código permite gerar embeddings de textos utilizando a API da Hugging Face e realizar consultas vetoriais em uma base de dados MongoDB para encontrar filmes semelhantes com base no enredo.

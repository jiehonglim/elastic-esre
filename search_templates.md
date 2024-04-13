
### BM25
{
    "query": {
      "match": {
        "desc-body": "{{query_string}}"
      }
    },
    "size": "1",
    "_source": [
      "title",
      "url",
      "desc-body"
    ]
}


### Dense Vector search
{
  "knn": {
    "field": "mitre-attack-vector",
    "k": 10,
    "num_candidates": 20,
    "query_vector_builder": {
      "text_embedding": {
        "model_id": "model_id",
        "model_text": "query_string"
      }
    },
    "boost": 24
  },
  "size": "1",
  "_source": [
    "title",
    "url",
    "desc-body"
  ]
}
import streamlit as st
import pandas as pd
from elasticsearch import Elasticsearch

es_username = st.secrets["es_username"]
es_password = st.secrets["es_password"]
es_cloudid = st.secrets["es_cloudid"]

es_index = "search-govtech-dev-docs"

source_fields = ["title", "meta_description", "url"]

logo = "https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt5d10f3a91df97d15/620a9ac8849cd422f315b83d/logo-elastic-vertical-reverse.svg"

es = Elasticsearch(
    cloud_id=es_cloudid,
    basic_auth=(es_username, es_password)
)

st.image(logo, width=100)


search = st.text_input("Enter your semantic search", "what products can I use to monitor my applications")

text_expand_query = {
    "text_expansion":{
        "ml.inference.body_content_expanded.predicted_value":{

            "model_id":".elser_model_1",
            "model_text":search
            }
        }
    }


resp = es.search(index=es_index, source=source_fields ,query=text_expand_query)
print("Got %d Hits:" % resp['hits']['total']['value'])

st.divider()

for hit in resp['hits']['hits']:
    st.write("%(title)s" % hit["_source"])
    st.write("%(meta_description)s" % hit["_source"])
    st.write("%(url)s" % hit["_source"])
    st.divider()


# querybody = {
#     "query" : {
#         "text_expansion":{
#             "ml.inference.body_content_expanded.predicted_value":{

#                 "model_id":".elser_model_1",
#                 "model_text":"what products can I use to monitor my applications"
#                 }
#             }
#         }
# #     }

# querybody = {
#     "text_expansion":{
#         "ml.inference.body_content_expanded.predicted_value":{

#             "model_id":".elser_model_1",
#             "model_text":"what products can I use to monitor my applications"
#             }
#         }
#     }

# resp = es.search(index="search-govtech-dev-docs", query=querybody)

# total_hits = resp['aggregations']['match_count']['value']

# st.write(total_hits)

# st.write("DB password:", st.secrets["es_password"])


# resp = es.search(index="test-index", query={"match_all": {}})
# print("Got %d Hits:" % resp['hits']['total']['value'])
# for hit in resp['hits']['hits']:
#     print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])


# GET search-govtech-dev-docs/_search
# {
#    "_source" : ["title", "meta_description"],
#    "query":{
#       "text_expansion":{
#          "ml.inference.body_content_expanded.predicted_value":{
#             "model_id":".elser_model_1",
#             "model_text":"what products can I use to monitor my applications"
#          }
#       }
#    }
# }
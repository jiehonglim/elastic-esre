import streamlit as st
from elasticsearch import Elasticsearch

es_username = st.secrets["es_username"]
es_password = st.secrets["es_password"]
es_cloudid = st.secrets["es_cloudid"]
es_index = st.secrets["es_index2"]

source_fields = ["title", "headings", "url"]

logo = "https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt5d10f3a91df97d15/620a9ac8849cd422f315b83d/logo-elastic-vertical-reverse.svg"

es = Elasticsearch(
    cloud_id=es_cloudid,
    basic_auth=(es_username, es_password)
)

st.set_page_config(layout="wide")

st.image(logo, width=100)

search = st.text_input("Enter your semantic search", "how can I secure my network?")

bool_query = {
    "bool": {
        "must": [
            {"match": {"body_content": search}},
        ],
    }
},

text_expand_query = {
    "text_expansion":{
        "ml.inference.body_content_expanded.predicted_value":{

            "model_id":".elser_model_1",
            "model_text":search
            }
        }
    }

text_expand_resp = es.search(index=es_index, source=source_fields ,query=text_expand_query)

st.divider()


st.write("Text Expansion Search")
st.write("The text expansion query uses a natural language processing model to convert the query text into a list of token-weight pairs which are then used in a query against a rank features field.")
for hit in text_expand_resp['hits']['hits']:
    st.write("%(title)s" % hit["_source"])
    st.write("%(headings)s" % hit["_source"])
    st.write("%(url)s" % hit["_source"])
    st.divider()
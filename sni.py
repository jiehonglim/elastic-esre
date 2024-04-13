import openai
import streamlit as st
from elasticsearch import Elasticsearch

es_username = st.secrets["es_username"]
es_password = st.secrets["es_password"]
es_cloudid = st.secrets["es_cloudid"]
es_index = st.secrets["es_index2"]

openai_api_key = st.secrets["openai_api_key"]

model_elser = ".elser_model_2_linux-x86_64"
model_dense = ".multilingual-e5-small_linux-x86_64"

fields = ["title", "content", "url"]

def es_connect(cid, user, passwd):
    es = Elasticsearch(cloud_id=cid, basic_auth=(user, passwd))
    return es

def get_bm25_query(query_text):
    return {
            "match": {
                "content": {
                    "query": query_text,
                    "fuzziness": "AUTO"
                    }
                }
            }

def get_knn_query(query_text):
    return {
            "field": "ml.inference.content.predicted_value",
            "k": 50,
            "num_candidates": 100,
            "query_vector_builder": {
                "text_embedding": {
                    "model_id": model_dense,
                    "model_text": query_text
                }
            }
        }

def process_resp(resp):
    if resp['hits']['total']['value'] > 0:
        for results in resp['hits']['hits']:
            st.write(results['_source']['title'])
            # st.caption(results['_source']['content'])
            st.write(results['_source']['url'])
            st.divider()

    else:
        st.write("nothing")    

def process_resp_content(resp):
    if resp['hits']['total']['value'] > 0:
        content = ""
        i = 0
        for results in resp['hits']['hits']:
            
            content = content + "\n\n\n Initiative: " + results['_source']['content']
            
        return content

    else:
        return False  

# Generate and display response on form submission
negResponse = "I'm unable to answer the question based on the information I have from your articles."
openai_keywords = ""

st.set_page_config(layout="wide")

st.title("Smart Nation Initatives Demo")
st.header("💬 Chat with a Smart Nation Assistant")
st.subheader("This is a concept conversational Q/A chatbot using Smart Nation Initatives")
st.write("With refernce to https://www.smartnation.gov.sg/initiatives/strategic-national-projects/")
st.write("🤖 RAG with Elastic + OpenAI LLM")

cid = es_cloudid
cp = es_password
cu = es_username
es = es_connect(cid, cu, cp)
query = ""
openai_keywords = ""
new_keywords = ""
query_2 = ""

with st.expander("Elastic Search, Fuzzy, Vector Search, Hybrid Search"):

    with st.form("search_form"):
        query = st.text_input("Search with Elastic", "How do we improve health outcomes?")
        search_submit_button = st.form_submit_button("Search")

    if search_submit_button:

        tab1, tab2, tab3 = st.tabs(["Fuzzy","Dense Vector","RRF"])

        with tab1:
            try:
                resp = es.search(
                    index=es_index,
                    source=fields,
                    size= 5,
                    query=get_bm25_query(query)
                    )
                process_resp(resp)

            except:
                st.write("No results found")

        with tab2:
            try:
                resp = es.search(
                    index=es_index,
                    source=fields,
                    size=5,
                    knn=get_knn_query(query)
                    )
                process_resp(resp)
            except:
                st.write("No results found")


        with tab3:
            rank = {"rrf": {}}
            try:
                resp = es.search(
                    index=es_index,
                    source=fields,
                    size=5,
                    knn=get_knn_query(query),
                    query=get_bm25_query(query),
                    rank = rank
                    )
                process_resp(resp)
            except:
                st.write("No results found")



openai.api_key = openai_api_key

with st.expander("Prompt Engineering: Generate search keywords"):

    with st.form("chat_form"):
        openai_query = st.text_input("Prompt OpenAI for search keywords", "How do we improve health outcomes?")
        prompt_submit_button = st.form_submit_button("Generate Keywords")
        
        if prompt_submit_button:

            keyword_question = f"""
                    Can you generate three internet search keywords from with this question: {openai_query}\n
                    No special formating, comma or punctuation required.
                    Example: keyword1 keyword2 keyword3
                    """

            keyword_prompt = [
                                {
                                    "role": "assistant", 
                                    "content": "You are a friendly assistant from Singapore Smart Nation Group."
                                },
                                {
                                    "role": "user",
                                    "content": keyword_question
                                }
                            ]

            keyword_response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=keyword_prompt
            )
            openai_keywords = keyword_response.choices[0].message.content
            new_keywords = openai_keywords

            st.write(openai_keywords)


with st.expander("LLM Powered Search"):

    with st.form("search_form_2"):
        query_2 = st.text_input("Search with Elastic, Responses by OpenAI", new_keywords)
        
        search_2_submit_button = st.form_submit_button("Search")

    if search_2_submit_button:
        rank = {"rrf": {}}

        resp = es.search(
            index=es_index,
            source=fields,
            size=5,
            knn=get_knn_query(query_2),
            query=get_bm25_query(query_2),
            rank = rank
            )
        process_resp(resp)
        context = process_resp_content(resp)

        long_question = f"""
                Can you reply the question "{query}" by 
                providing a short summary and suggest which initiatives is the most relevant based on the below list of initatives?\n
                If the answer is not contained in the supplied doc reply '{negResponse}' and nothing else.\n
                \n
                {context}
                \n
                
                """

        prompt_2 = [
                            {
                                "role": "assistant", 
                                "content": "You are a friendly assistant from Singapore Smart Nation Group."
                            },
                            {
                                "role": "user",
                                "content": long_question
                            }
                        ]

        response_2 = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=prompt_2
        )
        openai_responses_2 = response_2.choices[0].message.content

        st.write(openai_responses_2)


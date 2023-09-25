import openai
import streamlit as st
from elasticsearch import Elasticsearch

es_username = st.secrets["es_username"]
es_password = st.secrets["es_password"]
es_cloudid = st.secrets["es_cloudid"]
es_index = st.secrets["es_index2"]

openai_api_key = st.secrets["openai_api_key"]

model = "gpt-3.5-turbo-0301"

def es_connect(cid, user, passwd):
    es = Elasticsearch(cloud_id=cid, basic_auth=(user, passwd))
    return es

def search(index, search_template, query_text):
    cid = es_cloudid
    cp = es_password
    cu = es_username
    es = es_connect(cid, cu, cp)

    # params = '"query_string":' + '"' + query_text + '"'
    params = {"query_string" : query_text}

    resp = es.search_template(index=index,
                              id=search_template,
                              params=params)

    if resp['hits']['total']['value'] > 0:
        title = resp['hits']['hits'][0]['_source']['title']
        content = resp['hits']['hits'][0]['_source']['desc-body']
        url = resp['hits']['hits'][0]['_source']['url']

        return title, content, url
    else:
        return False 


# jh-search-bm25
# jh-search-text-expander
# jh-search-dense-vector
# jh-search-rrf
template = "mitre-search-rrf"

# Generate and display response on form submission
negResponse = "I'm unable to answer the question based on the information I have from your docs."

st.set_page_config(layout="wide")

st.title("MITRE GPT")
st.header("💬 Chat with MITRE ATT&CK® Enterprise")
st.subheader("This is a concept conversational Q/A chatbot using Tactics and Techniques from MITRE ATT&CK® knowledge base.")
st.write("© 2023 The MITRE Corporation. This work is reproduced and distributed with the permission of The MITRE Corporation. https://attack.mitre.org")
st.caption("🤖 RAG with Elastic + OpenAI LLM")

with st.expander("Expand for Search"):

    with st.form("chat_form"):
        query = st.text_input("Search with Elastic")
        submit_button = st.form_submit_button("Search")

    if submit_button:

        tab1, tab2, tab3 = st.tabs(["BM25","Dense Vector","RRF"])

        with tab1:
            results = False
            try:
                title, body, url = search(es_index, "mitre-search-bm25", query)
                results = True
            except:
                st.write("No results found")

            if results:
                st.header(title)
                st.write(body)
                st.write(url)

        with tab2:
            results = False
            try:
                title, body, url = search(es_index, "mitre-search-dense-vector", query)
                results = True
            except:
                st.write("No results found")

            if results:
                st.header(title)
                st.write(body)
                st.write(url)


        with tab3:
            results = False
            try:
                title, body, url = search(es_index, "mitre-search-rrf", query)
                results = True
            except:
                st.write("No results found")

            if results:
                st.header(title)
                st.write(body)
                st.write(url)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "You are a cyber security analyst friendly assistant."}]

if "prompts" not in st.session_state:
    st.session_state["prompts"] = [{"role": "assistant", "content": "You are a cyber security analyst friendly assistant."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

    results = False
    try:
        title, body, url = search(es_index, template, prompt)
        results = True
    except:
        results = False

    if results:
        assistant_prompt = f"""
        Using your years of experience as a blue team cyber defender, can you help me with this question: {prompt}\n
        Using only the following information from mitre attack framework and your experience: {body}\n
        Please structure the response to a cyber security analyst with the following format:\n
        Summary:\n
        Point 1:\n
        Point 2:\n
        Point 3:\n
        Additionally provide another 3 points from your analyst experience that is not found in the above\n
        Point 4:\n
        Point 5:\n
        Point 6:\n        
        Provide a simple explaination to a Chief Security Officer:\n
        If the answer is not contained in the supplied doc reply '{negResponse}' and nothing else.\n
        """

        openai.api_key = openai_api_key
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.prompts.append({"role": "user", "content": assistant_prompt})
        st.chat_message("user").write(prompt)

        # st.chat_message("assistant").write(assistant_prompt)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.prompts)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        st.session_state.prompts.append(msg)
        st.chat_message("assistant").write(msg.content)


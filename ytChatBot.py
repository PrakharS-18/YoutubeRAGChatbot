from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_oci import ChatOCIGenAI, OCIGenAIEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit as st
from urllib.parse import urlparse, parse_qs


COMPARTMENT_ID = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # put your compartment id
AUTH_TYPE = "API_KEY"
CONFIG_PROFILE = "DEFAULT"

# Service endpoint
endpoint = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# initialize chat model instance - this instance is provided by Oracle Cloud Infrastructure, you can use any other LLM models
chatModel = ChatOCIGenAI(
    model_id="cohere.command-a-03-2025",
    service_endpoint=endpoint,
    compartment_id=COMPARTMENT_ID,
    model_kwargs={
        "temperature": 0.5,
        "max_tokens": 600,
    },
    auth_type=AUTH_TYPE,
    auth_profile=CONFIG_PROFILE
)

# initialize embedding model instance - this instance is provided by Oracle Cloud Infrastructure, you can use any other Embedding models
embeddingsModel = OCIGenAIEmbeddings(
  model_id="cohere.embed-english-v3.0",
  service_endpoint=endpoint,
  truncate="NONE",
  compartment_id=COMPARTMENT_ID,
  auth_type=AUTH_TYPE,
  auth_profile=CONFIG_PROFILE
)


def fetch_video_id_from_url(url: str) -> str:
    """
    Extracts the YouTube video ID from a URL containing the 'v' query parameter.
    Returns the video ID as a string, or None if not found.
    """
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    video_id_list = query_params.get("v")

    if video_id_list:
        return video_id_list[0]
    return None


# --- App Title ---
st.title("🎥 YouTube Chat Bot")

# --- Initialize session state ---
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "prompt" not in st.session_state:
    st.session_state.prompt = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_video_id" not in st.session_state:
    st.session_state.current_video_id = None
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "question_key" not in st.session_state:
    st.session_state.question_key = 0


# --- Reset Function ---
def reset_app():
    st.session_state.retriever = None
    st.session_state.prompt = None
    st.session_state.chat_history = []
    st.session_state.current_video_id = None
    st.session_state.input_key += 1  # Increment key to reset input field


# --- Try Next Video Button (shown only when a video is loaded) ---
if st.session_state.retriever is not None:
    if st.button("🔄 Try Next Video"):
        reset_app()
        st.rerun()

# --- Input: YouTube URL ---
yt_url = st.text_input("Enter a YouTube video URL:", key=f"url_input_{st.session_state.input_key}",
                       placeholder="https://www.youtube.com/watch?v=...")
fetch_button = st.button("Enter", type="primary")

# --- Step 1: Fetch Transcript + Build FAISS ---
if fetch_button:
    if not yt_url or not yt_url.strip():
        st.warning("⚠️ Please enter a YouTube URL first!")
    else:
        video_id = fetch_video_id_from_url(yt_url)
        if not video_id:
            st.error("❌ Invalid YouTube URL")
        else:
            with st.spinner("🔄 Fetching transcript and building knowledge base..."):
                try:
                    transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=["en"])
                    transcript = " ".join(chunk.text for chunk in transcript_list)

                    # Store current video ID
                    st.session_state.current_video_id = video_id

                    # --- Text Splitting ---
                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    chunks = splitter.create_documents([transcript])

                    # --- FAISS Embeddings ---
                    vector_store = FAISS.from_documents(chunks, embeddingsModel)
                    st.session_state.retriever = vector_store.as_retriever(
                        search_type='similarity', search_kwargs={"k": 4}
                    )

                    # --- Prompt Template ---
                    st.session_state.prompt = PromptTemplate(
                        template="""
                        You are a helpful assistant. 
                        Answer only from the transcript provided below.

                        {context}

                        Question: {question}
                        """,
                        input_variables=['context', 'question']
                    )

                    st.success("✅ I am ready to answer your questions!")

                except TranscriptsDisabled:
                    st.error("❌ Transcripts are disabled for this video.")
                except NoTranscriptFound:
                    st.error("❌ No English transcript was found for this video.")
                except Exception as e:
                    st.error(f"⚠️ Error fetching transcript: {e}")

# --- Step 2: Ask Questions only if retriever is ready ---
if st.session_state.retriever:

    st.markdown("---")
    st.markdown("### 💬 Ask Questions About the Video")


    def format_doc(docs):
        yield "\n\n".join(x.page_content for x in docs)


    def run_rag_query(question):
        parallel_chain = RunnableParallel({
            "context": st.session_state.retriever | RunnableLambda(format_doc),
            "question": RunnablePassthrough(),
        })
        parser = StrOutputParser()
        main_chain = parallel_chain | st.session_state.prompt | chatModel | parser
        return main_chain.invoke(question)


    # --- Chat Form ---
    with st.form("ask_form", clear_on_submit=True):
        user_q = st.text_area("Ask a question:")  # No dynamic key needed!
        submitted = st.form_submit_button("Submit", type="primary")

    if submitted and user_q.strip():
        with st.spinner("🤔 Generating answer..."):
            response = run_rag_query(user_q)
            st.session_state.chat_history.append({"question": user_q, "response": response})
            st.session_state.question_key += 1  # Increment to clear the text area

        # Display the latest Q&A with styled formatting
        st.markdown("---")
        st.markdown(
            f"""
            <div style='background-color: #d1e7ff; padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 6px solid #0066cc; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                    <span style='font-size: 24px; margin-right: 10px;'>❓</span>
                    <b style='color: #0066cc; font-size: 18px;'>Question:</b>
                </div>
                <p style='margin: 0; color: #1a1a1a; font-size: 15px; line-height: 1.6;'>{user_q}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 24px; border-radius: 16px; border: 1px solid #334155; box-shadow: 0 8px 16px rgba(0,0,0,0.4), 0 0 0 1px rgba(148,163,184,0.1);'>
                <div style='display: flex; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #334155;'>
                    <span style='font-size: 28px; margin-right: 12px; filter: drop-shadow(0 0 8px rgba(34,197,94,0.5));'>✅</span>
                    <b style='color: #22c55e; font-size: 20px; letter-spacing: 0.5px; text-shadow: 0 0 10px rgba(34,197,94,0.3);'>Answer:</b>
                </div>
                <p style='margin: 0; color: #e2e8f0; font-size: 16px; line-height: 1.9; white-space: pre-wrap; text-shadow: 0 1px 2px rgba(0,0,0,0.3);'>{response}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- Sidebar Chat History ---
    st.sidebar.title("💬 Chat History")
    if st.session_state.chat_history:
        for i, chat in enumerate(st.session_state.chat_history, 1):
            with st.sidebar.expander(f"🟦 Q{i}: {chat['question'][:50]}..."):
                st.write(f"**Question:** {chat['question']}")
                st.write(f"**Answer:** {chat['response']}")
    else:
        st.sidebar.info("No questions asked yet.")
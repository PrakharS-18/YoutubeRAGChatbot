# 🎥 YouTube Chat Bot (Oracle Cloud + LangChain)

A Streamlit web application that allows you to interactively ask questions about YouTube videos using the video's transcript as knowledge source. This app leverages [LangChain](https://python.langchain.com/), [FAISS vector store](https://github.com/facebookresearch/faiss), Cohere LLM/embeddings hosted on [Oracle Cloud Infrastructure Generative AI](https://www.oracle.com/cloud/ai/generative-ai/), and supports secure deployment and private inference.

---

## ✨ Features

- **Ingest YouTube Video Transcript:** Paste a YouTube URL, and the app fetches the available English transcript (if available).
- **Embeddings and Retrieval:** The transcript is split and embedded using Cohere's embedding models (via OCI). Retrieval is powered by a FAISS vector store.
- **Oracle Cloud GenAI Integration:** Uses Oracle’s hosted Large Language Models (LLMs) for answering questions using context from the video.
- **Conversational Q&A:** Ask follow-up questions in a chat interface. Only the video’s transcript is referenced.
- **Chat History:** Sidebar displays all previously asked questions/answers.
- **Easy Reset:** “Try Next Video” button resets the session for a new video.

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.8 or later
- Oracle Cloud account with access to Generative AI services and API keys set up
- Access to [Cohere models](https://docs.oracle.com/en-us/iaas/tools/generative-ai/sdk/python/latest/models.html) via the [OCI Generative AI Python SDK](https://docs.oracle.com/en-us/iaas/tools/generative-ai/sdk/python/latest/)

### 2. Install Dependencies

```bash
pip install streamlit langchain oci langchain_oci youtube-transcript-api faiss-cpu
```

> **Note:** If running in Oracle environments, check with your IT team about internal package mirrors and compliance restrictions before installing new Python packages.

---

### 3. Required Configuration

- **OCI Credentials:**  
  - Place your OCI config file (typically at `~/.oci/config`) and set your desired profile name.
  - Ensure your user has access to the GenAI service and specified compartment.

- **Edit the Code:**  
  - Set your OCI `COMPARTMENT_ID`, `endpoint` (GenAI API endpoint), and other configuration parameters at the top of the script.

```python
COMPARTMENT_ID = "your_ocid"
endpoint = "your_service_endpoint"
CONFIG_PROFILE = "DEFAULT"
AUTH_TYPE = "API_KEY"
```

---

### 4. Running the Application

```bash
streamlit run app.py
```

- Open the provided local URL in your browser (e.g., `http://localhost:8501`).

---

## 📝 How It Works

1. **Paste any YouTube URL** (with a visible transcript).  
2. Click **Enter** – the app fetches the transcript, splits and embeds it, and builds a FAISS search index.
3. **Ask questions** related to the video content.
4. The app retrieves relevant chunks, combines them, and sends context plus your question to the GenAI LLM for an answer.
5. **Q&A pairs** appear in the chat and sidebar history.

---

## ⚠️ Security, Privacy, and Compliance

- Ensure all API keys and credentials are secured and **never** hardcoded or shared.
- Do not upload or process sensitive or internal videos or data unless you have permission and the content complies with relevant Oracle policies.
- Use Oracle-approved endpoints and models in accordance with internal security guidelines.
- For more details on safely using generative AI at Oracle, visit the [AI for Employees Portal](https://oracle.sharepoint.com/sites/ai-for-employees/SitePages/AI%20in%20chat.oracle.com.aspx).

---

## 🙋‍♀️ Troubleshooting & Help

- **Generative Chat Assistance:** [AI for Employees](https://oracle.sharepoint.com/sites/ai-for-employees/SitePages/AI%20in%20chat.oracle.com.aspx)
- **Technical Support:** Slack channel [#help-oracle-genai-chat](https://oracle.enterprise.slack.com/archives/C08S2U7HDPU)
- **Error Messages:**  
  - *“Transcripts are disabled for this video”*: The video owner has not enabled subtitles.
  - *“No English transcript was found for this video”*: Only English transcripts are supported by default.

---

## 🛡️ Disclaimer

This tool is meant for prototypes, demos, and personal productivity. For production usage, consult with Oracle Cloud engineering teams for best practices in security, scaling, and compliance. The app processes third-party content (YouTube) and relies on external APIs. Validate privacy and copyright policies accordingly.

---

## 📄 License

[MIT License](LICENSE) (modify as required by your project or organizational guidelines)

---

## 👋 Contact

For Oracle-internal use, reach out via the AI for Employees resources or [#help-oracle-genai-chat](https://oracle.enterprise.slack.com/archives/C08S2U7HDPU).

---

*Happy chatting with your favorite videos!*

from .llm_client import LLMClient
from .pinecone_utils import init_pinecone
from sentence_transformers import SentenceTransformer
from .web_search import google_search
import time



#Receives question and whether to use web or not, builds llm client up with api and specific model. 
#If it is set to use web search, searches. Packages question with web results and pases to llm to 
#generate. Pases answer and web results to evaluate overlap. If Web Search off, ensembles pinecone
#client, ensembles embeder model, embeds question, retrieves top 5 embeddings, takes matches and 
#contexts, creates prompt with q and retrieved, asks llm and evaluates. 

#With contents, question and prompt. If no web results answers with what there is at general knowledge, 
#ensembles with question, context and prompt. Evaluates answer with overlap. 

def orchestrate_query(question: str, use_web: bool, cfg, secrets: dict):
    llm = LLMClient(secrets["OPENAI_API_KEY"], cfg.OPENAI_MODEL)
    if use_web:
        web_results = google_search(question, secrets["google_api_key"], secrets.get("google_cx"),)
        if not isinstance(web_results, list):
            web_results = []
        prompt = craft_prompt_web(question, web_results)
        answer = llm.generate(prompt)
        evaluation = evaluate_answer(answer, web_results)
        # Optionally: log to DynamoDB here (left to caller)
        return {"answer": answer, "sources": web_results, "evaluation": evaluation}
    else:
        pine_idx = init_pinecone(secrets["pinecone_api_key"],cfg.PINECONE_INDEX,cfg.PINECONE_DIM)
        embedder = SentenceTransformer(cfg.EMBED_MODEL)
        q_emb = embedder.encode([question])[0].tolist()
        res = pine_idx.query(vector=q_emb, top_k=5, include_metadata=True)
        matches = res.get('matches', [])
        contexts = [m.get('metadata', {}) for m in matches]
        prompt = craft_prompt_rag(question, contexts)
        answer = llm.generate(prompt)
        evaluation = evaluate_answer(answer, contexts)
        return {"answer": answer, "sources": contexts, "evaluation": evaluation}




def craft_prompt_rag(question, contexts):
    context_text = "\n\n---\n".join([c.get("text", "")[:2000] for c in contexts])
    prompt = f"""You are a helpful, factual assistant. Use the provided context to answer the question. If the answer is not directly in the context, say \"I don't know\" and provide the best effort with explicit uncertainty.


Context:
{context_text}


Question:
{question}


Answer concisely and include short 'source:' lines listing source ids if relevant.
"""
    return prompt




def craft_prompt_web(question, web_results):
    if not web_results:
        return f"""You are a helpful assistant.

Question:
{question}

No web snippets were available. Answer using general knowledge and clearly state uncertainty if needed.
"""

    snippets = "\n".join(
        [
            f"{i+1}. {r.get('title', 'No title')} - {r.get('snippet', '')}"
            for i, r in enumerate(web_results)
            if isinstance(r, dict)
        ]
    )

    prompt = f"""You are an assistant that answers using web search snippets. Use the snippets and indicate which snippet you used.

Snippets:
{snippets}

Question:
{question}

Answer concisely, and list snippet numbers used under 'sources:'.
"""
    return prompt

def evaluate_answer(answer, sources):
    score = 0
    reasons = []
    if "i don't know" in answer.lower():
        score -= 1
        reasons.append("assistant admitted lack of knowledge")
    if len(answer.split()) > 10:
        score += 1
    src_text = " ".join(
        [
            s.get("text", "") if isinstance(s, dict)
            else s.get("snippet", "") if isinstance(s, dict)
            else str(s)
            for s in sources
        ]
    )


    overlap = sum(1 for w in set(answer.split()) if w in src_text)
    if overlap > 5:
        score += 1
    return {"score": score, "reasons": reasons, "overlap": overlap}
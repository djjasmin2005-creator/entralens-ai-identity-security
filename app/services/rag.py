from sqlalchemy.orm import Session
from ..models import KnowledgeDoc

def retrieve_knowledge(db: Session, question: str, limit: int = 3):
    words = {w.lower().strip('.,?!') for w in question.split() if len(w) > 2}
    docs = db.query(KnowledgeDoc).all()
    ranked = []
    for doc in docs:
        hay = (doc.title + ' ' + doc.content).lower()
        score = sum(1 for w in words if w in hay)
        if score:
            ranked.append((score, doc))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in ranked[:limit]] or docs[:limit]

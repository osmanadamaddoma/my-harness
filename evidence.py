# evidence.py - الميزة 2: جمع وتقييم الأدلة
# جزء من Verify-First Agent

import re
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Evidence:
    """دليل واحد"""
    text: str
    source: str = "manual"
    source_type: str = "text"
    reliability: float = 0.5
    id: str = ""
    added_at: str = ""
    keywords: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(self.text.encode()).hexdigest()[:8]
        if not self.added_at:
            self.added_at = datetime.now().isoformat()

@dataclass
class EvidenceScore:
    evidence_id: str
    evidence_text: str
    relevance: float
    reliability: float
    final_score: float
    matched_keywords: List[str] = field(default_factory=list)

class EvidenceStore:
    """مخزن الأدلة"""

    def __init__(self):
        self.items: List[Evidence] = []
        self.index: Dict[str, List[str]] = {}

    def add(self, text: str, source="manual", reliability=0.5, source_type="text") -> Evidence:
        ev = Evidence(text=text, source=source, reliability=reliability, source_type=source_type)
        ev.keywords = self._extract_keywords(text)
        self.items.append(ev)
        for kw in ev.keywords:
            if kw not in self.index:
                self.index[kw] = []
            self.index[kw].append(ev.id)
        return ev

    def add_many(self, texts: List[str], source="bulk") -> List[Evidence]:
        out = []
        for t in texts:
            out.append(self.add(t, source=source))
        return out

    def _extract_keywords(self, text: str) -> List[str]:
        words = re.findall(r'[\w]+', text.lower())
        out = []
        for w in words:
            if len(w) > 2 and w not in out:
                out.append(w)
        return out[:12]

    def get_all(self) -> List[Evidence]:
        return self.items

    def get_by_source(self, source: str) -> List[Evidence]:
        return [e for e in self.items if e.source == source]

    def search_by_keyword(self, keyword: str) -> List[Evidence]:
        keyword = keyword.lower()
        ids = self.index.get(keyword, [])
        return [e for e in self.items if e.id in ids]

    def clear(self):
        self.items = []
        self.index = {}

    def count(self) -> int:
        return len(self.items)

class EvidenceRetriever:
    """البحث عن الدليل المناسب للادعاء"""

    def __init__(self, store: EvidenceStore):
        self.store = store

    def _normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def _tokenize(self, text: str) -> set:
        return set(self._normalize(text).split())

    def relevance(self, claim: str, evidence_text: str) -> float:
        c = self._tokenize(claim)
        e = self._tokenize(evidence_text)
        if not c:
            return 0.0
        common = c.intersection(e)
        # Jaccard + coverage
        jaccard = len(common) / len(c.union(e)) if c.union(e) else 0
        coverage = len(common) / len(c)
        return round((jaccard * 0.4 + coverage * 0.6), 3)

    def find_best(self, claim: str, top_k=3) -> List[EvidenceScore]:
        scored = []
        claim_tokens = self._tokenize(claim)
        for ev in self.store.get_all():
            rel = self.relevance(claim, ev.text)
            if rel <= 0:
                continue
            matched = list(claim_tokens.intersection(self._tokenize(ev.text)))
            final = round(rel * 0.7 + ev.reliability * 0.3, 3)
            scored.append(EvidenceScore(ev.id, ev.text, rel, ev.reliability, final, matched))
        scored.sort(key=lambda x: x.final_score, reverse=True)
        return scored[:top_k]

    def find_by_keywords(self, keywords: List[str]) -> List[Evidence]:
        found = []
        seen = set()
        for kw in keywords:
            for ev in self.store.search_by_keyword(kw.lower()):
                if ev.id not in seen:
                    found.append(ev)
                    seen.add(ev.id)
        return found

class EvidenceEvaluator:
    """تقييم جودة الأدلة"""

    def __init__(self):
        self.source_trust = {
            "official": 0.95,
            "academic": 0.9,
            "news": 0.7,
            "manual": 0.5,
            "social": 0.3,
            "unknown": 0.2,
        }

    def trust_of(self, source_type: str) -> float:
        return self.source_trust.get(source_type, 0.5)

    def evaluate(self, evidences: List[Evidence]) -> Dict:
        if not evidences:
            return {"total": 0, "avg_reliability": 0.0, "best_source": "none", "verdict": "لا يوجد دليل"}
        avg = sum(e.reliability for e in evidences) / len(evidences)
        best = max(evidences, key=lambda x: x.reliability)
        if avg >= 0.8:
            verdict = "أدلة قوية"
        elif avg >= 0.5:
            verdict = "أدلة متوسطة"
        else:
            verdict = "أدلة ضعيفة"
        return {
            "total": len(evidences),
            "avg_reliability": round(avg, 2),
            "best_source": best.source,
            "best_text": best.text[:80],
            "verdict": verdict,
        }

    def filter_weak(self, evidences: List[Evidence], threshold=0.4) -> List[Evidence]:
        return [e for e in evidences if e.reliability >= threshold]

    def rank(self, evidences: List[Evidence]) -> List[Evidence]:
        return sorted(evidences, key=lambda x: x.reliability, reverse=True)

class EvidenceLogger:
    """تسجيل كل عملية بحث"""

    def __init__(self):
        self.logs: List[Dict] = []

    def log(self, claim: str, found: int, top_score: float):
        self.logs.append({
            "claim": claim[:100],
            "found": found,
            "top_score": top_score,
            "at": datetime.now().isoformat()
        })

    def summary(self) -> Dict:
        if not self.logs:
            return {"searches": 0}
        avg = sum(l["top_score"] for l in self.logs) / len(self.logs)
        return {"searches": len(self.logs), "avg_top_score": round(avg, 2)}

if __name__ == "__main__":
    store = EvidenceStore()
    store.add("الذكاء الاصطناعي يطور التعليم في المدارس", source="academic", reliability=0.9)
    store.add("الماء يغلي عند 100 درجة", source="official", reliability=0.95)
    store.add("كلام من فيسبوك بدون مصدر", source="social", reliability=0.3)
    retriever = EvidenceRetriever(store)
    results = retriever.find_best("الذكاء الاصطناعي يطور التعليم", top_k=2)
    for r in results:
        print(r.evidence_text, "->", r.final_score, r.matched_keywords)
    evaluator = EvidenceEvaluator()
    print(evaluator.evaluate(store.get_all()))
    print("Store count:", store.count())

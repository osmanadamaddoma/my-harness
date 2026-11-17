# verifier.py - الميزة 1: تحليل وتحقق الادعاء
# جزء من Verify-First Agent - النسخة الكاملة

import re
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Claim:
    """تمثيل ادعاء واحد"""
    text: str
    id: str = ""
    source: str = "user"
    created_at: str = ""
    parts: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    confidence: float = 0.0
    status: str = "pending"

    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(self.text.encode()).hexdigest()[:8]
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

@dataclass
class VerificationResult:
    """نتيجة التحقق"""
    claim_id: str
    claim_text: str
    verdict: str
    score: float
    reasons: List[str] = field(default_factory=list)
    evidence_used: List[str] = field(default_factory=list)
    checked_at: str = ""

class ClaimParser:
    """تقسيم الادعاء الطويل لادعاءات صغيرة"""

    def __init__(self):
        self.stop_words = {"في", "من", "الى", "على", "ان", "هو", "هي", "كان", "يكون"}
        self.sentence_end = re.compile(r'[.!?؟\n]+')

    def clean(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def split_sentences(self, text: str) -> List[str]:
        text = self.clean(text)
        if not text:
            return []
        parts = self.sentence_end.split(text)
        result = []
        for p in parts:
            p = p.strip()
            if len(p) > 3:
                result.append(p)
        return result

    def extract_keywords(self, text: str) -> List[str]:
        words = re.findall(r'[\w]+', text)
        keywords = []
        for w in words:
            if len(w) > 2 and w not in self.stop_words:
                if w not in keywords:
                    keywords.append(w)
        return keywords[:10]

    def parse(self, text: str) -> List[Claim]:
        sentences = self.split_sentences(text)
        claims = []
        for s in sentences:
            c = Claim(text=s)
            c.parts = self.split_sentences(s)
            c.keywords = self.extract_keywords(s)
            claims.append(c)
        return claims

class Verifier:
    """محرك التحقق الأساسي"""

    def __init__(self):
        self.parser = ClaimParser()
        self.history: List[VerificationResult] = []
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, float]:
        return {
            "empty_claim": -1.0,
            "empty_evidence": -1.0,
            "exact_match": 1.0,
            "partial_match": 0.6,
            "keyword_match": 0.4,
            "no_match": 0.0,
            "contradiction": -0.8,
        }

    def _normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def _keyword_score(self, claim: str, evidence: str) -> float:
        c_words = set(self._normalize(claim).split())
        e_words = set(self._normalize(evidence).split())
        if not c_words:
            return 0.0
        common = c_words.intersection(e_words)
        return len(common) / len(c_words)

    def _check_contradiction(self, claim: str, evidence: str) -> bool:
        neg_words = ["لا", "ليس", "not", "never", "no"]
        c_neg = any(w in claim for w in neg_words)
        e_neg = any(w in evidence for w in neg_words)
        return c_neg != e_neg and self._keyword_score(claim, evidence) > 0.5

    def verify_single(self, claim_text: str, evidence_list: List[str]) -> VerificationResult:
        claim = Claim(text=claim_text)
        claim.keywords = self.parser.extract_keywords(claim_text)

        if not claim_text.strip():
            return VerificationResult(claim.id, claim_text, "مرفوض", 0.0, ["الادعاء فارغ"])

        if not evidence_list:
            return VerificationResult(claim.id, claim_text, "مرفوض - مافي دليل", 0.0, ["لا يوجد دليل"])

        best_score = 0.0
        best_evidence = ""
        reasons = []
        used = []

        for ev in evidence_list:
            if not ev.strip():
                continue
            norm_claim = self._normalize(claim_text)
            norm_ev = self._normalize(ev)
            if norm_ev in norm_claim or norm_claim in norm_ev:
                score = 1.0
                reasons.append(f"تطابق كامل مع: {ev[:50]}")
            else:
                score = self._keyword_score(claim_text, ev)
                if score > 0.7:
                    reasons.append(f"تطابق عالي {score:.2f} مع: {ev[:50]}")
                elif score > 0.3:
                    reasons.append(f"تطابق جزئي {score:.2f}")

            if self._check_contradiction(claim_text, ev):
                score = max(0.0, score - 0.8)
                reasons.append("تم اكتشاف تناقض محتمل")

            if score > best_score:
                best_score = score
                best_evidence = ev
            used.append(ev)

        if best_score >= 0.8:
            verdict = "مقبول - تم التحقق"
        elif best_score >= 0.4:
            verdict = "يحتاج مراجعة"
        else:
            verdict = "مرفوض - دليل ضعيف"

        result = VerificationResult(
            claim_id=claim.id,
            claim_text=claim_text,
            verdict=verdict,
            score=round(best_score, 2),
            reasons=reasons if reasons else ["لا يوجد تطابق كافي"],
            evidence_used=used,
            checked_at=datetime.now().isoformat()
        )
        self.history.append(result)
        return result

    def verify_many(self, claims: List[str], evidences: Dict[str, List[str]]) -> List[VerificationResult]:
        results = []
        for c in claims:
            ev = evidences.get(c, [])
            results.append(self.verify_single(c, ev))
        return results

    def get_stats(self) -> Dict:
        if not self.history:
            return {"total": 0, "accepted": 0, "rejected": 0, "avg_score": 0.0}
        total = len(self.history)
        accepted = sum(1 for r in self.history if "مقبول" in r.verdict)
        rejected = sum(1 for r in self.history if "مرفوض" in r.verdict)
        avg = sum(r.score for r in self.history) / total
        return {"total": total, "accepted": accepted, "rejected": rejected, "avg_score": round(avg, 2)}

if __name__ == "__main__":
    v = Verifier()
    print("=== اختبار verifier.py ===")
    r1 = v.verify_single("الذكاء الاصطناعي يطور التعليم", ["الذكاء الاصطناعي يطور التعليم في المدارس"])
    print(r1.verdict, r1.score, r1.reasons)
    r2 = v.verify_single("الماء يغلي", [])
    print(r2.verdict, r2.score)
    print(v.get_stats())

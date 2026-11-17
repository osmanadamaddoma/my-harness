# main.py - المشغل الرئيسي - Verify-First Agent
# يربط verifier.py + evidence.py مع بعض

import os
import json
from datetime import datetime
from verifier import Verifier, ClaimParser
from evidence import EvidenceStore, EvidenceRetriever, EvidenceEvaluator, EvidenceLogger

class VerifyFirstAgent:
    """الوكيل الكامل"""

    def __init__(self):
        self.verifier = Verifier()
        self.parser = ClaimParser()
        self.store = EvidenceStore()
        self.retriever = EvidenceRetriever(self.store)
        self.evaluator = EvidenceEvaluator()
        self.logger = EvidenceLogger()
        self._load_default_evidence()

    def _load_default_evidence(self):
        defaults = [
            ("الذكاء الاصطناعي يطور التعليم في المدارس والجامعات", "academic", 0.9),
            ("الماء يغلي عند درجة حرارة 100 درجة مئوية", "official", 0.95),
            ("السودان يقع في شمال شرق افريقيا", "official", 0.95),
            ("الرياضة تحسن صحة القلب", "academic", 0.85),
            ("القراءة اليومية تطور مهارات اللغة", "academic", 0.8),
        ]
        for text, src, rel in defaults:
            self.store.add(text, source=src, reliability=rel)

    def add_evidence(self, text: str, source="manual", reliability=0.5):
        return self.store.add(text, source=source, reliability=reliability)

    def check(self, claim_text: str):
        # 1. تقسيم الادعاء
        claims = self.parser.parse(claim_text)
        print(f"\nتم تقسيم الادعاء الى {len(claims)} ادعاء فرعي")
        all_results = []
        for c in claims:
            # 2. البحث عن الدليل
            best = self.retriever.find_best(c.text, top_k=3)
            evid_texts = [b.evidence_text for b in best]
            self.logger.log(c.text, len(best), best[0].final_score if best else 0)
            # 3. التحقق
            result = self.verifier.verify_single(c.text, evid_texts)
            all_results.append((c, best, result))
            print("\n" + "=" * 50)
            print(f"الادعاء: {c.text}")
            print(f"الكلمات: {', '.join(c.keywords[:5])}")
            if best:
                print("أفضل الأدلة:")
                for b in best:
                    print(f"  - {b.evidence_text[:70]} | درجة: {b.final_score}")
            else:
                print("  لا يوجد دليل")
            print(f"النتيجة: {result.verdict} | الثقة: {result.score}")
            for reason in result.reasons:
                print(f"  * {reason}")
        return all_results

    def run_demo(self):
        print("=" * 60)
        print("Verify-First Agent - Demo كامل")
        print(f"عدد الأدلة في المخزن: {self.store.count()}")
        print("=" * 60)
        demos = [
            "الذكاء الاصطناعي يطور التعليم",
            "الماء يغلي عند 100 درجة",
            "السودان يقع في افريقيا",
            "الارض مسطحة تماما بدون دليل",
        ]
        for d in demos:
            self.check(d)
        self.print_report()

    def print_report(self):
        stats = self.verifier.get_stats()
        eval_info = self.evaluator.evaluate(self.store.get_all())
        log_info = self.logger.summary()
        print("\n" + "=" * 60)
        print("التقرير النهائي")
        print("=" * 60)
        print(f"إجمالي التحققات: {stats['total']}")
        print(f"مقبول: {stats['accepted']} | مرفوض: {stats['rejected']}")
        print(f"متوسط الثقة: {stats['avg_score']}")
        print(f"تقييم الأدلة: {eval_info['verdict']} - متوسط الموثوقية {eval_info['avg_reliability']}")
        print(f"عمليات البحث: {log_info.get('searches', 0)}")
        self.save_report(stats, eval_info)

    def save_report(self, stats, eval_info):
        report = {
            "app": "Verify-First Agent",
            "at": datetime.now().isoformat(),
            "stats": stats,
            "evidence_eval": eval_info,
            "total_evidence": self.store.count(),
        }
        with open("report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        with open("log.txt", "w", encoding="utf-8") as f:
            f.write(f"Verify-First Agent Log\n")
            f.write(f"At: {report['at']}\n")
            f.write(f"Stats: {stats}\n")
        print("تم حفظ report.json و log.txt")

    def interactive(self):
        print("\n=== الوضع التفاعلي - اكتب 'خروج' للخروج ===")
        while True:
            claim = input("\nالادعاء: ").strip()
            if claim.lower() in ["خروج", "exit", "quit", ""]:
                print("مع السلامة!")
                break
            ev = input("أضف دليل (أو اضغط Enter للتخطي): ").strip()
            if ev:
                self.add_evidence(ev, source="manual", reliability=0.6)
            self.check(claim)

def main():
    agent = VerifyFirstAgent()
    agent.run_demo()
    # لو داير تجرب بنفسك، شيل # من السطر الجاي:
    # agent.interactive()

if __name__ == "__main__":
    main()

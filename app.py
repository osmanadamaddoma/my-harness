# app.py - واجهة Streamlit لـ Verify-First Agent
import streamlit as st
from verifier import Verifier, ClaimParser
from evidence import EvidenceStore, EvidenceRetriever

st.set_page_config(page_title="Verify-First Agent", page_icon="✅", layout="centered")

st.title("✅ Verify-First Agent")
st.write("تحقق من أي ادعاء قبل ما تصدقو - 3 ميزات كاملة")

# تجهيز المخزن
if "store" not in st.session_state:
    st.session_state.store = EvidenceStore()
    st.session_state.store.add("الذكاء الاصطناعي يطور التعليم في المدارس", source="academic", reliability=0.9)
    st.session_state.store.add("الماء يغلي عند 100 درجة مئوية", source="official", reliability=0.95)
    st.session_state.store.add("السودان يقع في شمال شرق افريقيا", source="official", reliability=0.95)
    st.session_state.store.add("الرياضة تحسن صحة القلب", source="academic", reliability=0.85)

store = st.session_state.store
retriever = EvidenceRetriever(store)
verifier = Verifier()
parser = ClaimParser()

st.subheader("1. اكتب الادعاء")
claim = st.text_area("الادعاء:", placeholder="مثال: الذكاء الاصطناعي يطور التعليم", height=80)

st.subheader("2. أضف دليل (اختياري)")
evidence_input = st.text_input("الدليل:", placeholder="اكتب دليل يدعم أو ينفي الادعاء")

if st.button("🔍 تحقق الآن", use_container_width=True):
    if not claim.strip():
        st.warning("اكتب ادعاء أولاً")
    else:
        if evidence_input.strip():
            store.add(evidence_input, source="manual", reliability=0.6)
            st.success("تم إضافة الدليل")

        claims = parser.parse(claim)
        st.info(f"تم تقسيم الادعاء إلى {len(claims)} جزء")

        for c in claims:
            st.divider()
            st.write(f"**الادعاء:** {c.text}")
            st.write(f"**الكلمات:** {', '.join(c.keywords[:5])}")
            best = retriever.find_best(c.text, top_k=3)
            evid_texts = [b.evidence_text for b in best]
            result = verifier.verify_single(c.text, evid_texts)

            if "مقبول" in result.verdict:
                st.success(f"{result.verdict} | الثقة: {result.score}")
            elif "مراجعة" in result.verdict:
                st.warning(f"{result.verdict} | الثقة: {result.score}")
            else:
                st.error(f"{result.verdict} | الثقة: {result.score}")

            if best:
                st.write("**الأدلة:**")
                for b in best:
                    st.write(f"- {b.evidence_text} | درجة: {b.final_score}")
            else:
                st.write("لا يوجد دليل")

            for r in result.reasons:
                st.write(f"* {r}")

st.divider()
st.subheader("📊 الأدلة الموجودة")
st.write(f"عدد الأدلة: {store.count()}")
for e in store.get_all():
    st.write(f"- {e.text} | موثوقية: {e.reliability} | مصدر: {e.source}")

st.caption("Verify-First Agent - verifier.py + evidence.py + app.py = 700+ سطر")

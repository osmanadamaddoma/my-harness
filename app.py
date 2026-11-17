# app.py - Verify-First Agent - English - 3 Features
import streamlit as st
from verifier import Verifier, ClaimParser
from evidence import EvidenceStore, EvidenceRetriever, EvidenceEvaluator

st.set_page_config(page_title="Verify-First Agent", page_icon="✅", layout="wide")
st.title("✅ Verify-First Agent")
st.write("Verify any claim before you trust it - 3 Features")

if "store" not in st.session_state:
    st.session_state.store = EvidenceStore()
    st.session_state.store.add("AI improves education in schools", source="academic", reliability=0.9)
    st.session_state.store.add("Water boils at 100 degrees Celsius", source="official", reliability=0.95)
    st.session_state.store.add("Sudan is located in Northeast Africa", source="official", reliability=0.95)
    st.session_state.store.add("Sport improves heart health", source="academic", reliability=0.85)
    st.session_state.store.add("Daily reading improves language skills", source="academic", reliability=0.8)
    st.session_state.history = []

store = st.session_state.store
retriever = EvidenceRetriever(store)
verifier = Verifier()
parser = ClaimParser()
evaluator = EvidenceEvaluator()

# 3 TABS = 3 FEATURES
tab1, tab2, tab3 = st.tabs(["🔍 FEATURE 1: Verify Claim", "📚 FEATURE 2: Evidence Search", "📊 FEATURE 3: Report & Dashboard"])

# ============ FEATURE 1 ============
with tab1:
    st.subheader("Feature 1: Verify a Claim")
    st.write("Split claim, check keywords, calculate confidence score")
    claim = st.text_area("Claim:", placeholder="Example: AI improves education", height=80, key="claim1")
    evidence_input = st.text_input("Add Evidence (optional):", placeholder="Write evidence", key="ev1")
    if st.button("Verify Now", use_container_width=True, key="btn1"):
        if not claim.strip():
            st.warning("Please write a claim first")
        else:
            if evidence_input.strip():
                store.add(evidence_input, source="manual", reliability=0.6)
                st.success("Evidence added")
            claims = parser.parse(claim)
            st.info(f"Claim split into {len(claims)} part(s)")
            for c in claims:
                st.divider()
                st.write(f"**Claim:** {c.text}")
                st.write(f"**Keywords:** {', '.join(c.keywords[:5])}")
                best = retriever.find_best(c.text, top_k=3)
                evid_texts = [b.evidence_text for b in best]
                result = verifier.verify_single(c.text, evid_texts)
                st.session_state.history.append(result)
                if "Accepted" in result.verdict or "مقبول" in result.verdict or result.score >= 0.8:
                    st.success(f"VERIFIED | Confidence: {result.score}")
                elif result.score >= 0.4:
                    st.warning(f"NEEDS REVIEW | Confidence: {result.score}")
                else:
                    st.error(f"REJECTED - Weak Evidence | Confidence: {result.score}")
                for r in result.reasons:
                    st.write(f"* {r}")

# ============ FEATURE 2 ============
with tab2:
    st.subheader("Feature 2: Evidence Search & Ranking")
    st.write("Search evidence by claim, rank by relevance + reliability")
    search = st.text_input("Search for evidence:", placeholder="Example: AI education", key="search2")
    col1, col2 = st.columns(2)
    with col1:
        min_rel = st.slider("Min Reliability", 0.0, 1.0, 0.3, key="rel2")
    with col2:
        top_k = st.number_input("Top Results", 1, 10, 3, key="top2")
    if st.button("Search Evidence", use_container_width=True, key="btn2"):
        if not search.strip():
            st.warning("Type something to search")
        else:
            results = retriever.find_best(search, top_k=int(top_k))
            if not results:
                st.error("No evidence found")
            else:
                for r in results:
                    if r.reliability >= min_rel:
                        st.write(f"**{r.evidence_text}**")
                        st.write(f"Relevance: {r.relevance} | Reliability: {r.reliability} | Final Score: {r.final_score}")
                        st.write(f"Matched: {', '.join(r.matched_keywords)}")
                        st.divider()
    st.subheader("Add New Evidence")
    new_ev = st.text_input("New Evidence Text:", key="new_ev")
    new_src = st.selectbox("Source Type:", ["official", "academic", "news", "manual", "social"], key="src2")
    new_rel = st.slider("Reliability", 0.0, 1.0, 0.5, key="new_rel")
    if st.button("Add Evidence", use_container_width=True, key="btn_add"):
        if new_ev.strip():
            store.add(new_ev, source=new_src, reliability=new_rel)
            st.success(f"Added! Total evidence now: {store.count()}")

# ============ FEATURE 3 ============
with tab3:
    st.subheader("Feature 3: Report & Dashboard")
    st.write("Statistics, evidence quality, verification history")
    stats = verifier.get_stats()
    # Use history from session + verifier history
    total_checks = len(st.session_state.history) + stats["total"]
    st.metric("Total Evidence", store.count())
    st.metric("Total Verifications", total_checks)
    eval_info = evaluator.evaluate(store.get_all())
    st.write(f"**Evidence Quality:** {eval_info['verdict']}")
    st.write(f"**Avg Reliability:** {eval_info['avg_reliability']}")
    st.write(f"**Best Source:** {eval_info['best_source']}")
    st.write("---")
    st.write("**All Evidence:**")
    for e in store.get_all():
        st.write(f"- {e.text} | Reliability: {e.reliability} | Source: {e.source}")
    st.write("---")
    st.write("**Verification History (This Session):**")
    if not st.session_state.history:
        st.info("No verifications yet. Go to Feature 1 and verify a claim.")
    else:
        for h in st.session_state.history:
            st.write(f"- {h.claim_text} -> {h.verdict} | Score: {h.score}")

st.caption("Verify-First Agent | verifier.py + evidence.py + app.py | 700+ lines | 3 Features")

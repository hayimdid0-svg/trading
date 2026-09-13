# -*- coding: utf-8 -*-
"""증권 도메인 101 — QA 관점 단계별 학습 카드 (Lv0~)"""

from pathlib import Path
import yaml
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(page_title="증권 도메인 101", page_icon="📘", layout="centered")


@st.cache_data
def load_levels():
    levels = []
    for p in sorted(DATA_DIR.glob("lv*.yaml")):
        with open(p, encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
        meta = doc.get("meta", {})
        meta["_file"] = p.name
        levels.append({
            "meta": meta,
            "cards": doc.get("cards", []),
            "interview": doc.get("interview_questions", []),
        })
    levels.sort(key=lambda d: d["meta"].get("level", 99))
    return levels


levels = load_levels()
if not levels:
    st.error("data 폴더에서 lv*.yaml 파일을 찾지 못했습니다. data\\lv0.yaml 이 있는지 확인하세요.")
    st.stop()

if "done" not in st.session_state:
    st.session_state.done = set()

# ---------------- 사이드바 ----------------
with st.sidebar:
    st.header("학습 진행")
    titles = [lv["meta"].get("title", lv["meta"]["_file"]) for lv in levels]
    pick = st.radio("레벨", range(len(levels)), format_func=lambda i: titles[i])
    lv = levels[pick]
    cards = lv["cards"]

    all_ids = [c["id"] for l in levels for c in l["cards"]]
    done_all = len([i for i in all_ids if i in st.session_state.done])
    st.metric("이해한 카드", f"{done_all} / {len(all_ids)}")
    st.progress(done_all / len(all_ids) if all_ids else 0.0)

    st.divider()
    hide_answer = st.checkbox("퀴즈 정답 가리기", value=True)
    if st.button("파일 다시 읽기"):
        st.cache_data.clear()
        st.rerun()

key = f"idx_{pick}"
if key not in st.session_state:
    st.session_state[key] = 0

st.title(lv["meta"].get("title", ""))
st.caption(lv["meta"].get("goal", ""))

tab_card, tab_grad, tab_itv = st.tabs(["개념 카드", "졸업 조건", "면접 질문"])

# ---------------- 개념 카드 ----------------
with tab_card:
    if not cards:
        st.info("이 레벨에는 아직 카드가 없습니다.")
    else:
        idx = min(st.session_state[key], len(cards) - 1)
        labels = [f"{c['id']} · {c['title']}" for c in cards]
        idx = st.selectbox("카드 선택", range(len(cards)),
                           index=idx, format_func=lambda i: labels[i])
        st.session_state[key] = idx
        c = cards[idx]

        st.caption(f"{idx + 1} / {len(cards)}    선수 카드: "
                   f"{', '.join(c.get('prereq') or ['없음'])}")
        st.subheader(c["title"])
        st.info(f"**한 문장** — {c.get('one_liner','')}")

        if c.get("analogy"):
            st.markdown(f"🧒 **쉬운 비유**\n\n{c['analogy']}")
        if c.get("key_insight"):
            st.markdown(f"🔑 **핵심**\n\n{c['key_insight']}")
        if c.get("where_in_app"):
            st.markdown(f"📱 **앱에서 보이는 곳** — {c['where_in_app']}")
        if c.get("common_confusion"):
            st.warning(f"헷갈리는 지점 — {c['common_confusion']}")

        w = c.get("if_wrong") or {}
        if w:
            tag = "고객 금전손실 가능" if w.get("customer_loss") else "금전손실 없음"
            st.error(f"**틀리면 생기는 일 ({tag})**\n\n{w.get('detail','')}")

        if c.get("qa_checks"):
            st.markdown("✅ **QA 확인 포인트**")
            for chk in c["qa_checks"]:
                st.markdown(f"- {chk}")

        q = c.get("quiz") or {}
        if q:
            st.divider()
            st.markdown(f"❓ **판단 퀴즈** — {q.get('q','')}")
            if hide_answer:
                with st.expander("답 보기"):
                    st.success(q.get("a", ""))
            else:
                st.success(q.get("a", ""))

        st.divider()
        if c.get("next_level_hook"):
            st.caption(f"다음 레벨 예고 · {c['next_level_hook']}")
        if c.get("simplified_away"):
            st.caption("이 설명에서 일부러 생략한 것 · "
                       + ", ".join(c["simplified_away"]))

        checked = st.checkbox("이 카드 이해했음", value=c["id"] in st.session_state.done,
                              key=f"chk_{c['id']}")
        if checked:
            st.session_state.done.add(c["id"])
        else:
            st.session_state.done.discard(c["id"])

        col1, col2 = st.columns(2)
        if col1.button("← 이전", use_container_width=True, disabled=idx == 0):
            st.session_state[key] = idx - 1
            st.rerun()
        if col2.button("다음 →", use_container_width=True,
                       disabled=idx >= len(cards) - 1):
            st.session_state[key] = idx + 1
            st.rerun()

# ---------------- 졸업 조건 ----------------
with tab_grad:
    st.markdown("이 문장들을 남에게 설명할 수 있으면 다음 레벨로 넘어갑니다.")
    for i, g in enumerate(lv["meta"].get("graduation", []), 1):
        st.markdown(f"**{i}.** {g}")
    st.caption("설명이 막히는 문장이 있으면 해당 카드로 돌아가세요.")

# ---------------- 면접 질문 ----------------
with tab_itv:
    if lv["interview"]:
        st.markdown("이 레벨을 이해하면 답할 수 있는 질문입니다.")
        for qq in lv["interview"]:
            st.markdown(f"- {qq}")
    else:
        st.info("등록된 질문이 없습니다.")

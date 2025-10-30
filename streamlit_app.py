import streamlit as st
import pandas as pd
import json
from datetime import datetime
from app import RFPAnalyzer
import fitz  # PyMuPDF
import docx  # python-docx

# 페이지 설정 및 세션 상태 초기화
st.set_page_config(page_title="RFP 분석 대시보드", layout="wide")

if "search_history" not in st.session_state:
    st.session_state.search_history = []

st.title("RFP 분석 자동화 — Streamlit UI")

st.markdown(
    """
    이 UI는 Azure Search에서 관련 문서를 찾아 Azure OpenAI로부터 구조화된 요약을 생성합니다.
    
    ### 기능
    - 🔍 문서 검색 및 AI 기반 분석
    - 💡 키워드 하이라이트
    - 📊 검색 결과 정렬/필터링
    - 💾 JSON 형식으로 결과 저장
    - 📜 검색 히스토리 관리
    """
)

def highlight_text(text, keywords):
    """텍스트 내 키워드를 하이라이트"""
    if not text or not keywords:
        return text
    
    highlighted = text
    for kw in keywords:
        if kw and kw in str(highlighted):
            highlighted = str(highlighted).replace(
                kw, f"**:red[{kw}]**"
            )
    return highlighted

def save_to_json(data, filename_prefix="rfp_search"):
    """검색 결과를 JSON 파일로 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename

def extract_pdf_text(file):
    """PDF 파일에서 텍스트 추출"""
    try:
        with fitz.open(stream=file) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        return f"(PDF 파싱 오류: {e})"

def extract_docx_text(file):
    """DOCX 파일에서 텍스트 추출"""
    try:
        doc = docx.Document(file)
        text = "\n".join([p.text for p in doc.paragraphs])
        return text
    except Exception as e:
        return f"(DOCX 파싱 오류: {e})"

with st.sidebar:
    st.header("⚙️ 설정")
    
    # 검색 설정
    st.subheader("검색 옵션")
    top_n = st.number_input("가져올 문서 수 (top N)", min_value=1, max_value=20, value=5)
    
    # 키워드 하이라이트
    st.subheader("키워드 하이라이트")
    highlight_keywords = st.text_input(
        "하이라이트할 키워드 (쉼표로 구분)",
        placeholder="예: AI, 클라우드, 보안"
    ).split(",")
    highlight_keywords = [k.strip() for k in highlight_keywords if k.strip()]
    
    # 정렬 옵션
    st.subheader("정렬 옵션")
    sort_by = st.selectbox(
        "정렬 기준",
        ["연관도", "중요도", "프로젝트명"],
        index=0
    )
    
    # 필터 옵션
    st.subheader("필터")
    min_importance = st.slider("최소 중요도", 0.0, 1.0, 0.0)
    
    # 실행 버튼
    run_button = st.button("🔍 검색 실행")

# 검색 히스토리
if st.session_state.search_history:
    with st.expander("📜 검색 히스토리"):
        for hist in st.session_state.search_history[-5:]:  # 최근 5개만
            st.text(f"[{hist['timestamp']}] {hist['query'][:50]}...")

# 쿼리 입력 섹션
st.header("📝 쿼리 입력")

col1, col2 = st.columns([3, 1])

with col2:
    # define default query here so it's available to the button handler before text_area
    query_default = (
        "RFP 문서를 참고해서 사업명, 사업기간, 사업목적, 사업범위, 핵심기술, 고객사명, "
        "사업설명회날짜, 입찰일자, PT발표일, 우선협상대상자 선정 발표일, 제약사항을 알려주세요."
    )

    # 기본 쿼리 불러오기 동작: 버튼 클릭 시 session_state에 기록
    if st.button("📋 기본 쿼리 불러오기", help="클릭하면 기본 쿼리를 프롬프트에 채웁니다", key="prefill_button"):
        st.session_state.query = query_default
        st.session_state.prefilled = True

    # 보여진 기본쿼리로 즉시 실행할지 옵션 (기본 쿼리를 불러온 경우에만 표시)
    # 쿼리 실행 버튼은 항상 표시
    if st.button("🚀 쿼리 실행", key="execute_loaded_query", help="현재 입력된 쿼리로 검색을 실행합니다."):
        st.session_state.use_default_execute = True
    else:
        st.session_state.use_default_execute = False

with col1:
    # 텍스트 영역은 세션 상태 'query'를 사용하여 동적으로 업데이트 가능하게 만듭니다.
    if "query" not in st.session_state:
        st.session_state.query = ""

    # text_area는 key를 사용하여 상태를 자동으로 관리합니다.
    query = st.text_area("사용자 질문/쿼리", value=st.session_state.get("query", ""), key="query", height=160, placeholder="여기에 질문을 입력하세요...")

# 실행 결과를 보여줄 컨테이너
results_container = st.container()

# 검색 실행 섹션: 검색만 수행하고 문서 목록을 먼저 표시합니다 (LLM 호출은 별도)
# 실행 조건: 일반 실행 버튼 또는 (기본쿼리(prefill) 후 기본쿼리로 즉시 실행 옵션 체크)
use_prefill_and_execute = st.session_state.get("prefilled", False) and st.session_state.get("use_default_execute", False)
if run_button or use_prefill_and_execute:
    with results_container:
        if not query.strip():
            st.error("🚫 쿼리를 입력하거나 기본 쿼리를 선택해주세요.")
        else:
            with st.spinner("🔄 검색 중... Azure Search 호출을 실행합니다"):
                try:
                    analyzer = RFPAnalyzer()
                    raw_docs = analyzer.search(query, top=int(top_n))

                    # Convert to plain dicts for session storage and display
                    raw_docs = [dict(d) for d in raw_docs]

                    # 검색 히스토리 저장
                    st.session_state.search_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "query": query,
                        "n_results": len(raw_docs)
                    })

                    # Prepare display-friendly docs (Korean keys)
                    docs_list = []
                    for d in raw_docs:
                        doc_dict = {
                            "프로젝트명": d.get("projectName"),
                            "중요도": float(d.get("importance", 0) or 0),
                            "기능요구사항": d.get("functionalRequirements"),
                            "비기능요구사항": d.get("nonFunctionalRequirements"),
                            "기술요구사항": d.get("technicalRequirements"),
                            "스킬셋": d.get("skillsets", []),
                            "본문": d.get("chunk")
                        }
                        if float(doc_dict["중요도"]) >= min_importance:
                            docs_list.append(doc_dict)

                    # 정렬 적용
                    if docs_list:
                        if sort_by == "중요도":
                            docs_list.sort(key=lambda x: x["중요도"], reverse=True)
                        elif sort_by == "프로젝트명":
                            docs_list.sort(key=lambda x: x["프로젝트명"] or "")

                    # 저장: 원본(raw_docs)과 표시용(docs_list)
                    st.session_state.last_raw_docs = raw_docs
                    st.session_state.last_display_docs = docs_list

                    st.success(f"✅ 검색 완료 — {len(docs_list)}개 문서를 찾았습니다.")

                except Exception as e:
                    st.error(f"❌ 검색 중 오류가 발생했습니다: {str(e)}")
                    if "Missing Azure" in str(e):
                        st.warning("⚠️ 환경 변수가 설정되어 있는지 확인해주세요.")

# 문서가 있으면 표시
if "last_display_docs" in st.session_state and st.session_state.last_display_docs:
    st.subheader("📑 검색된 문서 (요약)")
    for i, d in enumerate(st.session_state.last_display_docs, start=1):
        with st.expander(f"문서 {i}: {d['프로젝트명'] or '제목 없음'} | 중요도: {d['중요도']:.2f}"):
            cols = st.columns(2)
            with cols[0]:
                st.markdown("### 요구사항")
                st.markdown("**🔹 기능 요구사항**")
                st.markdown(highlight_text(d["기능요구사항"], highlight_keywords))
                st.markdown("**🔹 비기능 요구사항**")
                st.markdown(highlight_text(d["비기능요구사항"], highlight_keywords))
                st.markdown("**🔹 기술 요구사항**")
                st.markdown(highlight_text(d["기술요구사항"], highlight_keywords))
            with cols[1]:
                st.markdown("### 스킬셋 및 본문")
                if d["스킬셋"]:
                    st.markdown("**🔹 필요 스킬**")
                    skillset_str = ", ".join(d["스킬셋"]) if isinstance(d["스킬셋"], list) else str(d["스킬셋"])
                    st.markdown(highlight_text(skillset_str, highlight_keywords))
                st.markdown("**🔹 본문 내용**")
                st.markdown(highlight_text(d["본문"], highlight_keywords))

    # --- 추가 파일 업로드 섹션 (AI 분석 위) ---
    st.markdown("---")
    st.subheader("📎 추가 문서 업로드 (선택사항)")
    uploaded_files = st.file_uploader(
        "분석에 포함할 추가 문서를 선택하세요 (여러 파일 선택 가능)",
        accept_multiple_files=True,
        type=['txt', 'pdf', 'docx']
    )
    uploaded_docs = []
    if uploaded_files:
        for file in uploaded_files:
            if file.type == "text/plain":
                content = file.read().decode("utf-8")
            elif file.type == "application/pdf":
                content = extract_pdf_text(file)  # 실제 PDF 파싱은 별도 구현 필요
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                content = extract_docx_text(file)  # 실제 DOCX 파싱은 별도 구현 필요
            else:
                content = "(알 수 없는 파일 형식)"
            uploaded_docs.append({
                "프로젝트명": file.name,
                "chunk": content,
                "기능요구사항": "",
                "비기능요구사항": "",
                "기술요구사항": "",
                "스킬셋": [],
                "중요도": 0.0
            })
        st.session_state.uploaded_docs = uploaded_docs
    else:
        st.session_state.uploaded_docs = []

    # --- LLM 프롬프트 입력 및 실행 섹션 ---
    st.markdown("---")
    st.header("🤖 AI 분석")
    st.write("검색된 문서와 업로드된 문서를 기반으로 LLM에게 추가 질의를 하려면 아래에 질문을 입력하고 'AI 분석 생성' 버튼을 누르세요.")
    llm_prompt = st.text_area("LLM에 보낼 질문/프롬프트", value="RFP 문서를 참고하여 주요 요구사항을 요약해 주세요.", height=120)
    # 기존 검색 문서 + 업로드 문서 합치기
    all_docs = st.session_state.get("last_raw_docs", []) + st.session_state.get("uploaded_docs", [])
    doc_labels = []
    filtered_docs = []
    for i, doc in enumerate(all_docs):
        label = doc.get("프로젝트명") or doc.get("projectName")
        if label:  # 문서명이 있으면만 옵션에 추가
            doc_labels.append(label)
            filtered_docs.append(doc)
            
    selected_labels = st.multiselect(
        "분석에 포함할 문서 선택",
        options=doc_labels,
        default=doc_labels,
        help="분석에 포함할 문서를 선택하세요. 기본적으로 모든 문서가 선택됩니다."
    )
    selected_docs = [doc for doc, label in zip(all_docs, doc_labels) if label in selected_labels]
    
    
    gen_button = st.button("🧠 AI 분석 생성")

    if gen_button:
        if not llm_prompt.strip():
            st.error("질문을 입력해주세요.")
        else:
            with st.spinner("LLM 호출 중... 잠시 기다려 주세요"):
                try:
                    analyzer = RFPAnalyzer()
                    response_text = analyzer.generate_from_documents(selected_docs, prompt=llm_prompt)
                    st.subheader("🤖 LLM 응답")
                    st.info(highlight_text(response_text, highlight_keywords))
                    st.session_state.last_llm_response = response_text
                except Exception as e:
                    st.error(f"LLM 호출 중 오류가 발생했습니다: {e}")
else:
    st.info("검색을 먼저 실행하면 문서 목록이 여기 표시됩니다. 그 다음 LLM에 질문을 보내 추가 분석을 받을 수 있습니다.")

st.markdown("---")
st.caption("환경변수: AZURE_SEARCH_API_KEY, AZURE_SEARCH_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_DEPLOYMENT_MODEL 필요")
# 📊 RFP 분석 자동화 시스템

<!-- [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()
[![Status](https://img.shields.io/badge/Stage-Development-orange.svg)]() -->

테스트 URL : https://project-ktds706.azurewebsites.net/

## 목차
- [프로젝트 개요](#프로젝트-개요)
- [핵심 기능](#핵심-기능)
- [기술 스택](#기술-스택)
- [시스템 아키텍처](#시스템-아키텍처)
- [전체 구조](#전체-구조)
- [폴더 구조](#폴더-구조)
- [실행 방법](#실행-방법)

## 프로젝트 개요
**RFP(Request for Proposal)** 문서에서 핵심 요구사항을 자동으로 추출하고,  
사전 분석 데이터를 기반으로 **PRE-ORB(Preliminary Opertunity Review Board)** 단계에서 활용 가능한 엑셀 보고서를 자동 생성하는 **분석 자동화 시스템**입니다.

### 🎯 목표
- RFP 문서의 **정량·정성적 분석 자동화**  
- 요구사항 분류 및 **가중치 기반 중요도 평가**  
- PRE-ORB용 **표준 엑셀 산출물 자동 생성**

---

## 핵심 기능

### 🧠 RFP 문서 분석
- PDF, Word 등 다양한 포맷의 문서를 NLP 기반으로 자동 분석  
- 주요 키워드, 요구사항, 제안 항목을 **자동 분류 및 정리**

### 📈 PRE-PRB 엑셀 자동 생성
- 사전 분석 데이터를 기반으로 **엑셀 리포트 자동 생성**  
- 표준 템플릿을 활용하여 **형식 일관성 유지**  

### 🌐 Streamlit 웹 인터페이스
- 직관적인 웹 기반 사용자 인터페이스
- 검색 결과와 AI 생성 응답을 단계별로 확인 가능
- 문서 검색 및 분석 결과를 실시간으로 시각화

---

## 기술 스택

| 구분       | 사용 기술 |
|-------------|------------|
| **FrontEnd** | 🚀 Streamlit |
| **BackEnd** | 🐍 Python 3.11+ |
| **Azure AI** | Azure OpenAI (GPT-4.1)<br>Azure AI Search<br>Azure Blob Storage
| **문서 처리** | PyMuPDF · pdfplumber · python-docx |
| **엑셀문서 생성** |  openpyxl |
| **개발환경** | VS Code · Jupyter Notebook |
| **형상관리** | Git · GitHub |


---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                     │
├─────────────────────────────────────────────────────────┤
│  🏠 메인 │ 📊 RFP 분석 │  문서 업로드  | 문서 다운로드      |    
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                     Python Backend                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│Azure OpenAI        │ AI Search              │   Blob    │
│   GPT-4.1          │                        │   Storage │
└─────────────────────────────────────────────────────────┘
```

## 전체 구조
```text
RFP 문서 → 텍스트 전처리 → NLP 분석 → 요구사항 추출 → 엑셀 자동생성

🔄 데이터 흐름

입력: 사용자가 업로드한 RFP 문서 (PDF/Word) + 추가 사전 분석 자료
처리: 텍스트 추출 → 자연어 분석 → 핵심 요구사항 분류 -> Template 항목에 맞도록 분류
출력: PRE-ORB 분석용 Excel 파일 (Pre-ORB_사업명_YYMMDD_v0.1.xlsx) 자동 생성
```
## 폴더 구조
```text
project-ktds706/
├── app.py                # RFPAnalyzer 클래스 및 백엔드 로직
├── streamlit_app.py      # Streamlit 기반 웹 UI
├── requirements.txt      # Python 패키지 목록
├── README.md             # 프로젝트 설명 파일
├── .gitignore            # Git 제외 파일 목록
├── files/                # 샘플 데이터 및 업로드 파일 저장 폴더
├── rfp_search_*.json     # 검색 결과 JSON 파일
├── create_search_index.py# Azure Search 인덱스 생성 스크립트
├── run_indexer_and_show_status.py # 인덱서 실행 및 상태 확인
├── upload_sample_data.py # 샘플 데이터 업로드 스크립트
├── streamlit.sh          # 리눅스/배포용 실행 스크립트
└── __pycache__/          # 파이썬 캐시 폴더
```

## 실행 방법

### 1. 환경 설정
```bash
# 필요한 패키지 설치
pip install -r requirements.txt
```

### 2. 실행
```

#### Streamlit UI 모드
```bash
streamlit run streamlit_app.py
```



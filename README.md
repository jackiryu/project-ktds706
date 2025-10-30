# 📊 RFP 분석 자동화 시스템

<!-- [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()
[![Status](https://img.shields.io/badge/Stage-Development-orange.svg)]() -->

테스트 URL : https://project-ktds706.azurewebsites.net/

## 📋 목차
- [프로젝트 개요](#-프로젝트-개요)
- [핵심 기능](#-핵심-기능)
- [기술 스택](#-기술-스택)
- [시스템 아키텍처](#-시스템-아키텍처)
- [전체 구조](#-전체-구조)

## 📘 프로젝트 개요
**RFP(Request for Proposal)** 문서에서 핵심 요구사항을 자동으로 추출하고,  
사전 분석 데이터를 기반으로 본부내 자체 **PRE-PRB(Preliminary Proposal Review Board)** 단계에서 활용 가능한  
엑셀 보고서를 자동 생성하는 **분석 자동화 시스템**입니다.

### 🎯 목표
- RFP 문서의 **정량·정성적 분석 자동화**  
- 요구사항 분류 및 **가중치 기반 중요도 평가**  
- PRE-PRB용 **표준 엑셀 산출물 자동 생성**

---

## ⚙️ 핵심 기능

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

## 💻 기술 스택

| 구분       | 사용 기술 |
|-------------|------------|
| **FrontEnd** | 🚀 Streamlit |
| **BackEnd** | 🐍 Python 3.11+ |
| **Azure AI** | Azure OpenAI (GPT-4.1)<br>Azure AI Search<br>Azure Blob Storage
| **문서 처리** | PyMuPDF · pdfplumber |
| **엑셀문서 생성** | python-docx |
| **개발환경** | VS Code · Jupyter Notebook |
| **형상관리** | Git · GitHub |


---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                     │
├─────────────────────────────────────────────────────────┤
│  🏠 메인  │ 📊 RFP 분석 │ 💡 인사이트 │ 🛠️ 품질관리      │
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

### 🗂️ 전체 구조
```text
RFP 문서 → 텍스트 전처리 → NLP 분석 → 요구사항 추출 → 엑셀 자동생성

🔄 데이터 흐름

입력: 사용자가 업로드한 RFP 문서 (PDF/Word)
처리: 텍스트 추출 → 자연어 분석 → 핵심 요구사항 분류
출력: PRE-PRB 분석용 Excel 파일 (Pre-ORB_사업명_YYMMDD_v0.1.xlsx) 자동 생성
```

## 🚀 실행 방법

### 1. 환경 설정
```bash
# 필요한 패키지 설치
pip install -r requirements.txt
```

### 2. 실행

#### CLI 모드
```bash
python app.py "검색어" --top 5
```

#### Streamlit UI 모드
```bash
streamlit run streamlit_app.py
```

## 💻 API 사용 예시

### RFPAnalyzer 클래스 사용
```python
from app import RFPAnalyzer

# RFPAnalyzer 인스턴스 생성
analyzer = RFPAnalyzer()

# 검색 및 분석 수행
documents, response = analyzer.search_and_generate("검색어", top=5)

# 검색만 수행
documents = analyzer.search("검색어", top=5)

# 문서 기반 응답 생성
response = analyzer.generate_from_documents(documents, "검색어")

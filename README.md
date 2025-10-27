# 📊 RFP 분석 및 사전 분석을 통한 PRE-PRB 엑셀자료 만들기

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()
[![Status](https://img.shields.io/badge/Stage-Development-orange.svg)]()

---

## 📘 프로젝트 개요

### 🔍 목적  
**RFP(Request for Proposal)** 문서에서 핵심 요구사항을 자동으로 추출하고,  
사전 분석 데이터를 기반으로 **PRE-PRB(Preliminary Proposal Review Board)** 단계에서 활용 가능한  
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

---

## 💻 기술 스택

| 구분 | 사용 기술 |
|------|------------|
| **언어** | 🐍 Python 3.11+ |
| **데이터 처리** | Pandas · OpenPyXL |
| **문서 처리** | PyMuPDF · docx2txt |
| **자연어 처리** | NLTK · spaCy |
| **개발환경** | VS Code · Jupyter Notebook |
| **형상관리** | Git · GitHub |
| **컨테이너(선택)** | Docker |

---

## 🏗️ 시스템 아키텍처

### 🗂️ 전체 구조
```text
RFP 문서 → 텍스트 전처리 → NLP 분석 → 요구사항 추출 → 엑셀 자동생성

🔄 데이터 흐름

입력: 사용자가 업로드한 RFP 문서 (PDF/Word)
처리: 텍스트 추출 → 자연어 분석 → 핵심 요구사항 분류
출력: PRE-PRB 분석용 Excel 파일 (pre_prb_result.xlsx) 자동 생성
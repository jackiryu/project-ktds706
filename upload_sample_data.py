from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
INDEX_NAME = "rfp-syryu-obj"

# Initialize the search client
search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
)

# Sample RFP document
sample_doc = {
    "id": "RFP001",
    "fileName": "전자계약시스템_구축_RFP.pdf",
    "fileUrl": "https://storage.example.com/rfp001.pdf",
    "uploadDate": "2025-10-29T00:00:00Z",
    "projectName": "전자계약시스템 구축 프로젝트",
    "projectSummary": "클라우드 기반 전자계약 시스템 구축",
    "clientName": "한국은행",
    "budget": 500000000.0,
    "projectDuration": 6,
    "projectStartDate": "2026-01-01T00:00:00Z",
    "projectEndDate": "2026-06-30T00:00:00Z",
    "functionalRequirements": "전자계약 생성 및 관리, 전자서명 기능, 계약 승인 워크플로우, 계약서 템플릿 관리, 계약 이력 관리",
    "nonFunctionalRequirements": "시스템 응답시간 3초 이내, 99.9% 시스템 가용성, 동시 사용자 1000명 지원",
    "technicalRequirements": "클라우드 네이티브 아키텍처, PKI 기반 전자서명, OAuth 2.0 인증",
    "requirementCategories": "전자계약, 보안, 클라우드",
    "keyKeywords": "전자계약, 전자서명, 클라우드, 워크플로우",
    "skillsets": ["Python", "Azure", "PKI", "OAuth 2.0"],
    "importance": 0.85,
    "analysisNotes": "디지털 전환 핵심 프로젝트",
    "constraints": "금융보안 규정 준수 필수, 감사 추적 기능 필수"
}

try:
    result = search_client.upload_documents([sample_doc])
    print(f"Uploaded {len(result)} documents")
    print("Upload completed successfully")
except Exception as e:
    print(f"Error during upload: {str(e)}")
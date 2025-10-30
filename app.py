"""App module exposing an RFPAnalyzer class that performs Azure Search + Azure OpenAI
queries and returns both the raw documents and the model response.

This file keeps a CLI-friendly behavior when executed directly.
"""

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from openai import AzureOpenAI
import os
import sys
from dotenv import load_dotenv
from typing import List, Tuple, Any

load_dotenv()

# Environment variables (expected to be set in .env or environment)
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT_MODEL = os.getenv("AZURE_DEPLOYMENT_MODEL")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "rfp-syryu-obj")


GROUNDED_PROMPT = """
당신은 RFP 문서를 분석하고 요구사항을 추출하는 전문가입니다.
아래 제공된 소스 정보만을 사용하여 질문에 답변하세요.
답변은 명확하고 구조화된 형식으로 작성하며, 제공된 소스에 없는 내용은 생성하지 마세요.
정보가 부족한 경우 "정보가 충분하지 않습니다"라고 답변하세요.

Query: {query}
Sources:\n{sources}
"""


class RFPAnalyzer:
    """Initializes Azure Search and Azure OpenAI clients and provides a single
    entry point to search the index and generate a grounded response.

    Methods
    -------
    search_and_generate(query, top=5) -> (documents_list, response_text)
    """

    def __init__(self, *, index_name: str = INDEX_NAME, model: str = AZURE_DEPLOYMENT_MODEL):
        # Validate minimal env
        if not AZURE_SEARCH_API_KEY or not AZURE_SEARCH_ENDPOINT:
            raise ValueError("Missing Azure Search configuration in environment variables")

        if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT or not model:
            raise ValueError("Missing Azure OpenAI configuration in environment variables")

        try:
            self.search_credential = AzureKeyCredential(AZURE_SEARCH_API_KEY)
            self.openai_client = AzureOpenAI(
                api_version="2023-12-01-preview",
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_API_KEY,
            )

            self.search_client = SearchClient(
                endpoint=AZURE_SEARCH_ENDPOINT,
                index_name=index_name,
                credential=self.search_credential,
            )  # type: ignore

            self.model = model

        except ClientAuthenticationError as auth_error:
            raise RuntimeError("Authentication error - check API keys and endpoints") from auth_error
        except HttpResponseError as http_error:
            raise RuntimeError("HTTP error while initializing clients") from http_error
        except Exception as e:
            raise RuntimeError("Unexpected error initializing clients") from e

    def _format_sources(self, documents: List[Any]) -> str:
        parts = []
        for doc in documents:
            # normalize skillsets
            skillsets_value = doc.get("skillsets", [])
            if isinstance(skillsets_value, str):
                skillsets_list = [skillsets_value]
            elif skillsets_value is None:
                skillsets_list = []
            else:
                try:
                    skillsets_list = list(skillsets_value)
                except Exception:
                    skillsets_list = [str(skillsets_value)]

            part = (
                f'프로젝트명: {doc.get("projectName")}\n'
                f'기능 요구사항: {doc.get("functionalRequirements")}\n'
                f'비기능 요구사항: {doc.get("nonFunctionalRequirements")}\n'
                f'기술 요구사항: {doc.get("technicalRequirements")}\n'
                f'중요도: {doc.get("importance")}\n'
                f'스킬셋: {", ".join(skillsets_list)}\n'
                f'본문(Chunk): {doc.get("chunk") if doc.get("chunk") is not None else ""}\n'
            )
            parts.append(part)

        return "\n".join(parts)

    def search_and_generate(self, query: str, top: int = 5, select: str = None) -> Tuple[List[Any], str]:
        """Search the Azure Search index and produce a grounded LLM response.

        Returns
        -------
        documents_list : list
            Raw documents returned by Azure Search (as dict-like objects)
        response_text : str
            Generated text from Azure OpenAI
        """

        # For backward compatibility, perform search then generate LLM response
        documents = self.search(query, top=top, select=select)
        response_text = self.generate_from_documents(documents, prompt=query)
        return documents, response_text

    def search(self, query: str, top: int = 5, select: str = None) -> List[Any]:
        """Execute only the Azure Search query and return documents (no LLM call)."""
        select = select or "projectName,functionalRequirements,nonFunctionalRequirements,technicalRequirements,importance,skillsets,chunk"

        try:
            search_results = self.search_client.search(
                search_text=query,
                top=top,
                select=select,  # type: ignore
            )
            documents = list(search_results)
        except Exception as e:
            raise RuntimeError("Error during search") from e

        return documents

    def generate_from_documents(self, documents: List[Any], prompt: str) -> str:
        """Given a list of documents (dict-like) and a prompt, produce the LLM response.

        This separates the expensive LLM call from the search step so the UI can
        present documents first and call the model only when requested.
        """
        sources_formatted = self._format_sources(documents)

        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": GROUNDED_PROMPT.format(query=prompt, sources=sources_formatted),
                    }
                ],
            )

            response_text = response.choices[0].message.content
        except Exception as e:
            raise RuntimeError("Error generating LLM response") from e

        return response_text


if __name__ == "__main__":
    # default query used in both CLI and Streamlit UI
    default_query = (
        "RFP 문서를 참고해서 사업명, 사업기간, 사업목적, 사업범위, "
        "핵심기술, 고객사명, 사업설명회날짜, 입찰일자, PT발표일, 우선협상대상자 선정 발표일, "
        "제약사항을 알려주세요. 단, 해당항목이 없을 경우에는 내용 없음으로 답변해주세요"
    )

    # If user explicitly asks for CLI mode, keep the old behavior
    if "--cli" in sys.argv:
        try:
            analyzer = RFPAnalyzer()
            docs, resp = analyzer.search_and_generate(default_query, top=5)
            print(f"Found {len(docs)} documents matching the query.")
            print("\n--- SOURCES ---\n")
            print(analyzer._format_sources(docs))
            print("\n--- MODEL RESPONSE ---\n")
            print(resp)
        except Exception as e:
            print(str(e))
            sys.exit(1)
    else:
        # Try to run as a Streamlit app. Import Streamlit lazily so CLI mode
        # still works when Streamlit isn't installed.
        try:
            import streamlit as st
        except Exception:
            # Fall back to CLI behavior if Streamlit is not available
            try:
                analyzer = RFPAnalyzer()
                docs, resp = analyzer.search_and_generate(default_query, top=5)
                print(f"Found {len(docs)} documents matching the query.")
                print("\n--- SOURCES ---\n")
                print(analyzer._format_sources(docs))
                print("\n--- MODEL RESPONSE ---\n")
                print(resp)
            except Exception as e:
                print(str(e))
                sys.exit(1)
        else:
            # Streamlit UI: only call the LLM when the user presses the button.
            st.set_page_config(page_title="RFP Analyzer", layout="wide")
            st.title("RFP Analyzer — 검색 및 LLM 생성 (버튼 클릭 시 실행)")

            st.markdown("아래에 질의를 작성한 뒤 '질문' 버튼을 눌러 검색과 모델 생성을 실행하세요. 앱 시작 시 자동으로 실행되지 않습니다.")

            query = st.text_area("질의 (Query)", value=default_query, height=160)
            top = st.number_input("Top 문서 수", min_value=1, max_value=50, value=5, step=1)

            # Cache the analyzer instance so it isn't re-created on every run
            @st.cache_resource
            def _get_analyzer():
                return RFPAnalyzer()

            analyzer = None

            if st.button("질문"):
                analyzer = _get_analyzer()
                try:
                    with st.spinner("검색 및 모델 응답 생성 중... 잠시 기다려주세요..."):
                        docs, resp = analyzer.search_and_generate(query, top=top)

                    st.success(f"{len(docs)}개의 문서가 검색되었습니다.")
                    with st.expander("Sources (검색 결과 원문 보기)"):
                        st.text(analyzer._format_sources(docs))

                    st.subheader("Model Response")
                    st.write(resp)
                except Exception as e:
                    st.error(f"오류 발생: {e}")
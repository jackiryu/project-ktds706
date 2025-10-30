from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    ComplexField,
    CorsOptions
)
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
INDEX_NAME = "rfp-syryu-obj"

# Initialize the search index client
search_client = SearchIndexClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
)

# Define the index
index = SearchIndex(
    name=INDEX_NAME,
    fields=[
    # Base Fields
    # Note: key field must be Edm.String and use the keyword analyzer for projections
    SearchableField(name="id", type=SearchFieldDataType.String, key=True, analyzer_name="keyword", filterable=True),
        SearchableField(name="fileName", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="fileUrl", type=SearchFieldDataType.String),
        SimpleField(name="uploadDate", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),

        # Project Information Fields
        SearchableField(name="projectName", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="projectSummary", type=SearchFieldDataType.String, analyzer_name="ko.microsoft"),
        SearchableField(name="clientName", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="budget", type=SearchFieldDataType.Double, filterable=True, sortable=True),
        SimpleField(name="projectDuration", type=SearchFieldDataType.Int32, filterable=True),
        SimpleField(name="projectStartDate", type=SearchFieldDataType.DateTimeOffset, filterable=True),
        SimpleField(name="projectEndDate", type=SearchFieldDataType.DateTimeOffset, filterable=True),

        # Requirements as a collection of complex objects (one item per RFP requirement)
        ComplexField(name="requirements", fields=[
            SearchableField(name="reqId", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="reqType", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="text", type=SearchFieldDataType.String, analyzer_name="ko.microsoft"),
            SearchableField(name="acceptanceCriteria", type=SearchFieldDataType.String, analyzer_name="ko.microsoft"),
            SimpleField(name="priority", type=SearchFieldDataType.Double, filterable=True),
            SimpleField(name="estimatedEffort", type=SearchFieldDataType.Double, filterable=True),
            SimpleField(name="sourcePage", type=SearchFieldDataType.Int32, filterable=True),
            SearchableField(name="stakeholders", type=SearchFieldDataType.Collection(SearchFieldDataType.String), analyzer_name="ko.microsoft", filterable=True),
            SearchableField(name="dependencies", type=SearchFieldDataType.Collection(SearchFieldDataType.String), analyzer_name="ko.microsoft", filterable=True),
            SearchableField(name="relatedReqIds", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True)
        ], collection=True),

        # Aggregated requirement fields (legacy/backwards compatible)
        SearchableField(name="functionalRequirements", type=SearchFieldDataType.Collection(SearchFieldDataType.String), analyzer_name="ko.microsoft"),
        SearchableField(name="nonFunctionalRequirements", type=SearchFieldDataType.Collection(SearchFieldDataType.String), analyzer_name="ko.microsoft"),
        SearchableField(name="technicalRequirements", type=SearchFieldDataType.Collection(SearchFieldDataType.String), analyzer_name="ko.microsoft"),
        SearchableField(name="requirementCategories", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),

        # Analysis Fields
        SearchableField(name="keyKeywords", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
        # Skillsets (collection) for faceting/filtering by skill
        SearchableField(name="skillsets", type=SearchFieldDataType.Collection(SearchFieldDataType.String), analyzer_name="ko.microsoft", filterable=True),
        SimpleField(name="importance", type=SearchFieldDataType.Double, filterable=True, sortable=True),
        SearchableField(name="analysisNotes", type=SearchFieldDataType.String, analyzer_name="ko.microsoft"),
        SearchableField(name="constraints", type=SearchFieldDataType.Collection(SearchFieldDataType.String), analyzer_name="ko.microsoft"),
        SearchableField(name="regulatoryRequirements", type=SearchFieldDataType.Collection(SearchFieldDataType.String), analyzer_name="ko.microsoft", filterable=True),
        SearchableField(name="technicalStack", type=SearchFieldDataType.Collection(SearchFieldDataType.String), analyzer_name="ko.microsoft", filterable=True),
        SearchableField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), analyzer_name="ko.microsoft", filterable=True),
        SearchableField(name="riskFactors", type=SearchFieldDataType.Collection(SearchFieldDataType.String), analyzer_name="ko.microsoft")
    ],
    cors_options=CorsOptions(allowed_origins=["*"])
)

try:
    # Delete the index if it exists
    if INDEX_NAME in [index.name for index in search_client.list_indexes()]:
        search_client.delete_index(INDEX_NAME)
        print(f"Deleted existing index '{INDEX_NAME}'")
    
    # Create the new index
    result = search_client.create_index(index)
    print(f"Created index '{result.name}' successfully")
    print("\nIndex fields:")
    for field in result.fields:
        print(f"- {field.name} ({field.type})")

except Exception as e:
    print(f"Error creating index: {str(e)}")
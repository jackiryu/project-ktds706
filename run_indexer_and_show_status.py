from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
import os
from dotenv import load_dotenv
import time
import json

load_dotenv()
endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
INDEXER_NAME = "rfp-syryu-obj-indexer"

if not endpoint or not key:
    print("Missing AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_API_KEY in environment (.env).")
    raise SystemExit(1)

client = SearchIndexerClient(endpoint=endpoint, credential=AzureKeyCredential(key))

try:
    print(f"Resetting indexer '{INDEXER_NAME}'...")
    client.reset_indexer(INDEXER_NAME)
except Exception as e:
    print(f"Warning: reset_indexer failed: {e}")

try:
    print(f"Running indexer '{INDEXER_NAME}'...")
    client.run_indexer(INDEXER_NAME)
except Exception as e:
    print(f"Failed to start indexer run: {e}")
    raise SystemExit(1)

# Wait a short time then fetch status
print("Waiting 5 seconds for indexer job to initialize...")
time.sleep(5)

try:
    status = client.get_indexer_status(INDEXER_NAME)
    # status is SearchIndexerStatus
    # Print summary
    print('\n===== Indexer Status Summary =====')
    try:
        last_result = status.last_result
        if last_result:
            lr = {
                'status': getattr(last_result, 'status', None),
                'error_count': getattr(last_result, 'error_count', None),
                'warnings_count': getattr(last_result, 'warnings_count', None),
                'status_message': getattr(last_result, 'status_message', None),
                'start_time': getattr(last_result, 'start_time', None),
                'end_time': getattr(last_result, 'end_time', None)
            }
            print(json.dumps(lr, default=str, ensure_ascii=False, indent=2))
        else:
            print('No last_result available yet.')
    except Exception as e:
        print('Could not read last_result:', e)

    # Execution history may be available
    try:
        if hasattr(status, 'execution_history') and status.execution_history:
            print('\n===== Recent Execution History =====')
            for h in status.execution_history[-5:]:
                he = {k: getattr(h, k) for k in dir(h) if not k.startswith('_') and not callable(getattr(h, k))}
                print(json.dumps(he, default=str, ensure_ascii=False, indent=2))
        else:
            print('\nNo execution_history available yet.')
    except Exception as e:
        print('Could not read execution_history:', e)

except Exception as e:
    print(f"Failed to get indexer status: {e}")
    raise

print('\nDone.')

---
description: Auto-run the TransitFlow ADK development and testing loop
---

// turbo-all
1. Clear background Python processes
   `taskkill /F /IM python.exe /T`

2. Start the ADK FastAPI server
   `$env:PYTHONPATH="."; $env:OPIK_DISABLED="true"; uv run python -m app.main`

3. Run the ADK Orchestration dry-run test
   `$env:PYTHONPATH=".."; uv run python tests/test_adk_agent.py`

4. Verify results
   `Get-Content -Path "tests/adk_dry_run_results.txt"`

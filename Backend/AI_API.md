# AI API (Sprint 2)

The AI API uses only text supplied in the request. It does not query the article
database, fetch a URL, or store questions and article text. Ollama runs locally at
`OLLAMA_BASE_URL` (default `http://127.0.0.1:11434`); `OLLAMA_MODEL` defaults to
`llama3.2`. The model must already be installed. No model download is automatic.

## Summarize

`POST /ai/summarize`

```json
{
  "article_text": "The city opened a new library on Monday. It has two reading rooms.",
  "source_url": "https://example.org/library",
  "language": "en"
}
```

## Ask about the article

`POST /ai/ask`

```json
{
  "article_text": "The city opened a new library on Monday. It has two reading rooms.",
  "question": "When did the library open?",
  "source_url": "https://example.org/library",
  "language": "en"
}
```

Both endpoints return the same shape:

```json
{
  "text": "It opened on Monday.",
  "sources": ["https://example.org/library"],
  "uncertainty": "Only the supplied article was checked; other sources were not verified.",
  "status": "answered"
}
```

`sources` contains the submitted URL only, or `[]` when omitted; it is **not** an
independently verified citation. An unsupported question returns
`status: "insufficient_information"`, a clear explanation in `text` and
`uncertainty`, and no invented answer. Empty or over-limit inputs receive HTTP 422;
an unavailable model or invalid model response receives HTTP 503. The article limit
is 12,000 characters and the question limit is 500 characters. `language` is `en`
or `nl` and controls the output language.

Kristína's Nova UI already expects `text`, `sources`, and `uncertainty` from
`Frontend/src/utils/nova.ts`. Its current story IDs and source links are fictional,
so integration must pass real article text and, if available, its actual URL.
The UI should not claim multiple verified sources based on this single-article API.
Browser-to-API CORS or a Vite proxy must be agreed before cross-origin integration.

Run offline unit tests with `python -m pytest -c Backend/pytest.ini
Backend/tests/unit/logic/test_ai_service.py Backend/tests/unit/logic/test_ollama_client.py`.
Once Ollama is running and the configured model is installed, run the separate
manual smoke test with `python -m Backend.tests.manual.ai_ollama_smoke`.

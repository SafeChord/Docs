# Pinned: the strict link check (.ai-rules.md §2.2) depends on how MkDocs and its plugins behave.
FROM squidfunk/mkdocs-material:9.8.0

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

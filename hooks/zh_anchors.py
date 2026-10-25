"""Anchor links are checked on the en build only (.ai-rules.md §2.2)."""


def on_page_content(html, page, config, files):
    # zh trails en (.ai-rules.md §2.3): a stale zh page lacks the ids its en page has gained since.
    if not config.plugins["i18n"].is_default_language_build:
        page.links_to_anchors = {}
    return html

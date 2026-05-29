from src.prioritizer import Feedback, prioritize, roadmap_markdown, sentiment_score, tokenize


def test_tokenize_removes_small_words_and_stopwords():
    assert "export" in tokenize("Export the report to PDF")
    assert "the" not in tokenize("Export the report to PDF")


def test_sentiment_score_detects_negative_feedback():
    assert sentiment_score("The report is slow and confusing") < 0


def test_prioritize_groups_related_items():
    feedback = [
        Feedback("1", "teacher", "Export report to PDF is missing", 4, 5),
        Feedback("2", "teacher", "PDF export would be useful", 3, 5),
        Feedback("3", "admin", "Dashboard is slow", 5, 3),
    ]
    themes = prioritize(feedback)
    assert themes[0].count == 2
    assert "export" in themes[0].label or "pdf" in themes[0].label


def test_roadmap_markdown_has_ranked_sections():
    feedback = [Feedback("1", "teacher", "Export report to PDF is missing", 4, 5)]
    text = roadmap_markdown(prioritize(feedback))
    assert "# Prioritized Product Feedback" in text
    assert "Priority score" in text


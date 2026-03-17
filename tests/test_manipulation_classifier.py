import re


def test_safe_template_substitution_no_cross_contamination():
    """Verify that {ceo_corpus} inside conversation_log is NOT replaced."""
    template = "Log:\n{conversation_log}\n\nCEO:\n{ceo_corpus}"
    conversation_log = "The defender said: check the {ceo_corpus} for clues"
    ceo_corpus = "REAL_CEO_DATA"

    placeholders = {"conversation_log": conversation_log, "ceo_corpus": ceo_corpus}
    result = re.sub(
        r"\{(\w+)\}",
        lambda m: placeholders.get(m.group(1), m.group(0)),
        template,
    )

    assert "REAL_CEO_DATA" in result
    assert result.count("REAL_CEO_DATA") == 1
    assert "{ceo_corpus}" in result  # the one inside conversation_log is preserved

"""Slang dictionary for query rewriting (F7c)."""

from ragmotion.rewrite import expand_slang


def test_slang_dictionary_expands_longest_terms_first_and_whole_words_only():
    assert expand_slang("SL RDL for hamstrings") == "SL RDL (single-leg Romanian deadlift) for hamstrings"
    assert expand_slang("sl rdl") == "sl rdl (single-leg Romanian deadlift)"  # case-insensitive
    assert expand_slang("RFESS with DBs").endswith("with DBs (dumbbells)")  # plural before singular
    assert expand_slang("Sandbag carries") == "Sandbag carries"  # "SA" inside a word is left alone
    assert expand_slang("I only have dumbbells") == "I only have dumbbells"

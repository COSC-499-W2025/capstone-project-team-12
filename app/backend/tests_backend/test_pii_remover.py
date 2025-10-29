import re
import pytest
from pii_remover import remove_pii


def test_remove_basic_pii():
    """ redacts name and email while keeping other words"""
    docs = [["my", "name", "is", "John", "Lennon", "and", "email", "is", "john.lennon@example.com"]]
    result = remove_pii(docs)

    assert isinstance(result, list) # make sure is returning a list
    assert len(result) == 1
    string = " ".join(result[0])
    assert "john" not in string and "lennon" not in string
    assert "email" in string


def test_mixed_non_pii_text():
    """ leaves text without PII unchanged """
    docs = [["this", "text", "contains", "no", "pii", "data"]]
    result = remove_pii(docs)
    assert result == [["this", "text", "contains", "no", "pii", "data"]]


def test_multiple_documents():
    """ handles multiple docs correctly and returns same count """
    docs = [
        ["name", "is", "Alice", "and", "email", "alice@example.com"],
        ["contact", "bob@example.com", "tomorrow"]
    ]
    result = remove_pii(docs)
    assert len(result) == len(docs)


def test_empty_documents_list():
    """handles empty input gracefully """
    result = remove_pii([])
    assert result == []


def test_empty_string_document():
    """ handles an empty document (no tokens)"""
    result = remove_pii([[]])
    assert result == [[]]


def test_no_leftover_angle_brackets(): 
    """ there should not be any leftover tags likes <PERSON> after redaction"""
    docs = [["my", "name", "is", "John", "Doe"]]
    result = remove_pii(docs)
    string = " ".join(result[0])
    assert "<" not in string and ">" not in string
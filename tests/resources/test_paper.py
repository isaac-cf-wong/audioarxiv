from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from audioarxiv.resources.paper import (  # Replace with actual module name
    Paper, validate_paper_arguments)


@pytest.fixture
def mock_paper_object():
    mock_paper = MagicMock()
    mock_paper.title = "Test Title"
    mock_paper.summary = "This is a test abstract."

    author1 = MagicMock()
    author1.name = "Alice"
    author2 = MagicMock()
    author2.name = "Bob"
    mock_paper.authors = [author1, author2]

    mock_paper.published = datetime(2022, 1, 1)
    mock_paper.updated = datetime(2022, 1, 2)
    return mock_paper


@patch("audioarxiv.resources.paper.arxiv.Client")
def test_paper_init_and_client(mock_client_class):
    paper = Paper(page_size=200, delay_seconds=5.0, num_retries=2)
    client_instance = mock_client_class.return_value

    assert paper.client == client_instance
    mock_client_class.assert_called_with(page_size=200, delay_seconds=5.0, num_retries=2)


def test_validate_paper_arguments():
    args = validate_paper_arguments(page_size=150, delay_seconds=2.0, num_retries=5)
    assert args == {
        'page_size': 150,
        'delay_seconds': 2.0,
        'num_retries': 5
    }


@patch("audioarxiv.resources.paper.arxiv.Client")
def test_search_by_arxiv_id_and_properties(mock_client_class, mock_paper_object):
    mock_client = MagicMock()
    mock_client.results.return_value = iter([mock_paper_object])
    mock_client_class.return_value = mock_client

    paper = Paper()
    paper.search_by_arxiv_id("1234.5678")

    assert paper.title == "Test Title"
    assert paper.abstract == "This is a test abstract."
    assert paper.authors == ["Alice", "Bob"]
    assert paper.published == datetime(2022, 1, 1)
    assert paper.updated == datetime(2022, 1, 2)


@patch("audioarxiv.resources.paper.arxiv.Client")
def test_init_without_validation(mock_client_class):
    paper = Paper(validate_arguments=False)  # noqa: F841 # pylint: disable=unused-variable
    mock_client_class.assert_called_once()

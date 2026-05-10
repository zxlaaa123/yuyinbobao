import json

from app.utils.json_parser import extract_json_from_text, try_fix_json


def test_extracts_markdown_json_block():
    text = '说明\n```json\n{"items":[{"title":"A"}]}\n```'
    assert extract_json_from_text(text)["items"][0]["title"] == "A"


def test_extracts_balanced_json_with_extra_text():
    text = '前缀 {"a": "包含 } 的字符串", "b": [1, 2]} 后缀 {"ignored": true}'
    assert extract_json_from_text(text) == {"a": "包含 } 的字符串", "b": [1, 2]}


def test_repairs_trailing_comma_and_comments():
    text = '{\n// comment\n"a": 1,\n"b": [2,],\n}'
    assert extract_json_from_text(text) == {"a": 1, "b": [2]}


def test_try_fix_returns_valid_json():
    fixed = try_fix_json("{'a': 1,}")
    assert fixed is not None
    assert json.loads(fixed) == {"a": 1}

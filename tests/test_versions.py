import check_versions as cv


def test_parse_requirements():
    text = """
    # comment
    requests==2.31.0
    pydantic[email]==2.7.1  ; python_version >= "3.10"
    httpx>=0.27
    """
    assert cv.parse_requirements(text) == {"requests": "2.31.0", "pydantic": "2.7.1"}


def test_parse_pyproject():
    text = """
[project]
name = "x"
dependencies = ["openai==1.3.0", "anyio>=4"]

[project.optional-dependencies]
dev = ["pytest==8.0.0"]
"""
    assert cv.parse_pyproject(text) == {"openai": "1.3.0", "pytest": "8.0.0"}


def test_compare():
    assert cv.compare("1.2.0", "1.2.5") == "ok"
    assert cv.compare("1.2.0", "1.3.0") == "minor"
    assert cv.compare("1.2.0", "2.0.0") == "major"
    assert cv.compare("0.1.0", "0.2.0") == "major"  # 0.x minor bumps are breaking
    assert cv.compare("2.0.0", "1.9.0") == "ok"


def test_no_pins_is_ok(tmp_path):
    assert cv.main([str(tmp_path)]) == 0

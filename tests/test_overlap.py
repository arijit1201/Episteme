import check_overlap as co

SOURCE = (
    "Agents are systems where the model dynamically directs its own process and tool usage, "
    "keeping control over how it accomplishes tasks. Workflows are systems where models and tools "
    "are orchestrated through predefined code paths that the developer writes in advance."
)


def test_copied_text_fails():
    page = "---\ntitle: T\n---\n" + SOURCE
    report = co.analyze(page, SOURCE)
    assert report.failures(15, 0.10)


def test_paraphrase_passes():
    page = (
        "---\ntitle: T\n---\n"
        "A workflow follows steps a developer fixed ahead of time. An agent picks its own next step "
        "and decides which tool to call [src:a-source]."
    )
    report = co.analyze(page, SOURCE)
    assert report.failures(15, 0.10) == []


def test_short_quote_is_excluded_from_run():
    page = 'The guide calls this "predefined code paths" and contrasts it with agents.'
    report = co.analyze(page, SOURCE)
    assert report.long_quotes == []
    assert report.longest_run < 3


def test_long_quote_fails():
    page = (
        '"Agents are systems where the model dynamically directs its own process and tool usage, '
        'keeping control over how it accomplishes tasks."'
    )
    report = co.analyze(page, SOURCE)
    assert report.long_quotes


def test_longest_shared_run():
    assert co.longest_shared_run("a b c d e".split(), "x b c d y".split()) == 3
    assert co.longest_shared_run("a b".split(), "c d".split()) == 0

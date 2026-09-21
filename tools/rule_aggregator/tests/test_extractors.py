from extractors.clearurls_extractor import extract_clearurls_data
from extractors.adguard_extractor import extract_adguard_data

def test_extract_clearurls_data(mocker):
    mock_data = {
        "providers": {
            "Amazon": {
                "urlPattern": "^https?:\\/\\/(?:[a-z0-9-]+\\.)*amazon\\.(?:[a-z]{2,3})(?:\\.[a-z]{2})?\\/",
                "rules": ["(site-redirect)", "(_encoding)"],
                "rawRules": ["(?:&|\\?)site-redirect=[^&]+", "(?:&|\\?)_encoding=[^&]+"]
            }
        }
    }
    mocker.patch('requests.get').return_value.json.return_value = mock_data

    result = extract_clearurls_data()

    assert "site-redirect" in result['sacred_params']
    assert "_encoding" in result['sacred_params']
    # Ensure no regex syntax leaked
    for param in result['sacred_params']:
        assert "(?:" not in param
        assert "\\?" not in param
        assert "[^&]" not in param


def test_extract_clearurls_empty_providers(mocker):
    mocker.patch('requests.get').return_value.json.return_value = {"providers": {}}
    result = extract_clearurls_data()
    assert result['sacred_params'] == []
    assert result['shortener_domains'] == []


def test_extract_clearurls_missing_rules_key(mocker):
    mock_data = {
        "providers": {
            "NoRules": {
                "urlPattern": "^https?://example.com/",
            }
        }
    }
    mocker.patch('requests.get').return_value.json.return_value = mock_data
    result = extract_clearurls_data()
    assert result['sacred_params'] == []


def test_extract_clearurls_dedup_across_providers(mocker):
    mock_data = {
        "providers": {
            "ProviderA": {"rules": ["(utm_source)"]},
            "ProviderB": {"rules": ["(utm_source)"]},
        }
    }
    mocker.patch('requests.get').return_value.json.return_value = mock_data
    result = extract_clearurls_data()
    assert result['sacred_params'].count("utm_source") == 1


def test_extract_clearurls_strips_single_char(mocker):
    mock_data = {
        "providers": {
            "Provider": {"rules": ["(x)"]},
        }
    }
    mocker.patch('requests.get').return_value.json.return_value = mock_data
    result = extract_clearurls_data()
    assert "x" not in result['sacred_params']


# AdGuard extractor tests

def test_extract_adguard_data(mocker):
    mock_text = "$removeparam=utm_source\n||tracker.com^$third-party\n$removeparam=fbclid"
    mocker.patch('requests.get').return_value.text = mock_text

    result = extract_adguard_data()

    assert "utm_source" in result['sacred_params']
    assert "fbclid" in result['sacred_params']
    assert "tracker.com" not in result['sacred_params']


def test_extract_adguard_comments_ignored(mocker):
    mock_text = "! This is a comment with $removeparam=should_be_ignored\n$removeparam=real_param"
    mocker.patch('requests.get').return_value.text = mock_text

    result = extract_adguard_data()

    assert "should_be_ignored" not in result['sacred_params']
    assert "real_param" in result['sacred_params']


def test_extract_adguard_empty_input(mocker):
    mocker.patch('requests.get').return_value.text = ""

    result = extract_adguard_data()

    assert result['sacred_params'] == []
    assert result['shortener_domains'] == []


def test_extract_adguard_complex_removeparam(mocker):
    mock_text = "$removeparam=/regex_pattern/\n$removeparam=simple_param"
    mocker.patch('requests.get').return_value.text = mock_text

    result = extract_adguard_data()

    assert "simple_param" in result['sacred_params']
    # Regex-style removeparam values (containing /) must be ignored
    for param in result['sacred_params']:
        assert "/" not in param

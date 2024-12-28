import mock
import pytest
from gitanalyzer.domain.developer import Developer
from gitanalyzer.utils.mailmap import DefaultDeveloperFactory, MailmapDeveloperFactory
from subprocess import CompletedProcess


def test_standard_dev_factory():
    dev_name, dev_email = "Alice", "alice@example.com"
    dev1 = Developer(dev_name, dev_email)
    factory = DefaultDeveloperFactory()

    dev2 = factory.create_developer(dev_name, dev_email)

    assert dev1 == dev2


repo_config = {"path_to_repo": "https://github.com/codingwithshawnyt/GitAnalyzer"}
test_data = [
    (repo_config, "Alice Example", "alice@users.noreply.github.com", Developer("Alice Example", "alice@example.com")),
    (repo_config, "Bob Builder", "bob.builder@gmail.com", Developer("Bob Builder", "bob.builder@gmail.com")),
    (repo_config, "Charlie Chaplin", "charlie@silentmovies.com", Developer("Charlie Chaplin", "charlie@silentmovies.com")),
    (repo_config, "Alice", "alice@example.com", Developer("Alice", "alice@example.com")),
]


@pytest.mark.parametrize("config,name,email,expected", test_data)
def test_mailmap_dev_factory_without_cache(config, name, email, expected):
    factory = MailmapDeveloperFactory(config)

    dev = factory.create_developer(name, email)

    assert dev == expected


factory_instance = MailmapDeveloperFactory(repo_config)
test_data2 = [
    (factory_instance, "Alice Example", "alice@users.noreply.github.com", Developer("Alice Example", "alice@example.com")),
    (factory_instance, "Bob Builder", "bob.builder@gmail.com", Developer("Bob Builder", "bob.builder@gmail.com")),
    (factory_instance, "Alice Example", "alice@users.noreply.github.com", Developer("Alice Example", "alice@example.com")),
    (factory_instance, "Bob Builder", "bob.builder@gmail.com", Developer("Bob Builder", "bob.builder@gmail.com")),
    (factory_instance, "Charlie Chaplin", "charlie@silentmovies.com", Developer("Charlie Chaplin", "charlie@silentmovies.com")),
    (factory_instance, "Alice", "alice@example.com", Developer("Alice", "alice@example.com")),
    (factory_instance, "", "charlie@silentmovies.com", Developer("", "charlie@silentmovies.com")),
]


@pytest.mark.parametrize("factory,name,email,expected", test_data2)
def test_mailmap_dev_factory_with_cache(factory, name, email, expected):
    dev = factory.create_developer(name, email)

    assert dev == expected


factory_instance = MailmapDeveloperFactory(repo_config)
test_data3 = [
    (factory_instance, "Alice Example", "alice@users.noreply.github.com", Developer("Alice Example", "alice@users.noreply.github.com")),
    (factory_instance, "Bob Builder", "bob.builder@gmail.com", Developer("Bob Builder", "bob.builder@gmail.com")),
    (factory_instance, "Charlie Chaplin", "charlie@silentmovies.com", Developer("Charlie Chaplin", "charlie@silentmovies.com")),
    (factory_instance, "Alice", "alice@example.com", Developer("Alice", "alice@example.com")),
]


@pytest.mark.parametrize("factory,name,email,expected", test_data3)
def test_mailmap_dev_factory_with_cache_exception(factory, name, email, expected):
    with mock.patch.object(factory, "_run_check_mailmap", side_effect=Exception("ERROR")):
        dev = factory.create_developer(name, email)

        assert dev == expected


@pytest.mark.parametrize("factory,name,email,expected", test_data3)
def test_mailmap_dev_factory_with_cache_stderr(factory, name, email, expected):
    mock_result = CompletedProcess("", 123)
    mock_result.stderr = "fatal: ..."

    with mock.patch("subprocess.run", return_value=mock_result):
        dev = factory.create_developer(name, email)

        assert dev == expected

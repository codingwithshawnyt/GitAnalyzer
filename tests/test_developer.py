from gitanalyzer.domain.developer import Developer


def test_developer_equality():
    # Create test developers with same and different emails
    developer1 = Developer("John", "john.dev@email.com")
    developer2 = Developer("John", "john.dev@email.com")
    developer3 = Developer("John", "john.dev@other.com")
    developer4 = None

    # Verify equality comparisons
    assert developer1 == developer1, "Developer should equal itself"
    assert developer1 == developer2, "Developers with same name and email should be equal"
    assert not (developer1 == developer3), "Developers with different emails should not be equal"
    assert not (developer1 == developer4), "Developer should not equal None"


def test_developer_string_representation():
    # Arrange
    test_dev = Developer("Alice", "alice.dev@email.com")
    
    # Act
    string_representation = test_dev.__repr__()
    
    # Assert
    expected = 'Developer("Alice", "alice.dev@email.com")'
    assert string_representation == expected, "Developer string representation should match expected format"
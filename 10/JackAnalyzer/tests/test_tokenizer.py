import pytest

@pytest.fixture
def mock_text_file(tmp_path):
    def _create_file():
        file_path = tmp_path / "mock_file.txt"
        file_path.write_text(
        """
        hola
        adios
        """)
        return file_path
    return _create_file 

class TestHasMoreTokens:
    def test_has_more_tokens(self, mock_text_file):
        """ Creating mock phrases to check correct has token check """
        # Arrange
        file_path = mock_text_file()
        # Act
        print(file_path)
        assert False
        # Assert 
    def test_doesnt_have_more_tokens(self):
        pass

"""Tests for CQL CLI."""

from pathlib import Path

from typer.testing import CliRunner

from fhirkit.cql_cli import app

runner = CliRunner()


class TestCQLParse:
    """Tests for cql parse command."""

    def test_parse_valid_cql_file(self, tmp_path: Path) -> None:
        """Test parsing a valid CQL file."""
        cql_file = tmp_path / "test.cql"
        cql_file.write_text("library Test version '1.0'\n")

        result = runner.invoke(app, ["parse", str(cql_file)])
        assert result.exit_code == 0
        assert "Successfully parsed" in result.stdout

    def test_parse_valid_cql_file_quiet(self, tmp_path: Path) -> None:
        """Test parsing a valid CQL file in quiet mode."""
        cql_file = tmp_path / "test.cql"
        cql_file.write_text("library Test version '1.0'\n")

        result = runner.invoke(app, ["parse", str(cql_file), "--quiet"])
        assert result.exit_code == 0
        assert result.stdout.strip() == ""

    def test_parse_invalid_cql_file(self, tmp_path: Path) -> None:
        """Test parsing an invalid CQL file."""
        cql_file = tmp_path / "invalid.cql"
        cql_file.write_text("this is not valid cql @@@@")

        result = runner.invoke(app, ["parse", str(cql_file)])
        assert result.exit_code == 1
        assert "Parse errors" in result.stdout

    def test_parse_nonexistent_file(self) -> None:
        """Test parsing a nonexistent file."""
        result = runner.invoke(app, ["parse", "/nonexistent/file.cql"])
        assert result.exit_code == 1
        assert "File not found" in result.stdout

    def test_parse_example_file(self) -> None:
        """Test parsing an example CQL file."""
        example_file = Path("examples/cql/01_hello_world.cql")
        if example_file.exists():
            result = runner.invoke(app, ["parse", str(example_file)])
            assert result.exit_code == 0


class TestCQLAst:
    """Tests for cql ast command."""

    def test_ast_valid_cql(self, tmp_path: Path) -> None:
        """Test AST display for valid CQL."""
        cql_file = tmp_path / "test.cql"
        cql_file.write_text("library Test version '1.0'\n")

        result = runner.invoke(app, ["ast", str(cql_file)])
        assert result.exit_code == 0
        assert "library" in result.stdout

    def test_ast_invalid_cql(self, tmp_path: Path) -> None:
        """Test AST display for invalid CQL."""
        cql_file = tmp_path / "invalid.cql"
        cql_file.write_text("@@@@invalid@@@@")

        result = runner.invoke(app, ["ast", str(cql_file)])
        assert result.exit_code == 1
        assert "Parse errors" in result.stdout

    def test_ast_nonexistent_file(self) -> None:
        """Test AST for nonexistent file."""
        result = runner.invoke(app, ["ast", "/nonexistent/file.cql"])
        assert result.exit_code == 1
        assert "File not found" in result.stdout

    def test_ast_with_depth_option(self, tmp_path: Path) -> None:
        """Test AST with depth limit."""
        cql_file = tmp_path / "test.cql"
        cql_file.write_text("library Test version '1.0'\ndefine X: 1 + 2 * 3\n")

        result = runner.invoke(app, ["ast", str(cql_file), "--depth", "5"])
        assert result.exit_code == 0


class TestCQLTokens:
    """Tests for cql tokens command."""

    def test_tokens_valid_cql(self, tmp_path: Path) -> None:
        """Test token display for valid CQL."""
        cql_file = tmp_path / "test.cql"
        cql_file.write_text("library Test")

        result = runner.invoke(app, ["tokens", str(cql_file)])
        assert result.exit_code == 0
        assert "Tokens for" in result.stdout
        assert "Total:" in result.stdout

    def test_tokens_with_limit(self, tmp_path: Path) -> None:
        """Test token display with limit."""
        cql_file = tmp_path / "test.cql"
        cql_file.write_text("library Test version '1.0'\ndefine X: 1 + 2 + 3 + 4 + 5\n")

        result = runner.invoke(app, ["tokens", str(cql_file), "--limit", "5"])
        assert result.exit_code == 0
        assert "limited to 5 tokens" in result.stdout

    def test_tokens_nonexistent_file(self) -> None:
        """Test tokens for nonexistent file."""
        result = runner.invoke(app, ["tokens", "/nonexistent/file.cql"])
        assert result.exit_code == 1
        assert "File not found" in result.stdout


class TestCQLShow:
    """Tests for cql show command."""

    def test_show_valid_file(self, tmp_path: Path) -> None:
        """Test show command for valid file."""
        cql_file = tmp_path / "test.cql"
        cql_file.write_text("library Test version '1.0'\n")

        result = runner.invoke(app, ["show", str(cql_file)])
        assert result.exit_code == 0

    def test_show_nonexistent_file(self) -> None:
        """Test show for nonexistent file."""
        result = runner.invoke(app, ["show", "/nonexistent/file.cql"])
        assert result.exit_code == 1
        assert "File not found" in result.stdout


class TestCQLValidate:
    """Tests for cql validate command."""

    def test_validate_single_valid_file(self, tmp_path: Path) -> None:
        """Test validating a single valid file."""
        cql_file = tmp_path / "test.cql"
        cql_file.write_text("library Test version '1.0'\n")

        result = runner.invoke(app, ["validate", str(cql_file)])
        assert result.exit_code == 0
        assert "1/1 passed" in result.stdout

    def test_validate_multiple_files(self, tmp_path: Path) -> None:
        """Test validating multiple files."""
        file1 = tmp_path / "test1.cql"
        file1.write_text("library Test1 version '1.0'\n")
        file2 = tmp_path / "test2.cql"
        file2.write_text("library Test2 version '1.0'\n")

        result = runner.invoke(app, ["validate", str(file1), str(file2)])
        assert result.exit_code == 0
        assert "2/2 passed" in result.stdout

    def test_validate_with_invalid_file(self, tmp_path: Path) -> None:
        """Test validating mix of valid and invalid files."""
        valid = tmp_path / "valid.cql"
        valid.write_text("library Valid version '1.0'\n")
        invalid = tmp_path / "invalid.cql"
        invalid.write_text("@@@@not valid@@@@")

        result = runner.invoke(app, ["validate", str(valid), str(invalid)])
        assert result.exit_code == 1
        assert "1/2 passed" in result.stdout
        assert "1/2 failed" in result.stdout

    def test_validate_nonexistent_file(self, tmp_path: Path) -> None:
        """Test validating nonexistent file."""
        result = runner.invoke(app, ["validate", "/nonexistent/file.cql"])
        assert result.exit_code == 1
        assert "File not found" in result.stdout


class TestCQLDefinitions:
    """Tests for cql definitions command."""

    def test_definitions_valid_file(self, tmp_path: Path) -> None:
        """Test definitions extraction."""
        cql_file = tmp_path / "test.cql"
        cql_file.write_text("""library Test version '1.0'
using FHIR version '4.0.1'
define "Adult": Patient.birthDate + 18 years <= Today()
""")

        result = runner.invoke(app, ["definitions", str(cql_file)])
        assert result.exit_code == 0
        assert "Definitions in" in result.stdout

    def test_definitions_nonexistent_file(self) -> None:
        """Test definitions for nonexistent file."""
        result = runner.invoke(app, ["definitions", "/nonexistent/file.cql"])
        assert result.exit_code == 1
        assert "File not found" in result.stdout

    def test_definitions_invalid_file(self, tmp_path: Path) -> None:
        """Test definitions for invalid CQL."""
        cql_file = tmp_path / "invalid.cql"
        cql_file.write_text("@@@@invalid@@@@")

        result = runner.invoke(app, ["definitions", str(cql_file)])
        assert result.exit_code == 1
        assert "Parse errors" in result.stdout


class TestCQLNoArgs:
    """Test CLI behavior with no arguments."""

    def test_no_args_shows_help(self) -> None:
        """Test that no arguments shows help."""
        result = runner.invoke(app, [])
        # Typer uses exit code 0 or 2 for help display
        assert result.exit_code in (0, 2)
        assert "CQL" in result.stdout or "Usage" in result.stdout

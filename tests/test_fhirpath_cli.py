"""Tests for FHIRPath CLI."""

import json
from pathlib import Path

from typer.testing import CliRunner

from fhirkit.fhirpath_cli import app

runner = CliRunner()


class TestFHIRPathParse:
    """Tests for fhirpath parse command."""

    def test_parse_valid_expression(self) -> None:
        """Test parsing a valid FHIRPath expression."""
        result = runner.invoke(app, ["parse", "Patient.name.given"])
        assert result.exit_code == 0
        assert "Valid FHIRPath expression" in result.stdout

    def test_parse_valid_expression_quiet(self) -> None:
        """Test parsing a valid expression in quiet mode."""
        result = runner.invoke(app, ["parse", "Patient.name", "--quiet"])
        assert result.exit_code == 0
        assert result.stdout.strip() == ""

    def test_parse_complex_expression(self) -> None:
        """Test parsing complex expressions."""
        expressions = [
            "Patient.name.where(use = 'official').given.first()",
            "Observation.component.where(code.coding.code = '8480-6').value",
            "1 + 2 * 3",
            "name.exists() and active = true",
            "@2024-01-15",
            "10 'kg'",
        ]
        for expr in expressions:
            result = runner.invoke(app, ["parse", expr])
            assert result.exit_code == 0, f"Failed to parse: {expr}"

    def test_parse_invalid_expression(self) -> None:
        """Test parsing an invalid expression."""
        # Use truly invalid FHIRPath syntax
        result = runner.invoke(app, ["parse", "Patient..name"])
        assert result.exit_code == 1
        assert "Parse errors" in result.stdout or "Error" in result.stdout


class TestFHIRPathAst:
    """Tests for fhirpath ast command."""

    def test_ast_valid_expression(self) -> None:
        """Test AST display for valid expression."""
        result = runner.invoke(app, ["ast", "Patient.name.given"])
        assert result.exit_code == 0
        assert "expression" in result.stdout

    def test_ast_with_depth(self) -> None:
        """Test AST with depth limit."""
        result = runner.invoke(app, ["ast", "1 + 2 * 3 - 4", "--depth", "3"])
        assert result.exit_code == 0

    def test_ast_invalid_expression(self) -> None:
        """Test AST for invalid expression."""
        result = runner.invoke(app, ["ast", "@@@@"])
        assert result.exit_code == 1
        assert "Parse errors" in result.stdout


class TestFHIRPathTokens:
    """Tests for fhirpath tokens command."""

    def test_tokens_simple(self) -> None:
        """Test tokens for simple expression."""
        result = runner.invoke(app, ["tokens", "Patient.name"])
        assert result.exit_code == 0
        assert "Tokens:" in result.stdout
        assert "Total:" in result.stdout

    def test_tokens_complex(self) -> None:
        """Test tokens for complex expression."""
        result = runner.invoke(app, ["tokens", "name.where(use = 'official').first()"])
        assert result.exit_code == 0
        assert "Total:" in result.stdout


class TestFHIRPathParseFile:
    """Tests for fhirpath parse-file command."""

    def test_parse_file_valid(self, tmp_path: Path) -> None:
        """Test parsing file with valid expressions."""
        expr_file = tmp_path / "expressions.fhirpath"
        expr_file.write_text("Patient.name\nPatient.birthDate\n1 + 2\n")

        result = runner.invoke(app, ["parse-file", str(expr_file)])
        assert result.exit_code == 0
        assert "3/3 passed" in result.stdout

    def test_parse_file_with_comments(self, tmp_path: Path) -> None:
        """Test parsing file with comments."""
        expr_file = tmp_path / "expressions.fhirpath"
        expr_file.write_text("// This is a comment\n# Also a comment\nPatient.name\n\n")

        result = runner.invoke(app, ["parse-file", str(expr_file)])
        assert result.exit_code == 0
        assert "1/1 passed" in result.stdout

    def test_parse_file_with_errors(self, tmp_path: Path) -> None:
        """Test parsing file with invalid expressions."""
        expr_file = tmp_path / "expressions.fhirpath"
        expr_file.write_text("Patient.name\nPatient..invalid\n")

        result = runner.invoke(app, ["parse-file", str(expr_file)])
        assert result.exit_code == 1
        assert "1/2 failed" in result.stdout

    def test_parse_file_quiet(self, tmp_path: Path) -> None:
        """Test parsing file in quiet mode."""
        expr_file = tmp_path / "expressions.fhirpath"
        expr_file.write_text("Patient.name\nPatient.active\n")

        result = runner.invoke(app, ["parse-file", str(expr_file), "--quiet"])
        assert result.exit_code == 0
        assert "2/2 passed" in result.stdout

    def test_parse_file_nonexistent(self) -> None:
        """Test parsing nonexistent file."""
        result = runner.invoke(app, ["parse-file", "/nonexistent/file.fhirpath"])
        assert result.exit_code == 1
        assert "File not found" in result.stdout


class TestFHIRPathShow:
    """Tests for fhirpath show command."""

    def test_show_valid_file(self, tmp_path: Path) -> None:
        """Test show command."""
        expr_file = tmp_path / "test.fhirpath"
        expr_file.write_text("Patient.name.given\nPatient.birthDate\n")

        result = runner.invoke(app, ["show", str(expr_file)])
        assert result.exit_code == 0

    def test_show_nonexistent_file(self) -> None:
        """Test show for nonexistent file."""
        result = runner.invoke(app, ["show", "/nonexistent/file.fhirpath"])
        assert result.exit_code == 1
        assert "File not found" in result.stdout


class TestFHIRPathEval:
    """Tests for fhirpath eval command."""

    def test_eval_simple_expression(self) -> None:
        """Test evaluating simple expression."""
        result = runner.invoke(app, ["eval", "1 + 2"])
        assert result.exit_code == 0
        assert "3" in result.stdout

    def test_eval_with_json_input(self) -> None:
        """Test evaluating with inline JSON."""
        patient = json.dumps({"resourceType": "Patient", "id": "123", "active": True})
        result = runner.invoke(app, ["eval", "Patient.id", "--json", patient])
        assert result.exit_code == 0
        assert "123" in result.stdout

    def test_eval_with_resource_file(self, tmp_path: Path) -> None:
        """Test evaluating with resource file."""
        resource_file = tmp_path / "patient.json"
        resource_file.write_text(
            json.dumps(
                {"resourceType": "Patient", "id": "test-patient", "name": [{"given": ["John"], "family": "Doe"}]}
            )
        )

        result = runner.invoke(app, ["eval", "Patient.name.given", "-r", str(resource_file)])
        assert result.exit_code == 0
        assert "John" in result.stdout

    def test_eval_empty_result(self) -> None:
        """Test evaluating with empty result."""
        patient = json.dumps({"resourceType": "Patient", "id": "123"})
        result = runner.invoke(app, ["eval", "Patient.name", "--json", patient])
        assert result.exit_code == 0
        assert "Empty result" in result.stdout

    def test_eval_multiple_results(self) -> None:
        """Test evaluating with multiple results."""
        patient = json.dumps({"resourceType": "Patient", "name": [{"given": ["John", "James"]}]})
        result = runner.invoke(app, ["eval", "Patient.name.given", "--json", patient])
        assert result.exit_code == 0
        assert "Results:" in result.stdout

    def test_eval_json_output(self) -> None:
        """Test evaluating with JSON output."""
        result = runner.invoke(app, ["eval", "1 + 2", "--json-output"])
        assert result.exit_code == 0
        # Should be valid JSON
        output = json.loads(result.stdout)
        # Result may be Decimal serialized as string
        assert len(output) == 1
        assert int(float(str(output[0]))) == 3

    def test_eval_invalid_expression(self) -> None:
        """Test evaluating invalid expression."""
        result = runner.invoke(app, ["eval", "Patient..name"])
        assert result.exit_code == 1
        assert "Error" in result.stdout

    def test_eval_invalid_json(self) -> None:
        """Test evaluating with invalid JSON input."""
        result = runner.invoke(app, ["eval", "Patient.id", "--json", "not valid json"])
        assert result.exit_code == 1
        assert "Invalid JSON" in result.stdout

    def test_eval_nonexistent_resource_file(self) -> None:
        """Test evaluating with nonexistent resource file."""
        result = runner.invoke(app, ["eval", "Patient.id", "-r", "/nonexistent/file.json"])
        assert result.exit_code == 1
        assert "not found" in result.stdout

    def test_eval_invalid_resource_file(self, tmp_path: Path) -> None:
        """Test evaluating with invalid JSON resource file."""
        resource_file = tmp_path / "invalid.json"
        resource_file.write_text("not valid json")

        result = runner.invoke(app, ["eval", "Patient.id", "-r", str(resource_file)])
        assert result.exit_code == 1
        assert "Invalid JSON" in result.stdout


class TestFHIRPathEvalFile:
    """Tests for fhirpath eval-file command."""

    def test_eval_file_valid(self, tmp_path: Path) -> None:
        """Test evaluating file with expressions."""
        expr_file = tmp_path / "expressions.fhirpath"
        expr_file.write_text("1 + 1\n2 * 3\n")

        result = runner.invoke(app, ["eval-file", str(expr_file)])
        assert result.exit_code == 0
        assert "2/2 passed" in result.stdout

    def test_eval_file_with_resource(self, tmp_path: Path) -> None:
        """Test evaluating file with resource."""
        expr_file = tmp_path / "expressions.fhirpath"
        expr_file.write_text("Patient.id\nPatient.active\n")

        resource_file = tmp_path / "patient.json"
        resource_file.write_text(json.dumps({"resourceType": "Patient", "id": "123", "active": True}))

        result = runner.invoke(app, ["eval-file", str(expr_file), "-r", str(resource_file)])
        assert result.exit_code == 0
        assert "2/2 passed" in result.stdout

    def test_eval_file_with_comments(self, tmp_path: Path) -> None:
        """Test evaluating file with comments."""
        expr_file = tmp_path / "expressions.fhirpath"
        expr_file.write_text("// Comment\n# Also comment\n1 + 1\n\n")

        result = runner.invoke(app, ["eval-file", str(expr_file)])
        assert result.exit_code == 0
        assert "1/1 passed" in result.stdout

    def test_eval_file_quiet(self, tmp_path: Path) -> None:
        """Test evaluating file in quiet mode."""
        expr_file = tmp_path / "expressions.fhirpath"
        expr_file.write_text("1 + 1\n2 + 2\n")

        result = runner.invoke(app, ["eval-file", str(expr_file), "--quiet"])
        assert result.exit_code == 0
        assert "2/2 passed" in result.stdout

    def test_eval_file_with_errors(self, tmp_path: Path) -> None:
        """Test evaluating file with errors."""
        expr_file = tmp_path / "expressions.fhirpath"
        expr_file.write_text("1 + 1\nPatient..invalid\n")

        result = runner.invoke(app, ["eval-file", str(expr_file)])
        assert result.exit_code == 1
        assert "1/2 failed" in result.stdout

    def test_eval_file_nonexistent(self) -> None:
        """Test evaluating nonexistent file."""
        result = runner.invoke(app, ["eval-file", "/nonexistent/file.fhirpath"])
        assert result.exit_code == 1
        assert "File not found" in result.stdout

    def test_eval_file_nonexistent_resource(self, tmp_path: Path) -> None:
        """Test evaluating with nonexistent resource file."""
        expr_file = tmp_path / "expressions.fhirpath"
        expr_file.write_text("Patient.id\n")

        result = runner.invoke(app, ["eval-file", str(expr_file), "-r", "/nonexistent.json"])
        assert result.exit_code == 1
        assert "not found" in result.stdout


class TestFHIRPathRepl:
    """Tests for fhirpath repl command."""

    def test_repl_quit(self) -> None:
        """Test REPL quit command."""
        result = runner.invoke(app, ["repl"], input="quit\n")
        assert result.exit_code == 0
        assert "Goodbye" in result.stdout

    def test_repl_exit(self) -> None:
        """Test REPL exit command."""
        result = runner.invoke(app, ["repl"], input="exit\n")
        assert result.exit_code == 0
        assert "Goodbye" in result.stdout

    def test_repl_q(self) -> None:
        """Test REPL q shortcut."""
        result = runner.invoke(app, ["repl"], input="q\n")
        assert result.exit_code == 0
        assert "Goodbye" in result.stdout

    def test_repl_parse_valid(self) -> None:
        """Test REPL parsing valid expression."""
        result = runner.invoke(app, ["repl"], input="Patient.name\nquit\n")
        assert result.exit_code == 0
        assert "Valid" in result.stdout

    def test_repl_parse_invalid(self) -> None:
        """Test REPL parsing invalid expression."""
        result = runner.invoke(app, ["repl"], input="@@@@\nquit\n")
        assert result.exit_code == 0

    def test_repl_help(self) -> None:
        """Test REPL help command."""
        result = runner.invoke(app, ["repl"], input="help\nquit\n")
        assert result.exit_code == 0
        assert "Commands" in result.stdout

    def test_repl_empty_input(self) -> None:
        """Test REPL with empty input."""
        result = runner.invoke(app, ["repl"], input="\nquit\n")
        assert result.exit_code == 0

    def test_repl_ast_command(self) -> None:
        """Test REPL ast subcommand."""
        result = runner.invoke(app, ["repl"], input="ast Patient.name\nquit\n")
        assert result.exit_code == 0
        assert "expression" in result.stdout

    def test_repl_ast_invalid(self) -> None:
        """Test REPL ast with invalid expression."""
        result = runner.invoke(app, ["repl"], input="ast @@@@\nquit\n")
        assert result.exit_code == 0

    def test_repl_tokens_command(self) -> None:
        """Test REPL tokens subcommand."""
        result = runner.invoke(app, ["repl"], input="tokens Patient.name\nquit\n")
        assert result.exit_code == 0

    def test_repl_eof(self) -> None:
        """Test REPL with EOF."""
        result = runner.invoke(app, ["repl"], input="")
        assert result.exit_code == 0
        assert "Goodbye" in result.stdout


class TestFHIRPathNoArgs:
    """Test CLI behavior with no arguments."""

    def test_no_args_shows_help(self) -> None:
        """Test that no arguments shows help."""
        result = runner.invoke(app, [])
        # Typer uses exit code 0 or 2 for help display
        assert result.exit_code in (0, 2)
        assert "FHIRPath" in result.stdout or "Usage" in result.stdout

"""Pruebas unitarias del analizador léxico de Mini C.

Verifica la especificación definida en analizador-lexico-mini-c (SKILL.md) y
CLAUDE.md: categorías, posiciones, máxima coincidencia, casos de la sección 7,
diagnósticos LEX001 y formato de salida.
"""

from minic.diagnostics.diagnostic import Diagnostic
from minic.lexer.lexer import Lexer
from minic.lexer.token import Token
from minic.lexer.token_type import TokenType
from minic.output.diagnostic_printer import format_diagnostic
from minic.output.token_printer import format_token


def test_section_7_valid_case() -> None:
    source = "int2 = 12abc;\nwhilex == -5"
    tokens, diagnostics = Lexer(source).scan()

    assert diagnostics == []

    expected = [
        ("IDENTIFIER", "int2", None, 1, 1),
        ("ASSIGN", "=", None, 1, 6),
        ("INTEGER_LITERAL", "12", 12, 1, 8),
        ("IDENTIFIER", "abc", None, 1, 10),
        ("SEMICOLON", ";", None, 1, 13),
        ("IDENTIFIER", "whilex", None, 2, 1),
        ("EQUAL_EQUAL", "==", None, 2, 8),
        ("MINUS", "-", None, 2, 11),
        ("INTEGER_LITERAL", "5", 5, 2, 12),
        ("EOF", "", None, 2, 13),
    ]

    assert len(tokens) == len(expected)
    for token, (exp_type, exp_lex, exp_lit, exp_line, exp_col) in zip(tokens, expected):
        assert token.type == exp_type
        assert token.lexeme == exp_lex
        assert token.literal == exp_lit
        assert token.line == exp_line
        assert token.column == exp_col

    formatted_lines = [format_token(t) for t in tokens]
    expected_output = [
        "IDENTIFIER 'int2' 1 1",
        "ASSIGN '=' 1 6",
        "INTEGER_LITERAL '12' 1 8",
        "IDENTIFIER 'abc' 1 10",
        "SEMICOLON ';' 1 13",
        "IDENTIFIER 'whilex' 2 1",
        "EQUAL_EQUAL '==' 2 8",
        "MINUS '-' 2 11",
        "INTEGER_LITERAL '5' 2 12",
        "EOF '' 2 13",
    ]
    assert formatted_lines == expected_output


def test_section_7_error_case() -> None:
    source = "int x = @;\nx ! = 0; // fin"
    tokens, diagnostics = Lexer(source).scan()

    expected_tokens = [
        ("KW_INT", "int", None, 1, 1),
        ("IDENTIFIER", "x", None, 1, 5),
        ("ASSIGN", "=", None, 1, 7),
        ("SEMICOLON", ";", None, 1, 10),
        ("IDENTIFIER", "x", None, 2, 1),
        ("ASSIGN", "=", None, 2, 5),
        ("INTEGER_LITERAL", "0", 0, 2, 7),
        ("SEMICOLON", ";", None, 2, 8),
        ("IDENTIFIER", "fin", None, 2, 13),
        ("EOF", "", None, 2, 16),
    ]

    assert len(tokens) == len(expected_tokens)
    for token, (exp_type, exp_lex, exp_lit, exp_line, exp_col) in zip(tokens, expected_tokens):
        assert token.type == exp_type
        assert token.lexeme == exp_lex
        assert token.literal == exp_lit
        assert token.line == exp_line
        assert token.column == exp_col

    expected_diagnostics = [
        ("LEX001", "error", "Carácter no reconocido: '@'", 1, 9),
        ("LEX001", "error", "Carácter no reconocido: '!'", 2, 3),
        ("LEX001", "error", "Carácter no reconocido: '/'", 2, 10),
        ("LEX001", "error", "Carácter no reconocido: '/'", 2, 11),
    ]

    assert len(diagnostics) == len(expected_diagnostics)
    for diag, (exp_code, exp_sev, exp_msg, exp_line, exp_col) in zip(diagnostics, expected_diagnostics):
        assert diag.code == exp_code
        assert diag.severity == exp_sev
        assert diag.message == exp_msg
        assert diag.line == exp_line
        assert diag.column == exp_col

    formatted_diagnostics = [format_diagnostic(d) for d in diagnostics]
    expected_diag_lines = [
        "LEX001 error 1:9 Carácter no reconocido: '@'",
        "LEX001 error 2:3 Carácter no reconocido: '!'",
        "LEX001 error 2:10 Carácter no reconocido: '/'",
        "LEX001 error 2:11 Carácter no reconocido: '/'",
    ]
    assert formatted_diagnostics == expected_diag_lines


def test_keywords_and_identifiers() -> None:
    source = "int while int_var while1 _while INT While"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    types = [t.type for t in tokens]
    lexemes = [t.lexeme for t in tokens]

    assert types == [
        TokenType.KW_INT,
        TokenType.KW_WHILE,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]
    assert lexemes == ["int", "while", "int_var", "while1", "_while", "INT", "While", ""]


def test_integer_literals() -> None:
    source = "0 007 42 12345678901234567890"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    assert tokens[0].literal == 0
    assert tokens[0].lexeme == "0"
    assert tokens[1].literal == 7
    assert tokens[1].lexeme == "007"
    assert tokens[2].literal == 42
    assert tokens[2].lexeme == "42"
    assert tokens[3].literal == 12345678901234567890
    assert tokens[3].lexeme == "12345678901234567890"


def test_all_symbols_and_operators() -> None:
    source = "= + - == != ( ) { } ;"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    expected_types = [
        TokenType.ASSIGN,
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.EQUAL_EQUAL,
        TokenType.NOT_EQUAL,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected_types


def test_maximal_munch_operators() -> None:
    source = "=== !== =="
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    expected = [
        (TokenType.EQUAL_EQUAL, "=="),
        (TokenType.ASSIGN, "="),
        (TokenType.NOT_EQUAL, "!="),
        (TokenType.ASSIGN, "="),
        (TokenType.EQUAL_EQUAL, "=="),
        (TokenType.EOF, ""),
    ]
    assert [(t.type, t.lexeme) for t in tokens] == expected


def test_positions_tabs_and_carriage_return() -> None:
    # \t cuenta como 1 columna; \r suelto es blanco de 1 columna
    source = "\tx\r\ny"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    # \t es col 1; x es col 2; \r es col 3; \n abre línea 2; y es col 1
    assert tokens[0].lexeme == "x"
    assert (tokens[0].line, tokens[0].column) == (1, 2)
    assert tokens[1].lexeme == "y"
    assert (tokens[1].line, tokens[1].column) == (2, 1)
    assert tokens[2].type == TokenType.EOF
    assert (tokens[2].line, tokens[2].column) == (2, 2)


def test_empty_source() -> None:
    source = ""
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF
    assert tokens[0].lexeme == ""
    assert (tokens[0].line, tokens[0].column) == (1, 1)


def test_whitespace_only() -> None:
    source = "   \n  \t "
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF
    assert (tokens[0].line, tokens[0].column) == (2, 5)

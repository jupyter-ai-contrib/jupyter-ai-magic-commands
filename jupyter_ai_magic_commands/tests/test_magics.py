import os
from unittest.mock import Mock, patch

import pytest
from IPython import InteractiveShell
from IPython.core.display import Markdown
from jupyter_ai_magic_commands.magics import AiMagics
from pytest import fixture
from traitlets.config.loader import Config


@fixture
def ip(tmp_path) -> InteractiveShell:
    ip = InteractiveShell(ipython_dir=str(tmp_path))
    ip.config = Config()
    return ip


def test_aliases_config(ip):
    ip.config.AiMagics.initial_aliases = {
        "my_custom_alias": {
            "target": "my_provider/my_model",
            "api_base": None,
            "api_key_name": None,
        }
    }
    ip.extension_manager.load_extension("jupyter_ai_magic_commands")
    models_list = ip.run_line_magic("ai", "list all").text
    assert "my_custom_alias" in models_list


def test_default_model_cell(ip):
    ip.config.AiMagics.initial_language_model = "my-favourite-llm"
    ip.extension_manager.load_extension("jupyter_ai_magic_commands")
    with patch.object(AiMagics, "run_ai_cell", return_value=None) as mock_run:
        ip.run_cell_magic("ai", "", cell="Write code for me please")
        assert mock_run.called
        cell_args = mock_run.call_args.args[0]
        assert cell_args.model_id == "my-favourite-llm"


def test_non_default_model_cell(ip):
    ip.config.AiMagics.initial_language_model = "my-favourite-llm"
    ip.extension_manager.load_extension("jupyter_ai_magic_commands")
    with patch.object(AiMagics, "run_ai_cell", return_value=None) as mock_run:
        ip.run_cell_magic("ai", "some-different-llm", cell="Write code for me please")
        assert mock_run.called
        cell_args = mock_run.call_args.args[0]
        assert cell_args.model_id == "some-different-llm"


def test_default_model_fix_line(ip):
    ip.config.AiMagics.initial_language_model = "my-favourite-llm"
    ip.extension_manager.load_extension("jupyter_ai_magic_commands")
    with patch.object(AiMagics, "handle_fix", return_value=None) as mock_run:
        ip.run_cell_magic("ai", "fix", cell=None)
        assert mock_run.called
        cell_args = mock_run.call_args.args[0]
        assert cell_args.model_id == "my-favourite-llm"


PROMPT = {"role": "user", "content": "Write code for me please"}
RESPONSE = {"role": "assistant", "content": "Leet code"}
AI1 = {"role": "assistant", "content": "ai1"}
H1 = {"role": "user", "content": "h1"}
AI2 = {"role": "assistant", "content": "ai2"}
H2 = {"role": "user", "content": "h2"}
AI3 = {"role": "assistant", "content": "ai3"}


@pytest.mark.parametrize(
    ["transcript", "max_history", "expected_context"],
    [
        ([], 3, [PROMPT]),
        ([AI1], 0, [PROMPT]),
        ([AI1], 1, [AI1, PROMPT]),
        ([H1, AI1], 0, [PROMPT]),
        ([H1, AI1], 1, [H1, AI1, PROMPT]),
        ([AI1, H1, AI2], 0, [PROMPT]),
        ([AI1, H1, AI2], 1, [H1, AI2, PROMPT]),
        ([AI1, H1, AI2], 2, [AI1, H1, AI2, PROMPT]),
        ([H1, AI1, H2, AI2], 0, [PROMPT]),
        ([H1, AI1, H2, AI2], 1, [H2, AI2, PROMPT]),
        ([H1, AI1, H2, AI2], 2, [H1, AI1, H2, AI2, PROMPT]),
        ([AI1, H1, AI2, H2, AI3], 0, [PROMPT]),
        ([AI1, H1, AI2, H2, AI3], 1, [H2, AI3, PROMPT]),
        ([AI1, H1, AI2, H2, AI3], 2, [H1, AI2, H2, AI3, PROMPT]),
        ([AI1, H1, AI2, H2, AI3], 3, [AI1, H1, AI2, H2, AI3, PROMPT]),
    ],
)
def test_max_history(ip, transcript, max_history, expected_context):
    ip.extension_manager.load_extension("jupyter_ai_magic_commands")
    ai_magics = ip.magics_manager.registry["AiMagics"]
    ai_magics.transcript = transcript.copy()
    ai_magics.max_history = max_history
    with (
        patch("jupyter_ai_magic_commands.magics.CHAT_MODELS", ["openrouter/model"]),
        patch("jupyter_ai_magic_commands.magics.litellm.completion") as completion,
    ):
        completion.return_value.choices = [Mock(message=Mock(content="Leet code"))]
        result = ip.run_cell_magic(
            "ai",
            "openrouter/model",
            cell="Write code for me please",
        )
        completion.assert_called_once_with(
            model="openrouter/model", messages=expected_context, stream=False
        )
    assert isinstance(result, Markdown)
    assert result.data == "Leet code"
    assert result.filename is None
    assert result.metadata == {"jupyter_ai_v3": {"model_id": "openrouter/model"}}
    assert result.url is None
    expected_transcript = [*transcript, PROMPT, RESPONSE]
    if max_history == 0:
        expected_transcript = []
    else:
        expected_transcript = expected_transcript[-2 * max_history :]
    assert ai_magics.transcript == expected_transcript


def test_reset(ip):
    ip.extension_manager.load_extension("jupyter_ai_magic_commands")
    ai_magics = ip.magics_manager.registry["AiMagics"]
    ai_magics.transcript = [AI1, H1, AI2, H2, AI3]
    ip.run_line_magic("ai", "reset")
    assert ai_magics.transcript == []


@pytest.mark.parametrize(
    ["output", "expected"],
    [
        ("```python\ndef add(a, b):\n    return a + b\n```", "def add(a, b):\n    return a + b"),
        (" ```python\ndef add(a, b):\n    return a + b\n```", "def add(a, b):\n    return a + b"),
        ("```\ndef add(a, b):\n    return a + b\n```", "def add(a, b):\n    return a + b"),
        ("def add(a, b):\n    return a + b", "def add(a, b):\n    return a + b"),
    ],
)
def test_display_output_strips_code_fences(ip, output, expected):
    ai_magics = AiMagics(ip)
    ip.set_next_input = Mock()

    ai_magics.display_output(output, "code", {})

    ip.set_next_input.assert_called_once_with(expected, replace=False)

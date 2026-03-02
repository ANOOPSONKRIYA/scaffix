import sys
import runpy

import pytest

from scaffix import cli


def _mock_inputs(monkeypatch, values):
    iterator = iter(values)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(iterator))


def test_format_folder_name_with_padding():
    assert cli.format_folder_name(7, 3) == "007"


def test_format_folder_name_without_padding():
    assert cli.format_folder_name(7, 0) == "7"


def test_render_preview_tree_with_overflow():
    tree = cli.render_preview_tree(1, 5, 2, ["code", "task"], preview_limit=2)
    assert "01/" in tree
    assert "├── code/" in tree
    assert "└── task/" in tree
    assert "... and 3 more folders" in tree


def test_print_progress_renders_final_line(capsys):
    cli.print_progress(3, 3, width=10)
    out = capsys.readouterr().out
    assert "3/3" in out


def test_print_progress_ignores_zero_total(capsys):
    cli.print_progress(0, 0)
    assert capsys.readouterr().out == ""


def test_get_folder_range_retries_on_invalid_input(monkeypatch):
    _mock_inputs(monkeypatch, ["abc", "2", "4"])
    assert cli.get_folder_range() == (2, 4)


def test_get_folder_range_retries_when_end_is_smaller(monkeypatch):
    _mock_inputs(monkeypatch, ["5", "2", "1", "2"])
    assert cli.get_folder_range() == (1, 2)


def test_get_zero_padding_yes(monkeypatch):
    _mock_inputs(monkeypatch, ["y"])
    assert cli.get_zero_padding(98) == 2


def test_get_zero_padding_no(monkeypatch):
    _mock_inputs(monkeypatch, ["n"])
    assert cli.get_zero_padding(98) == 0


def test_get_zero_padding_retries_on_invalid_choice(monkeypatch):
    _mock_inputs(monkeypatch, ["maybe", "yes"])
    assert cli.get_zero_padding(90) == 2


def test_get_subdirectories_parses_and_trims(monkeypatch):
    _mock_inputs(monkeypatch, [" code, task , docs "])
    assert cli.get_subdirectories() == ["code", "task", "docs"]


def test_get_subdirectories_retries_on_empty_and_invalid(monkeypatch):
    _mock_inputs(monkeypatch, ["", " , , ", "notes"])
    assert cli.get_subdirectories() == ["notes"]


def test_get_base_path_uses_current_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    _mock_inputs(monkeypatch, [""])
    assert cli.get_base_path() == str(tmp_path)


def test_get_base_path_creates_missing_path(monkeypatch, tmp_path):
    target = tmp_path / "new-output"
    _mock_inputs(monkeypatch, [str(target), "y"])
    result = cli.get_base_path()
    assert result == str(target)
    assert target.is_dir()


def test_get_base_path_retries_after_creation_failure(monkeypatch, tmp_path):
    bad_target = tmp_path / "bad-output"
    good_target = tmp_path / "good-output"

    real_makedirs = cli.os.makedirs

    def fake_makedirs(path, exist_ok):
        if str(path) == str(bad_target):
            raise OSError("cannot create")
        return real_makedirs(path, exist_ok=exist_ok)

    _mock_inputs(monkeypatch, [str(bad_target), "y", str(good_target), "y"])
    monkeypatch.setattr(cli.os, "makedirs", fake_makedirs)

    result = cli.get_base_path()
    assert result == str(good_target)
    assert good_target.is_dir()


def test_confirm_and_create_cancelled(monkeypatch, tmp_path, capsys):
    _mock_inputs(monkeypatch, ["n"])
    cli.confirm_and_create(str(tmp_path), 1, 2, 2, ["code", "task"])
    out = capsys.readouterr().out
    assert "Cancelled" in out
    assert not (tmp_path / "01").exists()


def test_confirm_and_create_generates_folders(monkeypatch, tmp_path, capsys):
    _mock_inputs(monkeypatch, [""])
    cli.confirm_and_create(str(tmp_path), 1, 2, 2, ["code", "task"])
    out = capsys.readouterr().out
    assert "DONE" in out
    assert (tmp_path / "01" / "code").is_dir()
    assert (tmp_path / "01" / "task").is_dir()
    assert (tmp_path / "02" / "code").is_dir()


def test_confirm_and_create_reports_skipped_on_error(monkeypatch, tmp_path, capsys):
    _mock_inputs(monkeypatch, [""])

    real_makedirs = cli.os.makedirs
    call_count = {"value": 0}

    def flaky_makedirs(path, exist_ok):
        call_count["value"] += 1
        if call_count["value"] == 1:
            raise OSError("boom")
        return real_makedirs(path, exist_ok=exist_ok)

    monkeypatch.setattr(cli.os, "makedirs", flaky_makedirs)
    cli.confirm_and_create(str(tmp_path), 1, 2, 0, ["code"])

    out = capsys.readouterr().out
    assert "Skipped" in out
    assert "Logs" in out


def test_configure_logging_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    logger = cli.configure_logging("test.log")
    handler_count = len(logger.handlers)
    logger_again = cli.configure_logging("test.log")
    assert logger is logger_again
    assert len(logger.handlers) == handler_count


def test_main_version_flag_exits(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["scaffix", "--version"])
    with pytest.raises(SystemExit) as exc_info:
        cli.main()
    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "Scaffix v" in out


def test_main_handles_keyboard_interrupt(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["scaffix"])
    monkeypatch.setattr(cli, "get_folder_range", lambda: (_ for _ in ()).throw(KeyboardInterrupt()))
    with pytest.raises(SystemExit) as exc_info:
        cli.main()
    assert exc_info.value.code == 0
    assert "Cancelled by user" in capsys.readouterr().out


def test_main_handles_unexpected_exception(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["scaffix"])
    monkeypatch.setattr(
        cli, "get_folder_range", lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    with pytest.raises(SystemExit) as exc_info:
        cli.main()
    assert exc_info.value.code == 1
    assert "Unexpected error" in capsys.readouterr().out


def test_main_happy_path(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["scaffix"])
    monkeypatch.setattr(cli, "get_folder_range", lambda: (1, 1))
    monkeypatch.setattr(cli, "get_zero_padding", lambda _end: 2)
    monkeypatch.setattr(cli, "get_subdirectories", lambda: ["code"])
    monkeypatch.setattr(cli, "get_base_path", lambda: "./demo")

    called = {"value": False}

    def fake_confirm(base_path, start, end, padding, subdirs):
        called["value"] = True
        assert base_path == "./demo"
        assert (start, end, padding, subdirs) == (1, 1, 2, ["code"])

    monkeypatch.setattr(cli, "confirm_and_create", fake_confirm)
    cli.main()
    assert called["value"] is True


def test_module_entrypoint_calls_main(monkeypatch):
    called = {"value": False}

    def fake_main():
        called["value"] = True

    monkeypatch.setattr("scaffix.cli.main", fake_main)
    runpy.run_module("scaffix.__main__", run_name="__main__")
    assert called["value"] is True

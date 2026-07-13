from pathlib import Path

from scripts.run_cases import archive_existing


def test_archive_existing_preserves_current_files(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    contents = {
        "config.cfg": "ITER= 100\n",
        "history.csv": "Inner_Iter,CL\n0,-0.5\n",
        "su2.log": "solver output\n",
        "forces_breakdown.dat": "forces\n",
    }
    for name, text in contents.items():
        (case / name).write_text(text, encoding="utf-8")

    archived = archive_existing(case)

    assert archived is not None
    assert archived.parent == case / "runs"
    for name, expected in contents.items():
        assert (archived / name).read_text(encoding="utf-8") == expected
        assert (case / name).read_text(encoding="utf-8") == expected


def test_archive_existing_skips_case_without_results(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    (case / "config.cfg").write_text("ITER= 100\n", encoding="utf-8")

    assert archive_existing(case) is None
    assert not (case / "runs").exists()

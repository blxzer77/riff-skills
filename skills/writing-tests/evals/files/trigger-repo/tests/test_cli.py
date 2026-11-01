from cli.main import main


def test_export_runs():
    assert main(["export"]) == 0

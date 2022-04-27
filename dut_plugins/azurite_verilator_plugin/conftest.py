# conftest.py
import pytest
import inspect
from py.xml import html


def pytest_html_report_title(report):
    report.title = "DuT Report - Chromite [Verilator Edition]"


def pytest_addoption(parser):
    parser.addoption("--make_file", action="store")
    parser.addoption("--work_dir", action="store")
    parser.addoption("--key_list", action="store")


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    cells.insert(1, html.th('Stage'))


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    cells.insert(1, html.td(report.ticket))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report.ticket = str(item.funcargs['test_input'][-1])

import typer
import re
from pathlib import Path
from loguru import logger

import reporter.parser as parser

app = typer.Typer()


@app.command()
def issues(report_path: Path):
    logger.info(f"Listing issues: {report_path}")
    lines = parser.get_lines(report_path)

    findings = parser.filter_finding_section(lines)
    for finding in findings:
        typer.echo(finding.rawline)


@app.command()
def table(report_path: Path):
    logger.info(f"Generating summary table: {report_path}")
    table_lines = parser.generate_table(report_path)

    for line in table_lines:
        typer.echo(line)


@app.command()
def override(report_path: Path):
    """ Generates the table and replaces the "Findings Summary" section in the report with the new table """

    logger.info(f"Creating and overwriting table: {report_path}")
    original_report = parser.get_lines(report_path)
    table_lines = parser.generate_table(report_path)

    new_report = []
    in_findings_section = False
    for line in original_report:
        if in_findings_section and re.match("## .*", line):
            in_findings_section = False

        if line.strip() == "## Findings Summary":
            in_findings_section = True
            new_report.extend("\n".join(table_lines))

        if in_findings_section:
            continue

        new_report.append(line)

    with open(report_path, "w") as f:
        f.writelines(new_report)


if __name__ == "__main__":
    app()

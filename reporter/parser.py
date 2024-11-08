import re
from typing import List
from pathlib import Path
from .finding import Finding


def get_lines(report_path: Path) -> List[str]:
    if not report_path.is_file():
        raise FileNotFoundError()

    with open(report_path) as f:
        lines = f.readlines()

    return lines


def filter_finding_section(lines: List[str]) -> List[Finding]:
    findings: List[Finding] = []
    in_findings_section = False
    for line in lines:
        if line.strip() == "# Findings":
            in_findings_section = True
            continue

        if re.match("# .*", line) and in_findings_section:
            break

        if not in_findings_section:
            continue

        if re.match("### .*", line):
            findings.append(Finding(rawline=line))

        team_response = re.match("#### team response: (.*)", line.lower())
        if team_response:
            findings[-1].set_team_response(team_response.groups()[0])

    return findings


def generate_table(report_path: Path) -> List[str]:
    lines_with_findings = get_lines(report_path)
    findings = filter_finding_section(lines_with_findings)

    lines = []
    lines.append("## Findings Summary")
    lines.append("")
    lines.append("| Finding | Risk | Description | Response |")
    lines.append("| :--- | :--- | :--- | :--- |")

    for finding in findings:
        lines.append(finding.row_in_summary_table())

    lines.append("")

    return lines


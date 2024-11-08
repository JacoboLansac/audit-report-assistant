from dataclasses import dataclass
import re


@dataclass
class Finding:
    rawline: str
    title: str = None
    severity_alias: str = None
    issue_id: str = None
    team_response: str = ""

    def __post_init__(self):
        if (self.rawline.count("[") > 1) or (self.rawline.count("]") > 1):
            raise ValueError(f"Invalid finding: {self.rawline}. Too many square brakets")

        match = re.match(r"### \[(.*)\] (.*)", self.rawline)
        if not match:
            raise ValueError(f"Couldn't parse finding: {self.rawline}")

        (issue_id, title) = match.groups()

        self.title = title
        self.severity_alias = str(issue_id)[0]
        self.issue_id = issue_id

    @property
    def link(self) -> str:
        """
        Following GitHub's markdown anchor rules:
        - Lowercase: Convert all characters to lowercase
        - Remove special characters except hyphens and underscores
        - Replace spaces with hyphens
        - Keep alphanumeric characters

        Example

        original:
        Users can claim from the Minter multiple times, draining the contract of SOAR tokens

        link:
        [C-1](<#c-1-users-can-claim-from-the-minter-multiple-times-draining-the-contract-of-soar-tokens>)
        """
        lower_line = f"{self.issue_id}-{self.title}".lower()
        removed_special_chars = re.sub(r"[^\-_a-zA-Z0-9\s]", "", lower_line)
        replaced_spaces = removed_special_chars.replace(" ", "-")
        return f"[[{self.issue_id}]](<#{replaced_spaces}>)"

    @property
    def severity(self) -> str:
        """
        Returns the severity of the finding
        """
        return {
            "C": "Critical",
            "H": "High",
            "M": "Medium",
            "Z": "Centralization",
            "L": "Low",
            "I": "Info",
            "G": "Gas",
        }[self.severity_alias]

    def set_team_response(self, response: str):
        if "acknowledged" in response.lower():
            response = "Ackn."
        if "fixed" in response.lower():
            response = "Fixed"

        self.team_response = response

    def row_in_summary_table(self) -> str:
        status = f"{self._icon_from_response(self.team_response)} {self.team_response}"
        return f"| {self.link} | {self.severity} | {self.title} | {status} |"

    #################
    # Private methods
    #################

    def _icon_from_response(self, response: str) -> str:
        if "fixed" in response.lower():
            return "✅"
        elif "wontfix" in response.lower():
            return "❌"
        elif "ack" in response.lower():
            return "🤝"
        elif "invalid" in response.lower():
            return "🔨"
        else:
            return ""

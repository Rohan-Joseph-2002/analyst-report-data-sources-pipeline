"""
AUTHOR: Rohan Joseph
PURPOSE: Shared repository settings, schema definitions, and extraction vocabularies.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Settings
"""

REPORT_REQUIRED_COLUMNS = [
    "DocumentID",
    "Date",
    "Year",
    "Contributor",
    "Report File Ticker",
    "Partial Title",
    "Pages",
    "PDF File Name",
    "Report Text",
]

ALTERNATIVE_SOURCE_COLUMN_MAP = {
    "List of Alternative Company Names | ATT = 1": {
        "source_group": "alternative_company_name",
        "attention_tier": "ATT = 1",
    },
    "List of Alternative Product Names | ATT = 1": {
        "source_group": "alternative_product_name",
        "attention_tier": "ATT = 1",
    },
    "List of Alternative Company Names | 0 < ATT < 1": {
        "source_group": "alternative_company_name",
        "attention_tier": "0 < ATT < 1",
    },
    "List of Alternative Product Names | 0 < ATT < 1": {
        "source_group": "alternative_product_name",
        "attention_tier": "0 < ATT < 1",
    },
    "List of Alternative Company Names | ATT = 0": {
        "source_group": "alternative_company_name",
        "attention_tier": "ATT = 0",
    },
    "List of Alternative Product Names | ATT = 0": {
        "source_group": "alternative_product_name",
        "attention_tier": "ATT = 0",
    },
}

PREPARED_REPORT_COLUMNS = [
    "DocumentID",
    "Date",
    "Year",
    "Contributor",
    "Report File Ticker",
    "Partial Title",
    "Pages",
    "PDF File Name",
    "Report Text",
    "Report Text Cleaned",
    "Report Text Preview",
    "Report Word Count",
]

PREPARED_SOURCE_COLUMNS = [
    "source_name",
    "source_name_normalized",
    "source_group",
    "attention_tier",
]

REGEX_SUMMARY_COLUMNS = [
    "DocumentID",
    "Year",
    "Date",
    "Contributor",
    "Report File Ticker",
    "Partial Title",
    "Pages",
    "PDF File Name",
    "Potential Source Phrases",
    "Regex Candidate Sources",
    "Explicit Mentioned Sources",
    "Matched Alternative Sources",
    "Matched Source Count",
]

REGEX_LONG_COLUMNS = [
    "DocumentID",
    "Year",
    "Date",
    "Contributor",
    "Report File Ticker",
    "PDF File Name",
    "Source Name",
    "Source Name Normalized",
    "Source Origin",
    "Source Group",
    "Attention Tier",
    "Match Score",
]

BASE_PHRASES = [
    "source",
    "sources",
    "sourced from",
    "according to",
    "referenced from",
    "reported by",
    "published in",
    "obtained from",
    "derived from",
    "extracted from",
    "taken from",
    "quoted from",
    "listed in",
    "disclosed by",
    "provided by",
    "compiled by",
    "courtesy of",
]

SOURCE_SPLIT_TOKENS = [
    ",",
    ";",
    " and ",
    " & ",
]

GENERIC_SOURCE_STOPWORDS = {
    "data",
    "dataset",
    "datasets",
    "estimates",
    "estimate",
    "research",
    "reports",
    "report",
    "analysis",
    "company",
    "companies",
    "public",
    "sources",
    "source",
}

SOURCE_DISQUALIFIER_PHRASES = [
    "believed to be reliable",
    "does not represent",
    "conflict of interest",
    "important disclosures",
    "legal disclaimer",
]

MOBILE_SIGNAL_KEYWORDS = [
    "mobile",
    "app",
    "apps",
    "smartphone",
    "ios",
    "android",
    "downloads",
]

REFERENCE_SOURCE_EXCLUSIONS = {
    "audiences",
    "consumer research",
    "data analytics",
    "data provider",
    "equities",
    "here",
    "hospitality and travel",
    "insights",
    "investment professionals",
    "places",
    "placed",
    "real estate",
    "store closings",
}

DEFAULT_MAX_REPORTS = 15
DEFAULT_REGEX_SIMILARITY_THRESHOLD = 0.88

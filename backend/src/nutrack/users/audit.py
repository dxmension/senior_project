"""
Degree audit logic — pure Python, no DB access.

Each DegreePlan holds a list of Categories; each Category holds
RequirementSpec objects describing what courses are needed.

Matching rules (applied to "CODE LEVEL" strings like "CSCI 151"):
  - Exact:  "CSCI 151" matches only "CSCI 151"
  - Prefix: "CSCI 3"   matches any "CSCI 3xx" course
  - Dept:   "CSCI"     matches any CSCI course (prefix with no digits)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ─── Matching helpers ────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    return s.strip().upper()


def _matches(course_code: str, pattern: str) -> bool:
    pn = _norm(pattern)
    if pn == "*":          # open elective wildcard — matches any course
        return True
    cn = _norm(course_code)
    if cn == pn:
        return True
    # prefix match — rest must be empty or start with space/digit
    if cn.startswith(pn):
        rest = cn[len(pn):]
        if not rest or rest[0] in " 0123456789":
            return True
    return False


def _course_matches_any(course_code: str, patterns: list[str]) -> bool:
    return any(_matches(course_code, p) for p in patterns)


# ─── Spec & result types ─────────────────────────────────────────────────────

@dataclass
class RequirementSpec:
    name: str
    patterns: list[str]          # course-code patterns to match against
    required_count: int = 1      # how many distinct matching courses are needed
    ects_per_course: int = 6
    note: str = ""               # shown in UI, e.g. "Any CSCI 300-400 level"
    is_elective: bool = False    # if True, courses already used elsewhere are excluded


@dataclass
class CategorySpec:
    name: str
    requirements: list[RequirementSpec]


@dataclass
class DegreePlan:
    major: str
    total_ects: int
    categories: list[CategorySpec]


# ─── Result types (returned by compute_audit) ────────────────────────────────

@dataclass
class MatchedCourse:
    code: str
    status: str  # "passed" | "in_progress"


@dataclass
class RequirementResult:
    name: str
    required_count: int
    completed_count: int
    in_progress_count: int
    status: str                          # "completed" | "in_progress" | "missing"
    matched_courses: list[MatchedCourse]
    ects_per_course: int = 6
    note: str = ""


@dataclass
class CategoryResult:
    name: str
    requirements: list[RequirementResult]
    total_ects: int = 0
    completed_ects: int = 0


@dataclass
class AuditResult:
    major: str
    supported: bool
    total_ects: int
    completed_ects: int      # ECTS counted toward tracked requirements
    in_progress_ects: int
    actual_credits_earned: int  # raw total from transcript (used for summary bar)
    categories: list[CategoryResult]


# ─── Degree plan definitions ─────────────────────────────────────────────────

# Shared university core for SEDS undergrad programs
_UNIV_CORE_SEDS = CategorySpec(
    name="University Core",
    requirements=[
        RequirementSpec("History of Kazakhstan", ["HST 100"]),
        RequirementSpec("Writing in Context I", ["WCS 150"]),
        RequirementSpec(
            "Writing in Context II",
            ["WCS 2"],
            note="Any WCS 200-level course",
        ),
        RequirementSpec(
            "Kazakh Language",
            ["KAZ"],
            required_count=2,
            note="2 KAZ language courses",
        ),
        RequirementSpec("Business Essentials", ["BUS 101"]),
        RequirementSpec("Ethics", ["PHIL 210"], note="PHIL 210"),
    ],
)

# University electives for SEDS programs
_UNIV_ELECTIVES_SEDS = CategorySpec(
    name="University Electives",
    requirements=[
        RequirementSpec(
            "Natural Science Electives",
            ["BIO", "BIOL", "CHEM", "PHYS", "ENV", "ENVS", "GEOL"],
            required_count=2,
            is_elective=True,
            note="2 Natural Science electives (beyond required courses)",
        ),
        RequirementSpec(
            "Technical Electives",
            ["CSCI 3", "CSCI 4", "EE 3", "EE 4", "CE 3", "CE 4"],
            required_count=4,
            is_elective=True,
            note="4 technical electives (CSCI/EE/CE 300–400 level, beyond core courses)",
        ),
        RequirementSpec(
            "Social Science Elective",
            ["SOC", "ANT", "PSY", "ECON", "ECO", "POL", "HST"],
            required_count=1,
            is_elective=True,
            note="1 Social Science course",
        ),
        RequirementSpec(
            "Open Elective",
            ["*"],
            required_count=1,
            is_elective=True,
            note="Any course from any department",
        ),
    ],
)

# University electives for SSH programs
_UNIV_ELECTIVES_SSH = CategorySpec(
    name="University Electives",
    requirements=[
        RequirementSpec(
            "Humanities Electives",
            ["HST", "PHIL", "ENG", "ENGL", "ART", "MUSC", "WCS", "LIT", "RUSS", "CHIN", "KORE"],
            required_count=4,
            is_elective=True,
            note="4 Humanities electives (beyond core courses)",
        ),
        RequirementSpec(
            "Social Science Electives",
            ["SOC", "ANT", "PSY", "ECON", "ECO", "POL", "HST", "GEOG"],
            required_count=3,
            is_elective=True,
            note="3 Social Science courses (beyond core courses)",
        ),
        RequirementSpec(
            "Open Elective",
            ["*"],
            required_count=1,
            is_elective=True,
            note="Any course from any department",
        ),
    ],
)

# Shared university core for SSH BA programs
_UNIV_CORE_SSH = CategorySpec(
    name="University Core",
    requirements=[
        RequirementSpec("History of Kazakhstan", ["HST 100"]),
        RequirementSpec("Writing in Context I", ["WCS 150"]),
        RequirementSpec(
            "Writing in Context II",
            ["WCS 2"],
            note="Any WCS 200-level course",
        ),
        RequirementSpec(
            "Kazakh Language",
            ["KAZ"],
            required_count=2,
            note="2 KAZ language courses",
        ),
        RequirementSpec(
            "Ethics",
            ["PHIL 210", "PHIL 211", "PHIL 212"],
            note="One ethics course (PHIL 210/211/212)",
        ),
        RequirementSpec("Business Essentials", ["BUS 101"]),
        RequirementSpec(
            "Natural Science",
            ["BIO", "BIOL", "CHEM", "PHYS", "ENV", "ENVS"],
            required_count=1,
            note="1 Natural Science course",
        ),
        RequirementSpec(
            "Mathematics",
            ["MATH"],
            required_count=1,
            note="1 MATH course",
        ),
        RequirementSpec(
            "Computing",
            ["CSCI"],
            required_count=1,
            note="1 CSCI course",
        ),
    ],
)

# University electives specifically for the CS program (different technical electives)
_UNIV_ELECTIVES_CS = CategorySpec(
    name="University Electives",
    requirements=[
        RequirementSpec(
            "Natural Science Electives",
            ["BIO", "BIOL", "CHEM", "PHYS", "ENV", "ENVS", "GEOL"],
            required_count=2,
            is_elective=True,
            note="2 Natural Science electives (beyond required courses)",
        ),
        RequirementSpec(
            "Technical Electives",
            ["CSCI 2", "CSCI 3", "CSCI 4",
             "MATH 351", "MATH 407", "MATH 417",
             "PHYS 270", "ROBT 310", "ROBT 407"],
            required_count=4,
            is_elective=True,
            note="4 technical electives (any non-required CSCI 200+ course, or MATH 351/407/417, PHYS 270, ROBT 310/407)",
        ),
        RequirementSpec(
            "Social Science Elective",
            ["SOC", "ANT", "PSY", "ECON", "ECO", "POL", "HST"],
            required_count=1,
            is_elective=True,
            note="1 Social Science course",
        ),
        RequirementSpec(
            "Open Elective",
            ["*"],
            required_count=1,
            is_elective=True,
            note="Any course from any department",
        ),
    ],
)

# ── Computer Science BSc ──────────────────────────────────────────────────────
_CS_PLAN = DegreePlan(
    major="computer science",
    total_ects=240,
    categories=[
        CategorySpec(
            "Mathematics & Science",
            requirements=[
                RequirementSpec("Calculus I", ["MATH 161"], ects_per_course=8),
                RequirementSpec("Calculus II", ["MATH 162"], ects_per_course=8),
                RequirementSpec("Physics I", ["PHYS 161"], ects_per_course=8),
                RequirementSpec("Physics II", ["PHYS 162"], ects_per_course=8),
                RequirementSpec("Linear Algebra", ["MATH 273"], ects_per_course=8),
                RequirementSpec("Discrete Mathematics", ["MATH 251"]),
                RequirementSpec("Probability", ["MATH 321"]),
                RequirementSpec("Microcontrollers", ["ROBT 206"], ects_per_course=8),
            ],
        ),
        CategorySpec(
            "Computer Science Core",
            requirements=[
                RequirementSpec("Programming I", ["CSCI 151"], ects_per_course=8),
                RequirementSpec("Programming II", ["CSCI 152"], ects_per_course=8),
                RequirementSpec("Computer Systems & Organization", ["CSCI 231"]),
                RequirementSpec("Programming Languages", ["CSCI 235"], ects_per_course=8),
                RequirementSpec("Formal Languages", ["CSCI 272"]),
                RequirementSpec("Algorithms", ["CSCI 270"]),
                RequirementSpec("Research Methods", ["CSCI 307"]),
                RequirementSpec("Operating Systems", ["CSCI 332"]),
                RequirementSpec("Computer Networks", ["CSCI 333"]),
                RequirementSpec("Database Systems", ["CSCI 341"]),
                RequirementSpec("Software Engineering", ["CSCI 361"]),
                RequirementSpec("Artificial Intelligence", ["CSCI 390"]),
            ],
        ),
        CategorySpec(
            "Capstone",
            requirements=[
                RequirementSpec("Senior Project I", ["CSCI 408"]),
                RequirementSpec("Senior Project II", ["CSCI 409"]),
            ],
        ),
        _UNIV_CORE_SEDS,
        _UNIV_ELECTIVES_CS,
    ],
)

# ── Electrical and Computer Engineering BSc ───────────────────────────────────
_ECE_PLAN = DegreePlan(
    major="electrical and computer engineering",
    total_ects=248,
    categories=[
        CategorySpec(
            "Mathematics & Science",
            requirements=[
                RequirementSpec("Calculus I", ["MATH 161"]),
                RequirementSpec("Calculus II", ["MATH 162"]),
                RequirementSpec("Linear Algebra / Differential Equations", ["MATH 201", "MATH 213"],
                                required_count=1, note="MATH 201 or MATH 213"),
                RequirementSpec("Physics I", ["PHYS 161"]),
                RequirementSpec("Physics II", ["PHYS 162"]),
            ],
        ),
        CategorySpec(
            "EE/CE Core",
            requirements=[
                RequirementSpec("Programming I", ["CSCI 151"]),
                RequirementSpec("Circuit Analysis", ["EE 201"]),
                RequirementSpec("Electronics", ["EE 2"], required_count=1, note="EE 200-level"),
                RequirementSpec("Advanced EE Courses", ["EE 3", "EE 4"], required_count=6,
                                is_elective=True, note="Advanced EE courses (300–400 level, beyond core)"),
            ],
        ),
        CategorySpec(
            "Capstone",
            requirements=[
                RequirementSpec("Senior Design I", ["EE 408", "ECE 408"]),
                RequirementSpec("Senior Design II", ["EE 409", "ECE 409"]),
            ],
        ),
        _UNIV_CORE_SEDS,
        _UNIV_ELECTIVES_SEDS,
    ],
)

# ── Civil and Environmental Engineering BSc ───────────────────────────────────
_CEE_PLAN = DegreePlan(
    major="civil and environmental engineering",
    total_ects=248,
    categories=[
        CategorySpec(
            "Mathematics & Science",
            requirements=[
                RequirementSpec("Calculus I", ["MATH 161"]),
                RequirementSpec("Calculus II", ["MATH 162"]),
                RequirementSpec("Physics I", ["PHYS 161"]),
                RequirementSpec("Chemistry", ["CHEM 161"]),
            ],
        ),
        CategorySpec(
            "Civil Engineering Core",
            requirements=[
                RequirementSpec("Statics", ["CE 201"]),
                RequirementSpec("Advanced CE Courses", ["CE 2", "CE 3", "CE 4"],
                                required_count=8, is_elective=True, note="Core CE courses (beyond CE 201)"),
            ],
        ),
        CategorySpec(
            "Capstone",
            requirements=[
                RequirementSpec("Senior Design I", ["CE 408"]),
                RequirementSpec("Senior Design II", ["CE 409"]),
            ],
        ),
        _UNIV_CORE_SEDS,
        _UNIV_ELECTIVES_SEDS,
    ],
)

# ── Mechanical and Aerospace Engineering BSc ──────────────────────────────────
_MAE_PLAN = DegreePlan(
    major="mechanical and aerospace engineering",
    total_ects=248,
    categories=[
        CategorySpec(
            "Mathematics & Science",
            requirements=[
                RequirementSpec("Calculus I", ["MATH 161"]),
                RequirementSpec("Calculus II", ["MATH 162"]),
                RequirementSpec("Physics I", ["PHYS 161"]),
                RequirementSpec("Physics II", ["PHYS 162"]),
            ],
        ),
        CategorySpec(
            "ME/AE Core",
            requirements=[
                RequirementSpec("Statics", ["ME 201", "MAE 201"]),
                RequirementSpec("Advanced ME Courses", ["ME 2", "ME 3", "ME 4", "MAE 2", "MAE 3", "MAE 4"],
                                required_count=8, is_elective=True, note="Core ME/AE courses (beyond ME 201)"),
            ],
        ),
        CategorySpec(
            "Capstone",
            requirements=[
                RequirementSpec("Senior Design I", ["ME 408", "MAE 408"]),
                RequirementSpec("Senior Design II", ["ME 409", "MAE 409"]),
            ],
        ),
        _UNIV_CORE_SEDS,
        _UNIV_ELECTIVES_SEDS,
    ],
)

# ── Chemical and Materials Engineering BSc ────────────────────────────────────
_CME_PLAN = DegreePlan(
    major="chemical and materials engineering",
    total_ects=248,
    categories=[
        CategorySpec(
            "Mathematics & Science",
            requirements=[
                RequirementSpec("Calculus I", ["MATH 161"]),
                RequirementSpec("Calculus II", ["MATH 162"]),
                RequirementSpec("Physics I", ["PHYS 161"]),
                RequirementSpec("Chemistry I", ["CHEM 161"]),
                RequirementSpec("Chemistry II", ["CHEM 162"]),
            ],
        ),
        CategorySpec(
            "ChE/MatE Core",
            requirements=[
                RequirementSpec("Advanced CHE/MAT Courses", ["CHE 2", "CHE 3", "CHE 4", "MAT 2", "MAT 3", "MAT 4"],
                                required_count=8, is_elective=True, note="Core ChE/MatE courses"),
            ],
        ),
        CategorySpec(
            "Capstone",
            requirements=[
                RequirementSpec("Senior Design I", ["CHE 408"]),
                RequirementSpec("Senior Design II", ["CHE 409"]),
            ],
        ),
        _UNIV_CORE_SEDS,
        _UNIV_ELECTIVES_SEDS,
    ],
)

# ── Mathematics BSc (SSH) ─────────────────────────────────────────────────────
_MATH_PLAN = DegreePlan(
    major="mathematics",
    total_ects=240,
    categories=[
        CategorySpec(
            "Mathematics Core",
            requirements=[
                RequirementSpec("Calculus I", ["MATH 161"]),
                RequirementSpec("Calculus II", ["MATH 162"]),
                RequirementSpec("Linear Algebra", ["MATH 201"]),
                RequirementSpec("Differential Equations", ["MATH 213"]),
                RequirementSpec(
                    "Advanced Mathematics",
                    ["MATH 2", "MATH 3", "MATH 4"],
                    required_count=6,
                    is_elective=True,
                    note="Advanced MATH courses (200–400 level, beyond MATH 161/162)",
                ),
            ],
        ),
        CategorySpec(
            "Supporting Sciences",
            requirements=[
                RequirementSpec("Physics I", ["PHYS 161"]),
                RequirementSpec(
                    "Computing",
                    ["CSCI"],
                    required_count=1,
                    note="1 CSCI course",
                ),
            ],
        ),
        _UNIV_CORE_SSH,
        _UNIV_ELECTIVES_SSH,
    ],
)

# ── Physics BSc (SSH) ─────────────────────────────────────────────────────────
_PHYSICS_PLAN = DegreePlan(
    major="physics",
    total_ects=240,
    categories=[
        CategorySpec(
            "Physics Core",
            requirements=[
                RequirementSpec("Physics I", ["PHYS 161"]),
                RequirementSpec("Physics II", ["PHYS 162"]),
                RequirementSpec(
                    "Advanced Physics",
                    ["PHYS 2", "PHYS 3", "PHYS 4"],
                    required_count=6,
                    is_elective=True,
                    note="Advanced Physics courses (beyond PHYS 161/162)",
                ),
            ],
        ),
        CategorySpec(
            "Supporting Mathematics",
            requirements=[
                RequirementSpec("Calculus I", ["MATH 161"]),
                RequirementSpec("Calculus II", ["MATH 162"]),
                RequirementSpec(
                    "Advanced Mathematics",
                    ["MATH 2", "MATH 3"],
                    required_count=2,
                    is_elective=True,
                    note="2 advanced MATH courses (beyond MATH 161/162)",
                ),
            ],
        ),
        _UNIV_CORE_SSH,
        _UNIV_ELECTIVES_SSH,
    ],
)

# ── Chemistry BSc (SSH) ───────────────────────────────────────────────────────
_CHEMISTRY_PLAN = DegreePlan(
    major="chemistry",
    total_ects=240,
    categories=[
        CategorySpec(
            "Chemistry Core",
            requirements=[
                RequirementSpec("General Chemistry I", ["CHEM 161"]),
                RequirementSpec("General Chemistry II", ["CHEM 162"]),
                RequirementSpec(
                    "Organic Chemistry",
                    ["CHEM 2"],
                    required_count=1,
                    is_elective=True,
                    note="Organic Chemistry (CHEM 200-level)",
                ),
                RequirementSpec(
                    "Advanced Chemistry",
                    ["CHEM 3", "CHEM 4"],
                    required_count=4,
                    is_elective=True,
                    note="Advanced Chemistry courses (beyond CHEM 161/162)",
                ),
            ],
        ),
        CategorySpec(
            "Supporting Sciences",
            requirements=[
                RequirementSpec("Calculus I", ["MATH 161"]),
                RequirementSpec("Physics I", ["PHYS 161"]),
            ],
        ),
        _UNIV_CORE_SSH,
        _UNIV_ELECTIVES_SSH,
    ],
)

# ── Biology BSc (SSH) ─────────────────────────────────────────────────────────
_BIOLOGY_PLAN = DegreePlan(
    major="biological sciences",
    total_ects=240,
    categories=[
        CategorySpec(
            "Biology Core",
            requirements=[
                RequirementSpec("Biology I", ["BIO 161", "BIOL 161"]),
                RequirementSpec("Biology II", ["BIO 162", "BIOL 162"]),
                RequirementSpec(
                    "Advanced Biology",
                    ["BIO 2", "BIO 3", "BIO 4", "BIOL 2", "BIOL 3", "BIOL 4"],
                    required_count=5,
                    is_elective=True,
                    note="Advanced Biology courses (beyond BIO 161/162)",
                ),
            ],
        ),
        CategorySpec(
            "Supporting Sciences",
            requirements=[
                RequirementSpec("Chemistry I", ["CHEM 161"]),
                RequirementSpec("Calculus", ["MATH 161"]),
            ],
        ),
        _UNIV_CORE_SSH,
        _UNIV_ELECTIVES_SSH,
    ],
)

# ── Economics BA (SSH) ────────────────────────────────────────────────────────
_ECONOMICS_PLAN = DegreePlan(
    major="economics",
    total_ects=240,
    categories=[
        CategorySpec(
            "Economics Core",
            requirements=[
                RequirementSpec(
                    "Intro Economics",
                    ["ECON 101", "ECO 101"],
                    note="Principles of Economics",
                ),
                RequirementSpec("Microeconomics", ["ECON 201", "ECO 201"]),
                RequirementSpec("Macroeconomics", ["ECON 202", "ECO 202"]),
                RequirementSpec(
                    "Econometrics / Statistics",
                    ["ECON 3", "ECO 3", "STAT"],
                    required_count=1,
                    note="Econometrics or Statistics",
                ),
                RequirementSpec(
                    "Advanced Economics Electives",
                    ["ECON 3", "ECON 4", "ECO 3", "ECO 4"],
                    required_count=4,
                    is_elective=True,
                    note="4 advanced Economics electives (beyond core courses)",
                ),
            ],
        ),
        CategorySpec(
            "Quantitative Methods",
            requirements=[
                RequirementSpec("Calculus", ["MATH 161"]),
                RequirementSpec(
                    "Statistics / Math",
                    ["MATH 1", "MATH 2", "STAT"],
                    required_count=1,
                    note="Statistics or Math course",
                ),
            ],
        ),
        _UNIV_CORE_SSH,
        _UNIV_ELECTIVES_SSH,
    ],
)

# ── History BA (SSH) ──────────────────────────────────────────────────────────
_HISTORY_PLAN = DegreePlan(
    major="history",
    total_ects=240,
    categories=[
        CategorySpec(
            "History Core",
            requirements=[
                RequirementSpec("History of Kazakhstan", ["HST 100"]),
                RequirementSpec(
                    "Advanced History Courses",
                    ["HST 2", "HST 3", "HST 4"],
                    required_count=8,
                    is_elective=True,
                    note="Advanced History courses (beyond HST 100)",
                ),
            ],
        ),
        _UNIV_CORE_SSH,
        _UNIV_ELECTIVES_SSH,
    ],
)

# ── Political Science BA (SSH) ────────────────────────────────────────────────
_POLS_PLAN = DegreePlan(
    major="political science and international relations",
    total_ects=240,
    categories=[
        CategorySpec(
            "Political Science Core",
            requirements=[
                RequirementSpec(
                    "Intro Political Science",
                    ["POL 101", "POLS 101"],
                    note="Intro to Political Science",
                ),
                RequirementSpec(
                    "Advanced POLS Courses",
                    ["POL 2", "POL 3", "POL 4", "POLS 2", "POLS 3", "POLS 4", "IR 2", "IR 3", "IR 4"],
                    required_count=7,
                    is_elective=True,
                    note="Advanced Political Science / IR courses (beyond intro)",
                ),
            ],
        ),
        _UNIV_CORE_SSH,
        _UNIV_ELECTIVES_SSH,
    ],
)

# ── Sociology BA (SSH) ────────────────────────────────────────────────────────
_SOCIOLOGY_PLAN = DegreePlan(
    major="sociology",
    total_ects=240,
    categories=[
        CategorySpec(
            "Sociology Core",
            requirements=[
                RequirementSpec("Intro Sociology", ["SOC 101"]),
                RequirementSpec(
                    "Advanced Sociology Courses",
                    ["SOC 2", "SOC 3", "SOC 4"],
                    required_count=7,
                    is_elective=True,
                    note="Advanced Sociology courses (beyond SOC 101)",
                ),
            ],
        ),
        _UNIV_CORE_SSH,
        _UNIV_ELECTIVES_SSH,
    ],
)

# ── Anthropology BA (SSH) ─────────────────────────────────────────────────────
_ANTHROPOLOGY_PLAN = DegreePlan(
    major="anthropology",
    total_ects=240,
    categories=[
        CategorySpec(
            "Anthropology Core",
            requirements=[
                RequirementSpec("Intro Anthropology", ["ANT 101"]),
                RequirementSpec(
                    "Advanced Anthropology Courses",
                    ["ANT 2", "ANT 3", "ANT 4"],
                    required_count=7,
                    is_elective=True,
                    note="Advanced Anthropology courses (beyond ANT 101)",
                ),
            ],
        ),
        _UNIV_CORE_SSH,
        _UNIV_ELECTIVES_SSH,
    ],
)

# ── Registry ──────────────────────────────────────────────────────────────────

_PLANS: dict[str, DegreePlan] = {
    "computer science": _CS_PLAN,
    "electrical and computer engineering": _ECE_PLAN,
    "civil and environmental engineering": _CEE_PLAN,
    "mechanical and aerospace engineering": _MAE_PLAN,
    "chemical and materials engineering": _CME_PLAN,
    "mathematics": _MATH_PLAN,
    "physics": _PHYSICS_PLAN,
    "chemistry": _CHEMISTRY_PLAN,
    "biological sciences": _BIOLOGY_PLAN,
    "biology": _BIOLOGY_PLAN,
    "economics": _ECONOMICS_PLAN,
    "history": _HISTORY_PLAN,
    "history and culture": _HISTORY_PLAN,
    "political science and international relations": _POLS_PLAN,
    "political sciences and international relations": _POLS_PLAN,
    "sociology": _SOCIOLOGY_PLAN,
    "anthropology": _ANTHROPOLOGY_PLAN,
}


# ─── Dynamic plan loader (from handbook JSON stored in DB) ───────────────────

def _plan_from_json(major_key: str, data: dict[str, Any]) -> DegreePlan | None:
    """
    Deserialise a single major's plan from the JSON stored by HandbookService.
    Returns None if the data is malformed.
    """
    try:
        categories: list[CategorySpec] = []
        for cat_data in data.get("categories", []):
            reqs: list[RequirementSpec] = []
            for r in cat_data.get("requirements", []):
                reqs.append(RequirementSpec(
                    name=r.get("name", ""),
                    patterns=r.get("patterns", []),
                    required_count=int(r.get("required_count", 1)),
                    ects_per_course=int(r.get("ects_per_course", 6)),
                    is_elective=bool(r.get("is_elective", False)),
                    note=r.get("note", ""),
                ))
            categories.append(CategorySpec(name=cat_data.get("name", ""), requirements=reqs))
        return DegreePlan(
            major=major_key,
            total_ects=int(data.get("total_ects", 240)),
            categories=categories,
        )
    except Exception:
        return None


def resolve_plan(major: str, handbook_plans: dict[str, Any] | None) -> DegreePlan | None:
    """
    Try the handbook JSON first (if provided), then fall back to hardcoded _PLANS.
    """
    major_key = major.strip().lower()
    if handbook_plans:
        for key, data in handbook_plans.items():
            if key.strip().lower() == major_key:
                plan = _plan_from_json(major_key, data)
                if plan:
                    return plan
    return _PLANS.get(major_key)


# ─── Audit computation ───────────────────────────────────────────────────────

def compute_audit(
    major: str,
    courses: list[tuple[str, str]],  # (course_code, status) e.g. [("CSCI 151", "passed")]
    credits_earned: int = 0,
    handbook_plans: dict[str, Any] | None = None,
) -> AuditResult:
    """
    Compute a degree audit.

    Args:
        major: The student's declared major (case-insensitive).
        courses: List of (course_code, enrollment_status) pairs.
                 Status is "passed" | "in_progress" | other (ignored).
        credits_earned: Total ECTS credited to the student.

    Returns:
        AuditResult with per-category, per-requirement breakdown.
    """
    plan = resolve_plan(major, handbook_plans)

    if plan is None:
        return AuditResult(
            major=major,
            supported=False,
            total_ects=0,
            completed_ects=0,
            in_progress_ects=0,
            actual_credits_earned=credits_earned,
            categories=[],
        )

    passed = {_norm(code) for code, st in courses if st == "passed"}
    in_prog = {_norm(code) for code, st in courses if st == "in_progress"}

    def _is_open_elective(req: RequirementSpec) -> bool:
        return req.is_elective and req.patterns == ["*"]

    def _consume(
        pool_passed: set[str],
        pool_ip: set[str],
        req: RequirementSpec,
        sink_passed: set[str],
        sink_ip: set[str],
    ) -> None:
        """Add up to required_count matching courses from pools into sinks."""
        used = 0
        for code in sorted(pool_passed):
            if used >= req.required_count:
                break
            if _course_matches_any(code, req.patterns):
                sink_passed.add(code)
                used += 1
        for code in sorted(pool_ip):
            if used >= req.required_count:
                break
            if _course_matches_any(code, req.patterns):
                sink_ip.add(code)
                used += 1

    # Pass 1 — Core requirements (is_elective=False) have first claim on all courses.
    consumed_passed: set[str] = set()
    consumed_ip: set[str] = set()
    for cat_spec in plan.categories:
        for req in cat_spec.requirements:
            if not req.is_elective:
                _consume(passed, in_prog, req, consumed_passed, consumed_ip)

    # Pass 2 — Specific electives (is_elective=True, non-wildcard) consume what's left.
    elective_passed: set[str] = set()
    elective_ip: set[str] = set()
    for cat_spec in plan.categories:
        for req in cat_spec.requirements:
            if req.is_elective and not _is_open_elective(req):
                avail_p = passed - consumed_passed - elective_passed
                avail_i = in_prog - consumed_ip - elective_ip
                _consume(avail_p, avail_i, req, elective_passed, elective_ip)

    # Pass 3 — Open electives ("*") only see whatever remains after passes 1 & 2.
    # (no pre-computation needed — availability is derived at render time below)

    total_completed_ects = 0
    total_in_progress_ects = 0
    category_results: list[CategoryResult] = []

    for cat_spec in plan.categories:
        req_results: list[RequirementResult] = []
        cat_completed_ects = 0
        cat_total_ects = 0

        for req in cat_spec.requirements:
            ects = req.ects_per_course
            cat_total_ects += req.required_count * ects

            if not req.is_elective:
                # Core: sees all courses
                avail_passed = passed
                avail_ip = in_prog
            elif _is_open_elective(req):
                # Open elective: sees only courses not yet consumed by core or specific electives
                avail_passed = passed - consumed_passed - elective_passed
                avail_ip = in_prog - consumed_ip - elective_ip
            else:
                # Specific elective: sees courses not consumed by core
                avail_passed = passed - consumed_passed
                avail_ip = in_prog - consumed_ip

            matched: list[MatchedCourse] = []
            seen: set[str] = set()

            for code in sorted(avail_passed):
                if code not in seen and _course_matches_any(code, req.patterns):
                    matched.append(MatchedCourse(code=code, status="passed"))
                    seen.add(code)

            for code in sorted(avail_ip):
                if code not in seen and _course_matches_any(code, req.patterns):
                    matched.append(MatchedCourse(code=code, status="in_progress"))
                    seen.add(code)

            completed_count = sum(1 for m in matched if m.status == "passed")
            ip_count = sum(1 for m in matched if m.status == "in_progress")

            # Only count up to required_count toward credit
            effective_completed = min(completed_count, req.required_count)
            effective_ip = min(ip_count, max(0, req.required_count - completed_count))

            cat_completed_ects += effective_completed * ects
            total_in_progress_ects += effective_ip * ects

            if completed_count >= req.required_count:
                status = "completed"
            elif completed_count + ip_count > 0:
                status = "in_progress"
            else:
                status = "missing"

            req_results.append(
                RequirementResult(
                    name=req.name,
                    required_count=req.required_count,
                    completed_count=completed_count,
                    in_progress_count=ip_count,
                    status=status,
                    # For specific electives, cap display at required_count so overflow
                    # courses don't appear as matched here AND in the open elective pool.
                    # Core and open elective requirements keep the +2 buffer.
                    matched_courses=matched[:req.required_count] if (req.is_elective and not _is_open_elective(req)) else matched[:req.required_count + 2],
                    ects_per_course=ects,
                    note=req.note,
                )
            )

        total_completed_ects += cat_completed_ects
        category_results.append(
            CategoryResult(
                name=cat_spec.name,
                requirements=req_results,
                total_ects=cat_total_ects,
                completed_ects=cat_completed_ects,
            )
        )

    return AuditResult(
        major=major,
        supported=True,
        total_ects=plan.total_ects,
        completed_ects=total_completed_ects,
        in_progress_ects=total_in_progress_ects,
        actual_credits_earned=credits_earned,
        categories=category_results,
    )

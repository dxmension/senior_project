from __future__ import annotations

from datetime import datetime, timezone

from nutrack.config import settings

# ── design tokens (copied from globals.css) ───────────────────────────────────

_BG_PAGE = "#0d0d0d"
_BG_CARD = "#161616"
_BG_ROW = "#1a1a1a"
_BORDER = "#2a2a2a"
_TEXT_PRIMARY = "#f5f5f5"
_TEXT_SECONDARY = "#a0a0a0"
_TEXT_MUTED = "#666666"
_GREEN = "#a3e635"
_GREEN_TEXT_ON = "#0d0d0d"   # dark text written on top of the green button
_ORANGE = "#fb923c"
_RED = "#f87171"

# ── assessment-type badge palette ─────────────────────────────────────────────
# Mirrors BADGE_STYLES in courses/[course_id]/page.tsx

_BADGE: dict[str, tuple[str, str]] = {
    "midterm":      ("#3d1515", "#f87171"),
    "final":        ("#3d1515", "#f87171"),
    "project":      ("#1e1535", "#c084fc"),
    "homework":     ("#0f2035", "#60a5fa"),
    "quiz":         ("#2d1a00", "#fb923c"),
    "lab":          ("#0d2620", "#34d399"),
    "presentation": ("#2a2000", "#fbbf24"),
    "other":        ("#1e1e1e", "#a0a0a0"),
}

_ASSESSMENT_LABELS: dict[str, str] = {
    "midterm":      "Midterm",
    "final":        "Final Exam",
    "project":      "Project",
    "homework":     "Homework",
    "quiz":         "Quiz",
    "lab":          "Lab",
    "presentation": "Presentation",
    "other":        "Other",
}


# ── helpers ───────────────────────────────────────────────────────────────────

def _urgency_color(iso_deadline: str) -> str:
    """Return a colour that conveys how close the deadline is."""
    dt = datetime.fromisoformat(iso_deadline).astimezone(timezone.utc)
    hours_left = (dt - datetime.now(tz=timezone.utc)).total_seconds() / 3600
    if hours_left < 24:
        return _RED
    if hours_left < 48:
        return _ORANGE
    return _TEXT_SECONDARY


def _fmt_deadline(iso_deadline: str) -> str:
    dt = datetime.fromisoformat(iso_deadline).astimezone(timezone.utc)
    return dt.strftime("%A, %B %d at %I:%M %p UTC")


def _course_url(course_id: int) -> str:
    """Deep-link to the Materials tab of the course-detail page."""
    base = settings.FRONTEND_URL.rstrip("/")
    return f"{base}/courses/{course_id}?tab=materials"


def _assessment_card(a: dict) -> str:
    """Render one assessment row as a self-contained HTML block."""
    atype = a["assessment_type"].lower()
    badge_bg, badge_text = _BADGE.get(atype, _BADGE["other"])
    label = _ASSESSMENT_LABELS.get(atype, atype.capitalize())
    deadline_str = _fmt_deadline(a["deadline"])
    urgency_color = _urgency_color(a["deadline"])
    url = _course_url(a["course_id"])

    return f"""
<table width="100%" cellpadding="0" cellspacing="0"
       style="background:{_BG_ROW};border:1px solid {_BORDER};border-radius:12px;
              margin-bottom:12px;overflow:hidden;">
  <tr>
    <td style="padding:16px 20px;">

      <!-- badge + title -->
      <table cellpadding="0" cellspacing="0">
        <tr>
          <td style="vertical-align:middle;padding-right:10px;">
            <span style="display:inline-block;background:{badge_bg};color:{badge_text};
                         font-size:10px;font-weight:700;padding:3px 9px;border-radius:6px;
                         text-transform:uppercase;letter-spacing:0.6px;white-space:nowrap;">
              {label}
            </span>
          </td>
          <td style="vertical-align:middle;">
            <span style="font-size:15px;font-weight:600;color:{_TEXT_PRIMARY};">
              {a["title"]}
            </span>
          </td>
        </tr>
      </table>

      <!-- course -->
      <p style="margin:8px 0 4px;font-size:12px;color:{_TEXT_SECONDARY};">
        {a["course_code"]} &mdash; {a["course_title"]}
      </p>

      <!-- deadline -->
      <p style="margin:0 0 14px;font-size:12px;color:{urgency_color};">
        &#128197; Due {deadline_str}
      </p>

      <!-- CTA -->
      <a href="{url}"
         style="display:inline-block;background:{_GREEN};color:{_GREEN_TEXT_ON};
                font-size:12px;font-weight:700;padding:8px 18px;border-radius:8px;
                text-decoration:none;letter-spacing:0.2px;">
        View course materials &rarr;
      </a>

    </td>
  </tr>
</table>"""


# ── public builder ────────────────────────────────────────────────────────────

def build_html_email(first_name: str, assessments: list[dict]) -> str:
    """Return a complete HTML email string for the given assessment list.

    Args:
        first_name: Recipient's first name used in the greeting.
        assessments: List of assessment dicts.  Each must contain:
            ``id``, ``title``, ``assessment_type``, ``course_id``,
            ``course_code``, ``course_title``, ``deadline`` (ISO-8601).
    """
    count = len(assessments)
    noun = "assessment" if count == 1 else "assessments"
    verb = "is" if count == 1 else "are"

    cards_html = "\n".join(
        _assessment_card(a)
        for a in sorted(assessments, key=lambda x: x["deadline"])
    )

    profile_url = f"{settings.FRONTEND_URL.rstrip('/')}/settings"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Upcoming Assessments &mdash; Nutrack</title>
</head>
<body style="margin:0;padding:0;background:{_BG_PAGE};
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,
             Arial,sans-serif;color:{_TEXT_PRIMARY};-webkit-text-size-adjust:100%;">

  <!-- outer wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0"
         style="background:{_BG_PAGE};padding:40px 16px;">
    <tr>
      <td align="center">

        <!-- content column, max 600 px -->
        <table width="100%" cellpadding="0" cellspacing="0"
               style="max-width:600px;">

          <!-- ── logo row ─────────────────────────────────────────────── -->
          <tr>
            <td style="padding-bottom:28px;">
              <span style="font-size:22px;font-weight:800;color:{_GREEN};
                           letter-spacing:-0.5px;">nutrack</span>
            </td>
          </tr>

          <!-- ── main card ─────────────────────────────────────────────── -->
          <tr>
            <td style="background:{_BG_CARD};border:1px solid {_BORDER};
                       border-radius:16px;padding:28px 28px 24px;">

              <!-- greeting -->
              <p style="margin:0 0 6px;font-size:24px;font-weight:700;
                        color:{_TEXT_PRIMARY};letter-spacing:-0.4px;">
                Hi {first_name} &#128075;
              </p>
              <p style="margin:0 0 24px;font-size:14px;color:{_TEXT_SECONDARY};
                        line-height:1.6;">
                You have <strong style="color:{_TEXT_PRIMARY};">{count} upcoming
                {noun}</strong> that {verb} due within the next 3&nbsp;days.
              </p>

              <!-- divider -->
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="margin-bottom:20px;">
                <tr>
                  <td style="border-top:1px solid {_BORDER};font-size:0;">&nbsp;</td>
                </tr>
              </table>

              <!-- assessment cards -->
              {cards_html}

            </td>
          </tr>

          <!-- ── footer ────────────────────────────────────────────────── -->
          <tr>
            <td style="padding-top:28px;text-align:center;">
              <p style="margin:0 0 6px;font-size:12px;color:{_TEXT_MUTED};
                        line-height:1.6;">
                Good luck with your studies!<br>
                &mdash; The Nutrack Team
              </p>
              <p style="margin:16px 0 0;font-size:11px;color:{_TEXT_MUTED};">
                You're receiving this because you opted into assessment reminders.<br>
                Manage your preferences in your&nbsp;<a href="{profile_url}"
                  style="color:{_GREEN};text-decoration:none;">Nutrack&nbsp;settings</a>.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>"""

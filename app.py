import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Lab Operations Tracker", page_icon="🖥️", layout="wide")

VENUES = {
    "E LES COMP": ["LAB 201", "LAB 202", "LAB 203", "LAB 204"],
    "D1 LAB COMP": ["LAB 108", "LAB 109", "LAB 110"],
    "C RING COMP": ["LAB 307", "LAB 303"],
    "E RING COMP": ["LAB 203", "LAB 204", "LAB 205", "LAB 206", "LAB 207"],
}

CATEGORIES = ["Computer", "Network/Internet", "Keyboard/Mouse", "Projector", "Software", "Power", "Other"]

if "reports" not in st.session_state:
    st.session_state.reports = []
if "issues_draft" not in st.session_state:
    st.session_state.issues_draft = []

def reset_draft():
    st.session_state.issues_draft = []

st.title("🖥️ Lab Operations Tracker")
st.caption("POC — University of Johannesburg | Replaces manual Excel-based Daily Lab Maintenance Report")

page = st.sidebar.radio("Navigation", ["Lab Assistant", "Team Leader Dashboard"])

# ============================================================
# LAB ASSISTANT PAGE
# ============================================================
if page == "Lab Assistant":
    st.header("📋 Daily Lab Report")

    col1, col2 = st.columns(2)
    with col1:
        venue = st.selectbox("Venue", list(VENUES.keys()))
    with col2:
        lab = st.selectbox("Lab", VENUES[venue])

    col3, col4 = st.columns(2)
    with col3:
        staff_name = st.text_input("Technical Assistant Name")
    with col4:
        report_date = st.date_input("Date", value=date.today())

    status = st.radio("Overall Status", ["No Issues", "Issues Identified"], horizontal=True)

    if status == "Issues Identified":
        st.subheader("Log an Issue")
        with st.form("issue_form", clear_on_submit=True):
            ic1, ic2 = st.columns(2)
            with ic1:
                equipment = st.text_input("Computer/Equipment Identifier (e.g. C09)")
            with ic2:
                category = st.selectbox("Category", CATEGORIES)
            description = st.text_area("Issue Description")
            notes = st.text_input("Optional Notes")
            add_issue = st.form_submit_button("➕ Add Issue")

            if add_issue:
                if equipment and description:
                    st.session_state.issues_draft.append({
                        "equipment": equipment,
                        "category": category,
                        "description": description,
                        "notes": notes,
                    })
                    st.success(f"Issue added for {equipment}.")
                else:
                    st.warning("Equipment identifier and description are required.")

        if st.session_state.issues_draft:
            st.write("**Issues logged so far:**")
            st.table(pd.DataFrame(st.session_state.issues_draft))

    st.divider()

    if st.button("✅ SUBMIT REPORT", type="primary", use_container_width=True):
        if not staff_name:
            st.error("Please enter the technical assistant's name.")
        elif status == "Issues Identified" and not st.session_state.issues_draft:
            st.error("You selected 'Issues Identified' but haven't logged any issues yet.")
        else:
            report = {
                "venue": venue,
                "lab": lab,
                "staff": staff_name,
                "date": report_date,
                "status": status,
                "issues": list(st.session_state.issues_draft),
            }
            st.session_state.reports.append(report)
            reset_draft()
            st.success(f"✅ Report submitted for {venue} – {lab} ({report_date}).")
            st.balloons()

# ============================================================
# TEAM LEADER DASHBOARD
# ============================================================
else:
    st.header("📊 Team Leader Dashboard")
    reports = st.session_state.reports

    total = len(reports)
    with_issues = sum(1 for r in reports if r["status"] == "Issues Identified")
    no_issues = total - with_issues
    open_issues = sum(len(r["issues"]) for r in reports)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Reports", total)
    c2.metric("Issues Identified", with_issues)
    c3.metric("No-Issue Reports", no_issues)
    c4.metric("Open Issues", open_issues)

    st.divider()

    if not reports:
        st.info("No reports submitted yet. Submit one from the Lab Assistant page.")
    else:
        st.subheader("🔍 Filter Reports")
        f1, f2, f3 = st.columns(3)
        with f1:
            venue_filter = st.selectbox("Venue", ["All"] + list(VENUES.keys()))
        with f2:
            lab_options = ["All"] + (VENUES[venue_filter] if venue_filter != "All" else sorted({l for labs in VENUES.values() for l in labs}))
            lab_filter = st.selectbox("Lab", lab_options)
        with f3:
            date_filter = st.date_input("Date", value=None)

        filtered = reports
        if venue_filter != "All":
            filtered = [r for r in filtered if r["venue"] == venue_filter]
        if lab_filter != "All":
            filtered = [r for r in filtered if r["lab"] == lab_filter]
        if date_filter:
            filtered = [r for r in filtered if r["date"] == date_filter]

        st.subheader(f"Reports ({len(filtered)})")
        summary_df = pd.DataFrame([{
            "Venue": r["venue"], "Lab": r["lab"], "Staff": r["staff"],
            "Date": r["date"], "Status": r["status"], "# Issues": len(r["issues"])
        } for r in filtered])
        st.dataframe(summary_df, use_container_width=True)

        st.divider()
        st.subheader("📄 Report Detail & Generation")
        idx = st.selectbox(
            "Select a report to view",
            range(len(filtered)),
            format_func=lambda i: f"{filtered[i]['venue']} – {filtered[i]['lab']} – {filtered[i]['staff']} – {filtered[i]['date']}"
        )
        r = filtered[idx]

        colA, colB = st.columns(2)
        with colA:
            st.write(f"**Venue:** {r['venue']}")
            st.write(f"**Lab:** {r['lab']}")
            st.write(f"**Staff Member:** {r['staff']}")
        with colB:
            st.write(f"**Date:** {r['date']}")
            st.write(f"**Overall Status:** {r['status']}")

        if r["issues"]:
            st.write("**Issues:**")
            st.table(pd.DataFrame(r["issues"]))
        else:
            st.write("No issues logged.")

        if st.button("📝 GENERATE REPORT"):
            lines = [
                "LAB OPERATIONS REPORT",
                "",
                f"Venue: {r['venue']}",
                f"Lab: {r['lab']}",
                f"Date: {r['date']}",
                f"Staff Member: {r['staff']}",
                "",
                f"Overall Status: {r['status']}",
                "",
                "Issues Identified:",
            ]
            if r["issues"]:
                for i, issue in enumerate(r["issues"], 1):
                    lines.append(f"{i}. [{issue['category']}] {issue['equipment']}: {issue['description']}" + (f" (Notes: {issue['notes']})" if issue['notes'] else ""))
            else:
                lines.append("None")
            lines += ["", "Outstanding Issues:", "..." , "", "Next Steps:", "..."]
            report_text = "\n".join(lines)
            st.code(report_text, language=None)
            st.download_button("⬇️ Download Report (.txt)", report_text, file_name=f"{r['lab'].replace(' ','_')}_{r['date']}.txt")

        st.divider()
        st.subheader("🚨 Venues Currently With Issues")
        issue_venues = {}
        for rep in reports:
            if rep["status"] == "Issues Identified":
                issue_venues.setdefault(rep["venue"], set()).add(rep["lab"])
        if issue_venues:
            for v, labs in issue_venues.items():
                st.write(f"**{v}**: {', '.join(sorted(labs))}")
        else:
            st.write("No venues currently reporting issues.")

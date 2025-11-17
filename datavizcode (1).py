import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="University Student Analytics",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Normalizar nombres de columnas
    new_cols = []
    for c in df.columns:
        nc = c.strip().lower()
        nc = nc.replace("(", "").replace(")", "")
        nc = nc.replace("%", "")
        nc = nc.replace(" ", "_")
        nc = nc.rstrip("_")
        new_cols.append(nc)
    df.columns = new_cols

    if "term" in df.columns:
        df["term"] = df["term"].astype(str).str.strip().str.title()

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    numeric_cols = [
        "applications", "admitted", "enrolled",
        "retention_rate", "student_satisfaction",
        "engineering_enrolled", "business_enrolled",
        "arts_enrolled", "science_enrolled",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

DATA_PATH = "university_student_data.csv"
df = load_data(DATA_PATH)

with st.sidebar:
    st.header("🔎 Filters")

    if "year" in df.columns:
        years = sorted(df["year"].dropna().unique().tolist())
        year_sel = st.multiselect("Year", options=years, default=years)
    else:
        year_sel = None

    if "term" in df.columns:
        terms = sorted(df["term"].dropna().unique().tolist())
        term_sel = st.multiselect("Term", options=terms, default=terms)
    else:
        term_sel = None

mask = pd.Series(True, index=df.index)

if year_sel is not None and len(year_sel) > 0:
    mask &= df["year"].isin(year_sel)

if term_sel is not None and len(term_sel) > 0 and "term" in df.columns:
    mask &= df["term"].isin(term_sel)

fdf = df[mask].copy()

if fdf.empty:
    st.error("No data available for the selected filters. Try selecting more years or terms.")
    st.stop()

st.title("📊 University Student Analytics")
st.caption("Admissions • Enrollment • Retention • Student Satisfaction — Interactive Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    total_enrolled = int(fdf["enrolled"].sum()) if "enrolled" in fdf.columns else 0
    st.metric("Total Enrolled (filtered)", f"{total_enrolled:,}")

with col2:
    if "retention_rate" in fdf.columns:
        avg_ret = fdf["retention_rate"].mean()
        st.metric("Avg Retention Rate", f"{avg_ret:.1f}%" if not np.isnan(avg_ret) else "N/A")
    else:
        st.metric("Avg Retention Rate", "N/A")

with col3:
    if "student_satisfaction" in fdf.columns:
        avg_sat = fdf["student_satisfaction"].mean()
        st.metric("Avg Student Satisfaction", f"{avg_sat:.1f}%" if not np.isnan(avg_sat) else "N/A")
    else:
        st.metric("Avg Student Satisfaction", "N/A")

st.markdown("---")

if {"year", "retention_rate"}.issubset(fdf.columns):
    trend_ret = (
        fdf.groupby("year", as_index=False)["retention_rate"]
           .mean()
           .sort_values("year")
    )
    fig_ret = px.line(
        trend_ret, x="year", y="retention_rate",
        markers=True, title="Retention Rate (%) — Trend Over Time"
    )
    fig_ret.update_yaxes(range=[0, 100])
    st.plotly_chart(fig_ret, use_container_width=True)

if {"year", "student_satisfaction"}.issubset(fdf.columns):
    trend_sat = (
        fdf.groupby("year", as_index=False)["student_satisfaction"]
           .mean()
           .sort_values("year")
    )
    fig_sat = px.bar(
        trend_sat, x="year", y="student_satisfaction",
        title="Average Student Satisfaction (%) by Year", text_auto=True
    )
    fig_sat.update_yaxes(range=[0, 100])
    st.plotly_chart(fig_sat, use_container_width=True)

if {"term", "enrolled"}.issubset(fdf.columns):
    term_grp = (
        fdf.groupby("term", as_index=False)["enrolled"]
           .sum()
           .sort_values("enrolled", ascending=False)
    )
    c1, c2 = st.columns(2)

    with c1:
        fig_term_bar = px.bar(
            term_grp, x="term", y="enrolled",
            title="Enrollment by Term", text_auto=True
        )
        st.plotly_chart(fig_term_bar, use_container_width=True)

    with c2:
        fig_term_pie = px.pie(
            term_grp, names="term", values="enrolled",
            title="Term Distribution (Enrollment Share)"
        )
        st.plotly_chart(fig_term_pie, use_container_width=True)

faculty_cols = [
    "engineering_enrolled",
    "business_enrolled",
    "arts_enrolled",
    "science_enrolled"
]
existing_fac = [c for c in faculty_cols if c in fdf.columns]

if len(existing_fac) > 0:
    st.markdown("### Enrollment by Area (Engineering / Business / Arts / Science)")
    fac_totals = fdf[existing_fac].sum().reset_index()
    fac_totals.columns = ["area", "enrolled"]
    fac_totals["area"] = fac_totals["area"].str.replace("_enrolled", "", regex=False).str.title()

    fig_fac = px.bar(
        fac_totals, x="area", y="enrolled",
        title="Enrollment by Academic Area (filtered)", text_auto=True
    )
    st.plotly_chart(fig_fac, use_container_width=True)

st.caption("Data Mining — Universidad de la Costa • Dashboard by Juan Bolívar")

from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import cv_match, skill_cooccurrence
from src.cv import extract_cv_text
from src.database import bootstrap_demo, connect, initialize, load_frame
from src.importers import read_csv, template
from src.nlp import extract_skills
from src.settings import DB_PATH, DEMO_DATA_PATH

st.set_page_config(
    page_title="Boussole — Tunisia Job Intelligence",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = ["#16C79A", "#F2B84B", "#7C6CF6", "#FF6B6B", "#2F80ED", "#71D7C2"]


def inject_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root { --ink:#17212B; --muted:#667085; --cream:#F5F3EC; --card:#FFFFFF; --green:#16C79A; }
    .stApp { background: radial-gradient(circle at 85% 0%, #DFF7EF 0, transparent 26rem), var(--cream); color:var(--ink); }
    html, body, [class*="css"] { font-family:'DM Sans', sans-serif; }
    h1,h2,h3 { font-family:'Manrope', sans-serif !important; letter-spacing:-.035em; }
    [data-testid="stSidebar"] { background:#13252A; border-right:0; }
    [data-testid="stSidebar"] * { color:#F8FAF9 !important; }
    [data-testid="stSidebar"] [data-baseweb="select"] * { color:#17212B !important; }
    .hero { padding:1.5rem 1.6rem; border-radius:24px; background:linear-gradient(125deg,#142E33,#1A4748); color:white; margin-bottom:1rem; position:relative; overflow:hidden; box-shadow:0 18px 50px rgba(20,46,51,.12); }
    .hero:after { content:''; position:absolute; width:180px;height:180px;border:35px solid rgba(22,199,154,.18);border-radius:50%;right:-40px;top:-65px; }
    .eyebrow { font:700 .72rem 'Manrope'; letter-spacing:.14em; text-transform:uppercase; color:#78E2C4; }
    .hero h1 { margin:.3rem 0 .25rem; font-size:2.15rem; color:#fff; }
    .hero p { margin:0; color:#CBE1DC; max-width:760px; }
    [data-testid="stMetric"] { background:rgba(255,255,255,.88); border:1px solid rgba(23,33,43,.07); padding:1rem 1.1rem; border-radius:18px; box-shadow:0 8px 30px rgba(23,33,43,.05); }
    [data-testid="stMetricValue"] { font-family:'Manrope'; color:#142E33; }
    [data-testid="stPlotlyChart"], [data-testid="stDataFrame"] { background:white; border:1px solid rgba(23,33,43,.07); border-radius:18px; padding:.35rem; box-shadow:0 8px 30px rgba(23,33,43,.04); }
    .section-note { color:#667085; font-size:.91rem; margin-top:-.55rem; margin-bottom:1rem; }
    .pill { display:inline-block; background:#DFF7EF;color:#08795C;border-radius:999px;padding:.28rem .65rem;margin:.15rem;font-size:.78rem;font-weight:700; }
    .demo-banner { border-left:4px solid #F2B84B; background:#FFF8E8; padding:.75rem 1rem; border-radius:10px; color:#6B4C05; margin:.5rem 0 1rem; }
    .match-card { background:white; border-radius:16px; padding:1rem; border:1px solid #E8E7E1; margin:.4rem 0; }
    .stButton>button, .stDownloadButton>button { border-radius:12px; font-weight:700; }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def get_connection():
    con = connect(DB_PATH)
    initialize(con)
    bootstrap_demo(con, DEMO_DATA_PATH)
    return con


@st.cache_data(ttl=60)
def load_data(_version: int = 0) -> tuple[pd.DataFrame, pd.DataFrame]:
    con = get_connection()
    jobs = con.execute("SELECT * FROM jobs ORDER BY posted_date DESC").df()
    skills = con.execute("SELECT * FROM job_skills").df()
    jobs["posted_date"] = pd.to_datetime(jobs["posted_date"])
    jobs["month"] = jobs["posted_date"].dt.to_period("M").astype(str)
    jobs["languages"] = jobs["language_requirements"].apply(
        lambda value: json.loads(value) if isinstance(value, str) else []
    )
    return jobs, skills


def style_chart(fig, height: int = 390):
    fig.update_layout(
        height=height, margin=dict(l=15, r=15, t=45, b=15), paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="DM Sans", color="#344054"),
        title_font=dict(family="Manrope", size=17, color="#17212B"),
        legend_title_text="", hoverlabel=dict(bgcolor="#142E33", font_color="white"),
    )
    fig.update_xaxes(gridcolor="#ECEBE6", zeroline=False)
    fig.update_yaxes(gridcolor="#ECEBE6", zeroline=False)
    return fig


def hero(title: str, subtitle: str, eyebrow: str) -> None:
    st.markdown(
        f'<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


inject_css()
con = get_connection()
jobs, all_skills = load_data()

with st.sidebar:
    st.markdown("## 🧭 Boussole")
    st.caption("Tunisia Job-Market Intelligence")
    page = st.radio(
        "Explore",
        ["Market pulse", "Skills radar", "People & pay", "Demand trends", "CV match", "Data studio"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("##### Filters")
    locations = st.multiselect("Location", sorted(jobs.location.dropna().unique()))
    industries = st.multiselect("Industry", sorted(jobs.industry.dropna().unique()))
    levels = st.multiselect("Experience", sorted(jobs.experience_level.dropna().unique()))
    dates = st.date_input(
        "Posted between", value=(jobs.posted_date.min().date(), jobs.posted_date.max().date()),
        min_value=jobs.posted_date.min().date(), max_value=jobs.posted_date.max().date(),
    )
    st.markdown("---")
    st.caption(f"Warehouse · {len(jobs):,} listings")
    st.caption(f"Refreshed · {pd.Timestamp.now():%d %b %Y}")

filtered = jobs.copy()
if locations:
    filtered = filtered[filtered.location.isin(locations)]
if industries:
    filtered = filtered[filtered.industry.isin(industries)]
if levels:
    filtered = filtered[filtered.experience_level.isin(levels)]
if isinstance(dates, tuple) and len(dates) == 2:
    filtered = filtered[filtered.posted_date.dt.date.between(dates[0], dates[1])]
skills = all_skills[all_skills.job_id.isin(filtered.job_id)]

if filtered.get("is_demo", pd.Series(dtype=bool)).any():
    demo_notice = '<div class="demo-banner">Portfolio demo mode · figures use a clearly labelled synthetic dataset. Import permitted real listings in Data studio.</div>'
else:
    demo_notice = ""

if page == "Market pulse":
    hero("See where Tunisia’s job market is moving.", "A decision-ready view of employer demand across skills, sectors, regions and seniority.", "Market pulse")
    st.markdown(demo_notice, unsafe_allow_html=True)
    salary = filtered[["salary_min_tnd", "salary_max_tnd"]].mean(axis=1).dropna()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Active listings", f"{len(filtered):,}", f"{filtered.company.nunique()} employers")
    k2.metric("Skills tracked", f"{skills.skill.nunique():,}", "auditable taxonomy")
    k3.metric("Entry-level share", f"{(filtered.experience_level.eq('Entry-level').mean() * 100):.0f}%")
    k4.metric("Median disclosed pay", f"{salary.median():,.0f} TND" if len(salary) else "Not enough data")

    c1, c2 = st.columns([1.15, .85])
    with c1:
        loc = filtered.groupby("location").size().reset_index(name="listings").sort_values("listings")
        fig = px.bar(loc, x="listings", y="location", orientation="h", color="listings", color_continuous_scale=["#DFF7EF", "#16C79A", "#08795C"], title="Opportunity by location")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_chart(fig), use_container_width=True)
    with c2:
        ind = filtered.groupby("industry").size().reset_index(name="listings").sort_values("listings", ascending=False)
        fig = px.treemap(ind, path=["industry"], values="listings", color="listings", color_continuous_scale=["#E7E4FF", "#7C6CF6"])
        fig.update_layout(title="Industry mix", coloraxis_showscale=False)
        st.plotly_chart(style_chart(fig), use_container_width=True)

    st.subheader("Latest opportunities")
    st.markdown('<p class="section-note">Filter the market using the controls on the left.</p>', unsafe_allow_html=True)
    st.dataframe(filtered[["posted_date", "title", "company", "location", "industry", "experience_level"]], hide_index=True, use_container_width=True)

elif page == "Skills radar":
    hero("Decode the skills behind every role.", "Find the technologies employers mention most—and the combinations that turn isolated tools into marketable profiles.", "Skills intelligence")
    st.markdown(demo_notice, unsafe_allow_html=True)
    counts = skills.groupby(["display_skill", "category"]).size().reset_index(name="listings").sort_values("listings", ascending=False)
    c1, c2 = st.columns([1.1, .9])
    with c1:
        top = counts.head(15).sort_values("listings")
        fig = px.bar(top, x="listings", y="display_skill", orientation="h", color="category", color_discrete_sequence=COLORS, title="Most requested skills")
        st.plotly_chart(style_chart(fig, 470), use_container_width=True)
    with c2:
        category = skills.groupby("category").size().reset_index(name="mentions")
        fig = px.sunburst(category, path=["category"], values="mentions", color="category", color_discrete_sequence=COLORS, title="Skill family share")
        st.plotly_chart(style_chart(fig, 470), use_container_width=True)

    st.subheader("Skills travel in packs")
    st.markdown('<p class="section-note">Each pair counts once per listing, revealing practical learning paths such as Python + SQL + Power BI.</p>', unsafe_allow_html=True)
    pairs = skill_cooccurrence(skills)
    if not pairs.empty:
        pair_view = pairs.head(18).copy()
        pair_view["pair"] = pair_view.skill_a + "  +  " + pair_view.skill_b
        fig = px.bar(pair_view.sort_values("jobs"), x="jobs", y="pair", orientation="h", color="jobs", color_continuous_scale=["#FFF0C7", "#F2B84B", "#E48124"], title="Top co-occurring skill pairs")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_chart(fig, 520), use_container_width=True)

elif page == "People & pay":
    hero("Understand who employers are hiring.", "Compare seniority, language expectations and disclosed compensation without hiding missing-data limitations.", "People & pay")
    st.markdown(demo_notice, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        exp = filtered.groupby("experience_level").size().reset_index(name="listings")
        fig = px.pie(exp, names="experience_level", values="listings", hole=.62, color_discrete_sequence=COLORS, title="Experience level")
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(style_chart(fig), use_container_width=True)
    with c2:
        lang_rows = [{"language": lang, "job_id": row.job_id} for row in filtered.itertuples() for lang in row.languages]
        lang = pd.DataFrame(lang_rows)
        if not lang.empty:
            lang = lang.groupby("language").size().reset_index(name="listings")
            fig = px.bar(lang, x="language", y="listings", color="language", color_discrete_sequence=COLORS, title="Explicit language requirements")
            st.plotly_chart(style_chart(fig), use_container_width=True)

    salary_jobs = filtered.dropna(subset=["salary_min_tnd", "salary_max_tnd"]).copy()
    salary_jobs["salary_mid"] = salary_jobs[["salary_min_tnd", "salary_max_tnd"]].mean(axis=1)
    coverage = len(salary_jobs) / len(filtered) if len(filtered) else 0
    st.subheader("Salary signals")
    st.markdown(f'<p class="section-note">Coverage: {coverage:.0%} of filtered listings disclose usable pay. Interpret medians with care.</p>', unsafe_allow_html=True)
    if len(salary_jobs):
        fig = px.box(salary_jobs, x="experience_level", y="salary_mid", color="experience_level", points="all", color_discrete_sequence=COLORS, title="Monthly salary midpoint by experience (TND)", hover_data=["title", "company"])
        st.plotly_chart(style_chart(fig, 450), use_container_width=True)
    else:
        st.info("No salary data is available for the current filters.")

elif page == "Demand trends":
    hero("Separate momentum from noise.", "Track monthly shifts in listings and skill mentions, with honest sample-size context.", "Demand over time")
    st.markdown(demo_notice, unsafe_allow_html=True)
    monthly = filtered.groupby("month").size().reset_index(name="listings")
    fig = px.area(monthly, x="month", y="listings", markers=True, color_discrete_sequence=["#16C79A"], title="Monthly employer demand")
    fig.update_traces(fillcolor="rgba(22,199,154,.17)", line_width=3)
    st.plotly_chart(style_chart(fig), use_container_width=True)

    options = skills.groupby("display_skill").size().sort_values(ascending=False).head(12).index.tolist()
    selected = st.multiselect("Compare skills", options, default=options[:5], max_selections=6)
    trend = skills.merge(filtered[["job_id", "month"]], on="job_id")
    trend = trend[trend.display_skill.isin(selected)].groupby(["month", "display_skill"]).job_id.nunique().reset_index(name="listings")
    if not trend.empty:
        fig = px.line(trend, x="month", y="listings", color="display_skill", markers=True, color_discrete_sequence=COLORS, title="Skill demand trajectory")
        fig.update_traces(line_width=3)
        st.plotly_chart(style_chart(fig, 460), use_container_width=True)

elif page == "CV match":
    hero("Turn your CV into a learning roadmap.", "Compare your current toolkit with market demand. Your file is processed locally in this app session and is not stored.", "Skill-gap studio")
    left, right = st.columns([.72, 1.28])
    with left:
        upload = st.file_uploader("Upload CV", type=["pdf", "docx", "txt"])
        pasted = st.text_area("Or paste CV text", height=220, placeholder="Paste your skills and experience here…")
        cv_text = extract_cv_text(upload) if upload else pasted
        if cv_text:
            detected = extract_skills(cv_text)
            st.markdown("##### Skills detected")
            st.markdown("".join(f'<span class="pill">{s["display_skill"]}</span>' for s in detected) or "No taxonomy matches yet.", unsafe_allow_html=True)
    with right:
        if cv_text:
            matches = cv_match(cv_text, filtered, skills, extract_skills)
            top = matches.head(12)
            fig = px.bar(top.sort_values("match_score"), x="match_score", y="title", orientation="h", color="match_score", color_continuous_scale=["#FFE8E8", "#F2B84B", "#16C79A"], range_x=[0, 100], title="Best-fit roles")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(style_chart(fig, 430), use_container_width=True)
            choice = st.selectbox("Inspect a role", top.index, format_func=lambda i: f"{top.loc[i, 'match_score']}% · {top.loc[i, 'title']} — {top.loc[i, 'company']}")
            row = top.loc[choice]
            st.markdown(
                f'<div class="match-card"><b>Matched</b><br>{row.matched}'
                f'<br><br><b>Skills to build</b><br>{row.missing}'
                f'<br><br><small>TF-IDF text similarity: {row.text_similarity:.1f}% '
                f'· used only to break skill-score ties</small></div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("Upload or paste a CV to calculate matches and missing skills.")

elif page == "Data studio":
    hero("Keep the evidence fresh.", "Load permitted datasets, audit coverage, and export analysis-ready data from one controlled workspace.", "Data operations")
    t1, t2, t3 = st.tabs(["Import CSV", "Quality audit", "Exports"])
    with t1:
        st.markdown("### Add manually collected or licensed listings")
        st.write("Use one row per listing. Imports are deduplicated by source URL, title and company; the original source remains traceable.")
        st.download_button("Download CSV template", template().to_csv(index=False).encode(), "job_import_template.csv", "text/csv")
        incoming = st.file_uploader("Choose completed CSV", type="csv", key="import")
        permission = st.checkbox("I confirm I am permitted to use this dataset and it contains no candidate personal data.")
        if st.button("Validate and import", type="primary", disabled=not (incoming and permission)):
            try:
                frame = read_csv(incoming)
                loaded = load_frame(con, frame)
                load_data.clear()
                st.success(f"Imported {loaded} listings. Refresh the page to see the updated dashboard.")
            except Exception as exc:
                st.error(f"Import could not be completed: {exc}")
        st.caption("Automated JSON-LD collection is available through the command-line workflow after reviewing the source’s terms and robots.txt.")
    with t2:
        a, b, c, d = st.columns(4)
        a.metric("Listings", len(jobs))
        b.metric("Unique URLs", jobs.source_url.nunique())
        c.metric("Salary coverage", f"{jobs.salary_min_tnd.notna().mean():.0%}")
        d.metric("Unclassified industry", f"{jobs.industry.eq('Autre').mean():.0%}")
        quality = pd.DataFrame({
            "check": ["Missing company", "Missing description", "Missing location", "No extracted skills", "Demo records"],
            "records": [jobs.company.isna().sum(), jobs.description.fillna('').eq('').sum(), jobs.location.isna().sum(), len(set(jobs.job_id)-set(all_skills.job_id)), jobs.is_demo.sum()],
        })
        st.dataframe(quality, hide_index=True, use_container_width=True)
    with t3:
        export = filtered.merge(
            skills.groupby("job_id").display_skill.apply(lambda x: ", ".join(sorted(x))).rename("skills"),
            on="job_id", how="left",
        )
        st.download_button("Export filtered listings", export.to_csv(index=False).encode(), "tunisia_job_market_export.csv", "text/csv", type="primary")
        st.dataframe(export[["posted_date", "title", "company", "location", "industry", "experience_level", "skills"]], hide_index=True, use_container_width=True)

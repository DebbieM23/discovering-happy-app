"""
Discovering Happy & Integrated Flourishing Index (v5)
------------------------------------------------------
An interactive web application prototype built with Streamlit.
Integrates four global well-being and flourishing frameworks into a single community dashboard:
1. WHR Evaluative & Affective Baseline (Gallup / WHR 2026)
2. UNDP HDI & Ontological Domain Workability
3. ESS Social Foundations & Digital Balance (European Social Survey Rounds 8–11)
4. Secular-Buddhist & First Nations Relational Interbeing

Features in v5:
- European (Western Europe, Nordic, CEE) & NANZ / Canadian Benchmarks
- All-Ages Cohort Selectors (Gen Z, Millennials, Gen X, Baby Boomers)
- NANZ Youth Decline (-0.86 pts) & CEE Convergence Insights
- Custom Thresholds & Weights for Index Calibration
- Data Export & Field Logging (CSV download)
- Enhanced Visual Analytics & Benchmark Grouping

Run locally via:
    streamlit run discovering_happy_app-v5.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Discovering Happy | Integrated Flourishing Index v5",
    page_icon="✨",
    layout="wide"
)

st.title("✨ Discovering Happy & Integrated Flourishing Index (v5)")
st.caption("A multi-paradigm community inquiry dashboard integrating global research (WHR 2026, Gallup, UNDP, ESS) with Secular-Buddhist and First Nations relational frameworks.")

# Initialize session state for logs if not existing
if 'logs' not in st.session_state:
    st.session_state['logs'] = pd.DataFrame(columns=[
        "Timestamp", "User", "Cohort", "Region_Focus", "WHR_Score", "UNDP_Score", "ESS_Score", "Relational_Score",
        "Weighted_Index", "Expression_Ratio", "Inquiry_Focus", "Reflection_Note"
    ])

# ---------------------------------------------------------
# Sidebar - User Demographic, Regional & Module Calibration
# ---------------------------------------------------------
st.sidebar.header("📋 User Profile & Calibration")
user_name = st.sidebar.text_input("Your Name / Identifier", "Community Member")

# All Ages Cohort Selection
age_cohort = st.sidebar.selectbox(
    "👥 Age Cohort / Generation",
    [
        "Gen Z / Youth (Ages 15–24)",
        "Millennials (Ages 25–39)",
        "Gen X (Ages 40–59)",
        "Baby Boomers / Older Adults (Ages 60+)"
    ],
    index=0
)

# Regional Reference Focus
region_focus = st.sidebar.selectbox(
    "🌍 Primary Regional Reference Benchmark",
    [
        "NANZ (Canada, US, Australia, NZ)",
        "Canada Focus (WHR 2026)",
        "Western Europe & Nordic Countries",
        "Central & Eastern Europe (CEE)",
        "Global Weighted Average"
    ],
    index=0
)

# Custom Weights Adjustment
with st.sidebar.expander("⚙️ Module Weights Calibration", expanded=False):
    st.caption("Adjust the relative weight of each module in your Integrated Flourishing Index (Total auto-normalizes to 100%).")
    w1 = st.slider("1. WHR Evaluative Weight", 0, 100, 25, 5)
    w2 = st.slider("2. UNDP Capability Weight", 0, 100, 25, 5)
    w3 = st.slider("3. ESS Social Trust Weight", 0, 100, 25, 5)
    w4 = st.slider("4. Relational Interbeing Weight", 0, 100, 25, 5)

    total_w = w1 + w2 + w3 + w4
    if total_w == 0:
        norm_w1, norm_w2, norm_w3, norm_w4 = 0.25, 0.25, 0.25, 0.25
    else:
        norm_w1, norm_w2, norm_w3, norm_w4 = w1/total_w, w2/total_w, w3/total_w, w4/total_w

# Module 1: WHR
with st.sidebar.expander("1. WHR: Life Evaluation & Affect", expanded=True):
    cantril_score = st.slider("Cantril Ladder (0–10)", 0.0, 10.0, 7.5, 0.5,
                              help="0 = Worst possible life, 10 = Best possible life you could create.")
    pos_affect = st.slider("Positive Affect (0–10)", 0.0, 10.0, 7.0, 0.5,
                           help="Laughter, joy, play, interest, spontaneous delight yesterday.")
    neg_affect = st.slider("Negative Affect / Friction (0–10)", 0.0, 10.0, 3.0, 0.5,
                           help="Worry, sadness, anger, friction experienced yesterday.")

# Module 2: UNDP & Ontological
with st.sidebar.expander("2. UNDP & Workability Scope", expanded=False):
    st.markdown("**Domain Capabilities (0–10)**")
    rel_score = st.slider("Relationships & Kinship", 0, 10, 8)
    voc_score = st.slider("Vocation & Business Expression", 0, 10, 7)
    inner_score = st.slider("Inner Peace & Mind-State", 0, 10, 8)
    comm_score = st.slider("Community Contribution", 0, 10, 9)
    
    st.markdown("**Expression Mode (Default vs. Created)**")
    rel_mode = st.radio("Relationships Mode", ["Default Routine", "Created Commitment"], index=1)
    voc_mode = st.radio("Vocation Mode", ["Default Routine", "Created Commitment"], index=1)
    inner_mode = st.radio("Inner Peace Mode", ["Default Routine", "Created Commitment"], index=1)
    comm_mode = st.radio("Community Mode", ["Default Routine", "Created Commitment"], index=1)

# Module 3: ESS Social Foundations
with st.sidebar.expander("3. ESS: Trust & Digital Balance", expanded=False):
    trust_score = st.slider("Interpersonal & Institutional Trust (0–10)", 0.0, 10.0, 7.0, 0.5,
                            help="Degree of trust in people and community institutions.")
    belonging_score = st.slider("Community Belonging & Safety (0–10)", 0.0, 10.0, 8.0, 0.5)
    digital_balance = st.slider("Digital Ratio (% Active Connection vs. Algorithmic Feed)", 0, 100, 70,
                                help="0% = Pure passive scrolling, 100% = Pure active connection & learning.")

# Module 4: Relational & Mind-Training
with st.sidebar.expander("4. Relational & Mind-Training", expanded=False):
    karuna_score = st.slider("Warm-Heartedness & Compassion (0–10)", 0.0, 10.0, 8.5, 0.5,
                             help="Secular-Buddhist altruism and active care for others.")
    reciprocity_score = st.slider("Communal Reciprocity (0–10)", 0.0, 10.0, 8.0, 0.5,
                                  help="First Nations practice of resource sharing and mutual support.")
    place_score = st.slider("Connection to Place & Custodianship (0–10)", 0.0, 10.0, 7.5, 0.5)

# ---------------------------------------------------------
# Calculations & Weighted Metrics
# ---------------------------------------------------------
net_affect = max(0.0, min(10.0, (pos_affect - neg_affect + 10) / 2))
domain_avg = np.mean([rel_score, voc_score, inner_score, comm_score])

modes = [rel_mode, voc_mode, inner_mode, comm_mode]
created_count = sum(1 for m in modes if m == "Created Commitment")
expression_ratio = (created_count / 4.0) * 100

social_foundations_avg = np.mean([trust_score, belonging_score, digital_balance / 10.0])
relational_interbeing_avg = np.mean([karuna_score, reciprocity_score, place_score])

# Weighted Integrated Flourishing Index
integrated_flourishing_index = (
    (cantril_score * norm_w1) +
    (domain_avg * norm_w2) +
    (social_foundations_avg * norm_w3) +
    (relational_interbeing_avg * norm_w4)
)

# ---------------------------------------------------------
# Top KPI Cards
# ---------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Weighted Flourishing Index", f"{integrated_flourishing_index:.1f} / 10",
              delta=f"{integrated_flourishing_index - 5.0:+.1f} vs Baseline")
with kpi2:
    st.metric("WHR Cantril Ladder", f"{cantril_score:.1f} / 10")
with kpi3:
    st.metric("Expression Ratio", f"{expression_ratio:.0f}%",
              delta=f"{created_count} of 4 Created Domains")
with kpi4:
    st.metric("Relational & Trust Index", f"{(social_foundations_avg + relational_interbeing_avg)/2:.1f} / 10")

st.divider()

# ---------------------------------------------------------
# Main Module Dashboard Tabs
# ---------------------------------------------------------
tab_summary, tab1, tab2, tab3, tab4, tab_benchmarks, tab_analytics = st.tabs([
    "📊 Summary Matrix",
    "1. WHR Evaluative",
    "2. UNDP Workability",
    "3. ESS Social & Digital",
    "4. Relational Interbeing",
    "🌍 European, NANZ & All-Ages Benchmarks",
    "📈 Analytics & Field Logger"
])

# Summary Matrix Tab
with tab_summary:
    st.subheader("Summary Matrix: Integrated Flourishing Framework")
    st.caption("A multi-layered synthesis aligning subjective well-being data with ontological capability and wisdom ontologies.")
    
    summary_data = [
        {"Layer / Dimension": "1. Evaluative Life Score", "Core Metric & Question": f"Cantril Ladder: {cantril_score:.1f}/10 | Net Affect: {net_affect:.1f}/10", "Underlying Philosophy": "World Happiness Report / Gallup", "Weight": f"{norm_w1*100:.0f}%"},
        {"Layer / Dimension": "2. Workability & Expression", "Core Metric & Question": f"Domain Avg: {domain_avg:.1f}/10 | Created Ratio: {expression_ratio:.0f}%", "Underlying Philosophy": "UNDP HDI & Ontological Inquiry", "Weight": f"{norm_w2*100:.0f}%"},
        {"Layer / Dimension": "3. Social Foundations", "Core Metric & Question": f"Trust & Belonging: {social_foundations_avg:.1f}/10 | Active Digital: {digital_balance}%", "Underlying Philosophy": "European Social Survey (ESS)", "Weight": f"{norm_w3*100:.0f}%"},
        {"Layer / Dimension": "4. Relational Reciprocity", "Core Metric & Question": f"Warm-Heartedness & Reciprocity: {relational_interbeing_avg:.1f}/10", "Underlying Philosophy": "Secular-Buddhist & First Nations Ontologies", "Weight": f"{norm_w4*100:.0f}%"}
    ]
    st.table(pd.DataFrame(summary_data))
    
    col_sum1, col_sum2 = st.columns(2)
    with col_sum1:
        pillar_df = pd.DataFrame({
            "Layer": ["1. WHR Evaluative", "2. UNDP Workability", "3. ESS Social Trust", "4. Relational Interbeing"],
            "Score": [cantril_score, domain_avg, social_foundations_avg, relational_interbeing_avg],
            "Weight (%)": [norm_w1*100, norm_w2*100, norm_w3*100, norm_w4*100]
        })
        fig_summary_bar = px.bar(pillar_df, x="Layer", y="Score", color="Layer",
                                 color_discrete_sequence=["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b"],
                                 title="Layer Score Profile", range_y=[0, 10], text="Score")
        fig_summary_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_summary_bar.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_summary_bar, use_container_width=True)
        
    with col_sum2:
        fig_weight_pie = px.pie(pillar_df, names="Layer", values="Weight (%)",
                                color="Layer", color_discrete_sequence=["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b"],
                                title="Custom Calibrated Weights Breakdown", hole=0.4)
        fig_weight_pie.update_layout(height=350)
        st.plotly_chart(fig_weight_pie, use_container_width=True)

# Tab 1: WHR Evaluative Matrix
with tab1:
    st.subheader("Module 1: WHR Evaluative & Affective Baseline")
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        if cantril_score >= 5.0 and net_affect >= 5.0:
            quadrant = "🌟 Joyful Expression"
            desc = "High evaluative life score paired with positive daily affective balance."
        elif cantril_score >= 5.0 and net_affect < 5.0:
            quadrant = "🧘 Quiet Contentment"
            desc = "Solid life evaluation, but daily affect is weighed down by friction or worry."
        elif cantril_score < 5.0 and net_affect >= 5.0:
            quadrant = "⚡ Growth / Active Drive"
            desc = "Positive daily emotional drive while navigating structural challenges."
        else:
            quadrant = "🌊 Adrift / Default"
            desc = "Experiencing both low life evaluation and daily friction. Opportunity to reset commitment."
            
        st.info(f"**State:** {quadrant}\n\n_{desc}_")
        
        fig_matrix = go.Figure()
        fig_matrix.add_shape(type="rect", x0=0, y0=5, x1=5, y1=10, fillcolor="#e0f2fe", opacity=0.4, layer="below")
        fig_matrix.add_shape(type="rect", x0=5, y0=5, x1=10, y1=10, fillcolor="#dcfce7", opacity=0.5, layer="below")
        fig_matrix.add_shape(type="rect", x0=0, y0=0, x1=5, y1=5, fillcolor="#fef3c7", opacity=0.4, layer="below")
        fig_matrix.add_shape(type="rect", x0=5, y0=0, x1=10, y1=5, fillcolor="#fae8ff", opacity=0.4, layer="below")
        
        fig_matrix.add_trace(go.Scatter(
            x=[cantril_score],
            y=[net_affect],
            mode="markers+text",
            marker=dict(size=18, color="#059669", line=dict(width=2, color="DarkSlateGrey")),
            text=[f"{user_name} ({age_cohort.split()[0]})"],
            textposition="top center"
        ))
        
        fig_matrix.update_layout(
            title="Cantril Ladder vs. Net Affect Balance",
            xaxis=dict(title="Evaluative Score (Cantril Ladder 0–10)", range=[0, 10]),
            yaxis=dict(title="Net Daily Affect Balance (0–10)", range=[0, 10]),
            height=380,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_matrix, use_container_width=True)
        
    with col_b:
        st.markdown("### Daily Affect Breakdown")
        affect_df = pd.DataFrame({
            "Metric": ["Positive Affect (Joy/Play)", "Negative Affect (Worry/Friction)", "Net Affect Balance"],
            "Score": [pos_affect, neg_affect, net_affect]
        })
        fig_affect = px.bar(affect_df, x="Metric", y="Score", color="Metric",
                            color_discrete_sequence=["#10b981", "#ef4444", "#3b82f6"],
                            text="Score", range_y=[0, 10], title="Affective Emotional Profile")
        fig_affect.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_affect.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig_affect, use_container_width=True)

# Tab 2: UNDP Workability Scope
with tab2:
    st.subheader("Module 2: UNDP Capability & Ontological Workability Scope")
    col_c, col_d = st.columns([1, 1])
    
    with col_c:
        domains = ["Relationships", "Vocation", "Inner Peace", "Community"]
        scores = [rel_score, voc_score, inner_score, comm_score]
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=scores + [scores[0]],
            theta=domains + [domains[0]],
            fill='toself',
            fillcolor='rgba(59, 130, 246, 0.3)',
            line=dict(color='#3b82f6', width=3)
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=False,
            height=380,
            title="4-Domain Capability Radar"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col_d:
        st.markdown("### Expression Modes Breakdown")
        mode_df = pd.DataFrame({
            "Domain": domains,
            "Capability Score": scores,
            "Mode": modes
        })
        fig_modes = px.bar(mode_df, x="Domain", y="Capability Score", color="Mode",
                           color_discrete_map={"Default Routine": "#f59e0b", "Created Commitment": "#10b981"},
                           title="Domain Score by Expression Mode", text="Capability Score")
        fig_modes.update_layout(height=380, yaxis=dict(range=[0, 10]))
        st.plotly_chart(fig_modes, use_container_width=True)

# Tab 3: ESS Social & Digital Audit
with tab3:
    st.subheader("Module 3: ESS Social Foundations & Digital Balance")
    col_e, col_f = st.columns([1, 1])
    
    with col_e:
        st.markdown("### Trust & Belonging Metrics")
        trust_df = pd.DataFrame({
            "Indicator": ["Interpersonal Trust", "Community Belonging", "Digital Connection Ratio"],
            "Score": [trust_score, belonging_score, digital_balance / 10.0]
        })
        fig_trust = px.bar(trust_df, x="Indicator", y="Score", color="Indicator",
                           color_discrete_sequence=["#8b5cf6", "#ec4899", "#06b6d4"],
                           title="Social Trust & Safety Scorecard", range_y=[0, 10], text="Score")
        fig_trust.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_trust.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig_trust, use_container_width=True)
        
    with col_f:
        st.markdown("### Digital Environment Impact")
        if digital_balance >= 60:
            st.success(f"**Active Connection Dominant ({digital_balance}% Active)**\n\nDirect communication and active learning habit.")
        elif digital_balance >= 40:
            st.warning(f"**Balanced Digital Exposure ({digital_balance}% Active)**\n\nModerate exposure to passive social media feeds.")
        else:
            st.error(f"**Algorithmic Feed Dominant ({digital_balance}% Active)**\n\nHigh passive feed scrolling. Research indicates increased risk of social comparison & worry.")
            
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=digital_balance,
            title={'text': "Active Connection Ratio (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#06b6d4"},
                'steps': [
                    {'range': [0, 40], 'color': "#fee2e2"},
                    {'range': [40, 60], 'color': "#fef3c7"},
                    {'range': [60, 100], 'color': "#d1fae5"}
                ]
            }
        ))
        fig_gauge.update_layout(height=260)
        st.plotly_chart(fig_gauge, use_container_width=True)

# Tab 4: Relational Interbeing
with tab4:
    st.subheader("Module 4: Relational Interbeing & Mind-Training Frameworks")
    col_g, col_h = st.columns([1, 1])
    
    with col_g:
        rel_df = pd.DataFrame({
            "Dimension": ["Warm-Heartedness (Karuṇā)", "Communal Reciprocity", "Place & Custodianship"],
            "Score": [karuna_score, reciprocity_score, place_score]
        })
        fig_rel = px.bar(rel_df, x="Dimension", y="Score", color="Dimension",
                         color_discrete_sequence=["#f59e0b", "#10b981", "#84cc16"],
                         title="Relational Flourishing Profile", range_y=[0, 10], text="Score")
        fig_rel.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_rel.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig_rel, use_container_width=True)
        
    with col_h:
        st.markdown("### Paradigm Insights")
        st.info(f"**Secular-Buddhist Mind-Training ({karuna_score}/10):** Practice of warm-heartedness (*karuṇā*) and universal responsibility.")
        st.success(f"**First Nations Relational Reciprocity ({reciprocity_score}/10):** Resource redistribution, kinship obligations, and honoring connection to *Country*.")

# Tab Benchmarks: European, NANZ & All-Ages
with tab_benchmarks:
    st.subheader("🌍 European, NANZ & All-Ages Regional Benchmarks (WHR & ESS Data)")
    st.caption("Grounding your inquiry in empirical national ratings from the World Happiness Report (2026), Gallup World Poll, and European Social Survey.")

    col_b1, col_b2 = st.columns([1, 1])
    
    with col_b1:
        st.markdown("### 1. Country & Regional Baseline Comparison")
        
        region_scores = {
            "Nordic Average (Finland #1, Iceland #2, Denmark #3)": 7.61,
            "Canada (WHR 2026 Rank #25)": 6.74,
            "New Zealand (WHR 2026 Rank #11)": 7.00,
            "Australia (WHR 2026 Rank #15)": 6.92,
            "United States (WHR 2026 Rank #23)": 6.82,
            "Western Europe Avg (excl UK/Ireland)": 7.10,
            "Central & Eastern Europe (CEE) Avg": 6.70,
            "Global Average (Gallup 140+ countries)": 5.50
        }
        
        bench_df = pd.DataFrame(list(region_scores.items()), columns=["Region / Nation", "Cantril Ladder Score"])
        bench_df = pd.concat([pd.DataFrame([{"Region / Nation": f"⭐ YOUR SCORE ({user_name})", "Cantril Ladder Score": cantril_score}]), bench_df], ignore_index=True)
        
        fig_regional = px.bar(bench_df, x="Cantril Ladder Score", y="Region / Nation", orientation="h",
                              color="Region / Nation",
                              color_discrete_map={f"⭐ YOUR SCORE ({user_name})": "#10b981"},
                              title="Cantril Ladder Score vs. Regional Benchmarks", text="Cantril Ladder Score")
        fig_regional.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_regional.update_layout(height=420, showlegend=False, xaxis=dict(range=[0, 10]))
        st.plotly_chart(fig_regional, use_container_width=True)

    with col_b2:
        st.markdown("### 2. Generational & Cohort Insights (All Ages)")
        
        if "Gen Z" in age_cohort:
            st.error("**Gen Z / Youth (15–24) Regional Divergence:**\n\n"
                     "- **NANZ & Canada Crisis**: Under-25 happiness in NANZ dropped by **0.86 points** over 15 years (Canada youth -1.14 pts, US -0.96 pts, NZ -0.72 pts, Australia -0.62 pts). NANZ is the *only* global region where young people are less happy than older adults.\n"
                     "- **CEE Growth Story**: In Central & Eastern Europe, Gen Z reports rising satisfaction (+1.0 point convergence), outpacing older generations.\n"
                     "- **ESS Trust Drop**: Gen Z females experienced the largest drop in interpersonal and system trust (-0.428 IV effect in ESS).")
        elif "Millennials" in age_cohort:
            st.warning("**Millennials (25–39) Structural Insights:**\n\n"
                       "- **Social Activity Comparison**: ESS Round 11 shows perceived social activity relative to peers dropped significantly post-2020 among Millennials.\n"
                       "- **Digital Exposure**: Moderate negative correlation with algorithmic feed overuse, mitigated by direct communication platforms.")
        elif "Gen X" in age_cohort:
            st.info("**Gen X (40–59) Workability Baseline:**\n\n"
                    "- **Mid-Life U-Curve**: Reflects stable evaluative satisfaction across Western Europe and NANZ.\n"
                    "- **Digital Balance**: Near-zero negative sensitivity to internet download speeds, showing higher resilience to feed saturation.")
        else:
            st.success("**Baby Boomers / Older Adults (60+) Resilience Profile:**\n\n"
                       "- **High Evaluative Anchor**: Highest overall life satisfaction in NANZ (7.2–7.5).\n"
                       "- **Strong Attachments**: Highest self-reported attachment to country and institutional trust, providing a buffer against loneliness.")

        st.divider()
        st.markdown("### 3. NANZ vs. Western Europe Youth Decline Breakdown")
        
        decline_df = pd.DataFrame({
            "Region": ["Canada & US", "Australia & NZ", "UK & Ireland", "Western Europe (excl UK)"],
            "Youth Life Eval Drop (Pts)": [-0.98, -0.65, -0.39, -0.30]
        })
        fig_decline = px.bar(decline_df, x="Region", y="Youth Life Eval Drop (Pts)", color="Region",
                             color_discrete_sequence=["#ef4444", "#f97316", "#eab308", "#3b82f6"],
                             title="15-Year Change in Youth Happiness (Under 25)", text="Youth Life Eval Drop (Pts)")
        fig_decline.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_decline.update_layout(height=280, showlegend=False, yaxis=dict(range=[-1.3, 0.2]))
        st.plotly_chart(fig_decline, use_container_width=True)

# Tab Analytics & Logger
with tab_analytics:
    st.subheader("📈 Cohort Benchmarks, Longitudinal Trends & Field Logger")
    
    st.markdown("### 1. Multi-Metric Benchmark Profile")
    
    if "NANZ" in region_focus or "Canada" in region_focus:
        ref_whr, ref_undp, ref_ess, ref_rel = 6.85, 7.20, 6.10, 6.50
        ref_label = "NANZ / Canadian Avg"
    elif "Western Europe" in region_focus:
        ref_whr, ref_undp, ref_ess, ref_rel = 7.10, 7.50, 6.80, 6.70
        ref_label = "Western Europe Avg"
    elif "Central" in region_focus:
        ref_whr, ref_undp, ref_ess, ref_rel = 6.70, 7.00, 5.80, 6.90
        ref_label = "CEE Avg"
    else:
        ref_whr, ref_undp, ref_ess, ref_rel = 5.50, 6.00, 5.20, 5.00
        ref_label = "Global Gallup Avg"

    benchmark_df = pd.DataFrame({
        "Metric": ["WHR Evaluative", "UNDP Capability", "ESS Social Trust", "Relational Care"],
        "Your Score": [cantril_score, domain_avg, social_foundations_avg, relational_interbeing_avg],
        ref_label: [ref_whr, ref_undp, ref_ess, ref_rel],
        "Target Benchmark": [8.2, 8.5, 8.0, 8.5]
    })
    
    fig_benchmark = go.Figure()
    fig_benchmark.add_trace(go.Bar(x=benchmark_df["Metric"], y=benchmark_df["Your Score"], name="Your Score", marker_color="#10b981"))
    fig_benchmark.add_trace(go.Bar(x=benchmark_df["Metric"], y=benchmark_df[ref_label], name=ref_label, marker_color="#cbd5e1"))
    fig_benchmark.add_trace(go.Bar(x=benchmark_df["Metric"], y=benchmark_df["Target Benchmark"], name="Target Benchmark", marker_color="#3b82f6"))
    
    fig_benchmark.update_layout(barmode='group', title=f"Your Scores vs. {ref_label} & High Flourishing Benchmark", height=350, yaxis=dict(range=[0, 10]))
    st.plotly_chart(fig_benchmark, use_container_width=True)
    
    st.divider()
    
    # Section B: Field Entry Logging
    st.markdown("### 2. Daily Field Discovery Logger & Export")
    col_log1, col_log2 = st.columns([1, 1])
    
    with col_log1:
        inquiry_q = st.selectbox(
            "Select Inquiry Focus:",
            [
                "Where did I move from 'adrift' to being 'at cause' today?",
                "What simple act of warm-heartedness or reciprocity did I share?",
                "Who did I inspire or enroll into a conversation about workability?",
                "What did I discover about my created happy today?"
            ]
        )
        user_discovery = st.text_area("Field Reflection Note:", placeholder="Type your observation or breakthrough...")
        
        if st.button("✨ Save & Log Entry"):
            new_entry = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "User": user_name,
                "Cohort": age_cohort,
                "Region_Focus": region_focus,
                "WHR_Score": round(cantril_score, 2),
                "UNDP_Score": round(domain_avg, 2),
                "ESS_Score": round(social_foundations_avg, 2),
                "Relational_Score": round(relational_interbeing_avg, 2),
                "Weighted_Index": round(integrated_flourishing_index, 2),
                "Expression_Ratio": f"{expression_ratio:.0f}%",
                "Inquiry_Focus": inquiry_q,
                "Reflection_Note": user_discovery
            }
            st.session_state['logs'] = pd.concat([st.session_state['logs'], pd.DataFrame([new_entry])], ignore_index=True)
            st.success("Entry successfully recorded into session field log!")

    with col_log2:
        st.markdown("### 3. Session Log Data & CSV Export")
        if not st.session_state['logs'].empty:
            st.dataframe(st.session_state['logs'][["Timestamp", "Cohort", "Weighted_Index", "Expression_Ratio", "Reflection_Note"]], height=180)
            
            csv_data = st.session_state['logs'].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Field Logs (CSV)",
                data=csv_data,
                file_name="discovering_happy_field_logs.csv",
                mime="text/csv"
            )
        else:
            st.info("No field entries logged in this session yet. Fill out the form on the left and click 'Save & Log Entry'.")

    # Section C: Longitudinal Trend Plot
    st.divider()
    st.markdown("### 4. Longitudinal Trend Tracker")
    if len(st.session_state['logs']) >= 2:
        fig_trend = px.line(st.session_state['logs'], x="Timestamp", y=["Weighted_Index", "WHR_Score", "UNDP_Score", "ESS_Score", "Relational_Score"],
                            markers=True, title="Flourishing Index Trajectory Over Session Entries")
        fig_trend.update_layout(height=350, yaxis=dict(range=[0, 10]))
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.caption("Log 2 or more entries during your session to unlock real-time longitudinal line chart tracking.")

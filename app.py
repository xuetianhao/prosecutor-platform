import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# 1. 页面配置
# =====================================================
st.set_page_config(
    page_title="检力资源业绩数智平台",
    page_icon="⚖️",
    layout="wide"
)

# =====================================================
# 2. 全局样式
# =====================================================
st.markdown("""
<style>
/* ===== 背景 ===== */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 20% 20%, #f2f6fb 0%, #e6edf6 90%);
}

/* ===== 侧边栏 ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #081f3f, #0a2d5a);
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * {
    color: rgba(235,242,255,0.9);
    font-size: 13px;
}

/* ===== 主业务卡片 ===== */
.glass-card {
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(14px);
    border-radius: 22px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.45);
    box-shadow: 0 14px 36px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}

/* 空卡片自动隐藏 */
.glass-card:empty {
    display: none;
}

/* ===== KPI ===== */
.kpi { text-align:center; padding:14px; }
.kpi-title { font-size:13px; color:#6b7a90; }
.kpi-value { font-size:32px; font-weight:700; color:#0a2d5a; }
.kpi-note  { font-size:12px; opacity:0.6; }

/* ===== 页面标题 ===== */
.page-title h1 { color:#0a2d5a; margin-bottom:6px; }
.page-title p  { color:#5b6b82; margin:0; }

/* ===== 能力条 ===== */
.ability-row { margin-bottom:14px; }
.ability-title {
    display:flex;
    justify-content:space-between;
    font-size:13px;
    color:#3a4a63;
}
.ability-bar-bg {
    height:10px;
    background:#e6ecf3;
    border-radius:6px;
    overflow:hidden;
}
.ability-bar {
    height:100%;
    background:linear-gradient(90deg,#003366,#0077cc);
}
.ability-tag {
    font-size:12px;
    padding:2px 8px;
    border-radius:10px;
    background:rgba(0,85,170,0.12);
    color:#0055aa;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. 数据
# =====================================================
@st.cache_data(ttl=600)
def load_data():
    df = pd.read_excel("prosecutors_data.xlsx")
    abilities = ["业务能力", "信调宣能力", "创新能力", "学习能力", "综合能力", "政治素养"]
    for c in abilities:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["综合得分"] = df[abilities].mean(axis=1).round(2)
    return df, abilities

df, categories = load_data()

def ability_level(score):
    if score >= 9: return "优秀"
    if score >= 7.5: return "良好"
    if score >= 6: return "合格"
    return "需提升"

# =====================================================
# 4. 侧边栏
# =====================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;margin-bottom:28px;">
        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="64">
        <h2 style="margin-top:12px;">检力资源数智平台</h2>
        <p style="opacity:0.7;">Procuratorial Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "功能导航",
        ["数字化驾驶舱", "人员精准画像", "统计决策分析", "系统管理"]
    )

    st.markdown("---")
    depts = st.multiselect("所属部门", df["部门"].unique(), default=df["部门"].unique())
    score_range = st.slider("综合得分", 0.0, 10.0, (0.0, 10.0))

f_df = df[df["部门"].isin(depts) & df["综合得分"].between(*score_range)]

# =====================================================
# 5. 页面标题
# =====================================================
st.markdown("""
<div class="glass-card page-title">
    <h1>检力资源科学管理与业绩数智平台</h1>
    <p>多维能力模型驱动的队伍结构分析与辅助决策支持</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# 6. 数字化驾驶舱
# =====================================================
if page == "数字化驾驶舱":

    # KPI 卡片
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    cols = st.columns(4)
    kpis = [
        ("干警总数", len(df), "纳入评价"),
        ("平均综合得分", f"{f_df['综合得分'].mean():.2f}", "能力均值"),
        ("部门覆盖", df["部门"].nunique(), "业务部门"),
        ("高创新人才", len(f_df[f_df["创新能力"] >= 9]), "创新 ≥ 9.0"),
    ]
    for col, (t, v, n) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-title">{t}</div>
                <div class="kpi-value">{v}</div>
                <div class="kpi-note">{n}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 图表区
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    left, right = st.columns([3, 2])

    with left:
        st.markdown("#### 部门能力结构分布")
        if not f_df.empty:
            dept_avg = f_df.groupby("部门")[categories].mean().reset_index()
            fig = px.bar(dept_avg, x="部门", y=categories, barmode="group")
            fig.update_layout(height=420, margin=dict(l=0,r=0,t=40,b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("当前筛选条件下无数据")

    with right:
        st.markdown("#### 高分人才 TOP5")
        if not f_df.empty:
            st.dataframe(
                f_df.nlargest(5,"综合得分")[["姓名","部门","综合得分"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("无数据")
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# 7. 人员精准画像
# =====================================================
elif page == "人员精准画像":

    if f_df.empty:
        st.warning("当前筛选条件下无人员可展示")
    else:
        target = st.selectbox("选择人员", f_df["姓名"].unique())
        row = f_df[f_df["姓名"] == target].iloc[0]

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        left, right = st.columns([2.3, 1])

        with left:
            st.markdown("#### 能力结构雷达分析")
            values = [row[c] for c in categories]
            fig = go.Figure(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0,10])),
                height=420,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.markdown(f"""
            <h2>{row['姓名']}</h2>
            <p>所属部门：{row['部门']}</p>
            <p>政治面貌：{row['政治面貌']}</p>
            <h1 style="text-align:center">{row['综合得分']}</h1>
            <p style="text-align:center;opacity:0.6;">综合能力评价</p>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### 能力分项解析")
        for c in categories:
            score = row[c]
            st.markdown(f"""
            <div class="ability-row">
                <div class="ability-title">
                    <span>{c}</span>
                    <span class="ability-tag">{score} · {ability_level(score)}</span>
                </div>
                <div class="ability-bar-bg">
                    <div class="ability-bar" style="width:{score/10*100}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# 8. 统计决策分析
# =====================================================
elif page == "统计决策分析":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["能力热力", "维度相关"])

    with tab1:
        if not f_df.empty:
            st.plotly_chart(px.imshow(f_df.set_index("姓名")[categories]), use_container_width=True)
        else:
            st.info("无数据")

    with tab2:
        if not f_df.empty:
            st.plotly_chart(px.imshow(f_df[categories].corr(), text_auto=True), use_container_width=True)
        else:
            st.info("无数据")

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# 9. 系统管理
# =====================================================
elif page == "系统管理":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("#### 数据维护")
    if st.checkbox("开启编辑模式"):
        st.data_editor(df)
    st.download_button(
        "导出筛选数据 CSV",
        f_df.to_csv(index=False).encode("utf-8-sig"),
        "filtered.csv"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# 10. 页脚
# =====================================================
st.markdown("""
<p style="text-align:center;color:#8a94a6;font-size:12px;margin-top:40px;">
北京检察科技中心 ｜ 检力资源业绩数智平台1.0 ｜ 2026
</p>
""", unsafe_allow_html=True)

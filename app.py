import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import base64
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="检力资源科学管理暨检察官业绩数智平台",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 自定义 CSS ====================
st.markdown("""
    <style>
    .main {background-color: #f8f9fc;}
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        margin-bottom: 30px;
    }
    .title-header {font-size: 2.8rem; color: #003366; text-align: center;}
    .subtitle {text-align: center; color: #555; font-size: 1.3rem; margin-bottom: 3rem;}
    .metric-card {
        background-color: #e6f0ff; padding: 15px; border-radius: 10px;
        text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== 登录系统 ====================
VALID_USERS = {
    "admin": {"password": "123456", "role": "管理员"},
    "leader": {"password": "leader2025", "role": "领导"},
    "user": {"password": "prosecutor", "role": "普通干警"},
}

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = ""

def login():
    st.markdown("<h2 style='text-align: center; color: #003366;'>⚖️ 系统登录</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submit = st.form_submit_button("登录", use_container_width=True)
        if submit:
            if username in VALID_USERS and VALID_USERS[username]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.role = VALID_USERS[username]["role"]
                st.success(f"欢迎 {username}（{st.session_state.role}）登录！")
                st.rerun()
            else:
                st.error("用户名或密码错误")

if not st.session_state.authenticated:
    login()
    st.stop()

# ==================== 标题 ====================
st.markdown('<h1 class="title-header">检力资源科学管理暨检察官业绩数智平台</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">—— 科学定岗 • 人岗适配 • 精准画像 • 增强版 v3.2 ——</p>', unsafe_allow_html=True)

# ==================== 数据加载 ====================
@st.cache_data(ttl=600)
def load_data():
    try:
        df = pd.read_excel("prosecutors_data.xlsx")
        abilities = ['业务能力', '信调宣能力', '创新能力', '学习能力', '综合能力', '政治素养']
        df['综合得分'] = df[abilities].mean(axis=1).round(2)
        return df
    except Exception as e:
        st.error(f"加载数据失败：{e} 请检查文件路径或格式。")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# ==================== 侧边栏 ====================
st.sidebar.image("https://photo.16pic.com/00/86/23/16pic_8623259_b.jpg", width=120)
st.sidebar.markdown("### 🔍 筛选与功能导航")

page = st.sidebar.radio("功能页面", ["主页画像", "统计分析", "数据管理", "AI推荐", "设置"])

search_name = st.sidebar.text_input("🔍 搜索姓名")
dept_options = ["全部"] + sorted(df["部门"].unique().tolist())
selected_dept = st.sidebar.selectbox("部门", dept_options)
min_innov = st.sidebar.slider("最低创新能力", 0.0, 10.0, 0.0, 0.1)
min_pol = st.sidebar.slider("最低政治素养", 0.0, 10.0, 0.0, 0.1)
if '年龄' in df.columns:
    min_age = st.sidebar.slider("最低年龄", int(df['年龄'].min()), int(df['年龄'].max()), 0)
sort_by = st.sidebar.selectbox("排序", ["综合得分", "业务能力", "创新能力", "政治素养"])

filtered_df = df.copy()
if search_name:
    filtered_df = filtered_df[filtered_df["姓名"].str.contains(search_name, case=False)]
if selected_dept != "全部":
    filtered_df = filtered_df[filtered_df["部门"] == selected_dept]
filtered_df = filtered_df[filtered_df["创新能力"] >= min_innov]
filtered_df = filtered_df[filtered_df["政治素养"] >= min_pol]
if '年龄' in df.columns:
    filtered_df = filtered_df[filtered_df["年龄"] >= min_age]
filtered_df = filtered_df.sort_values(by=sort_by, ascending=False)

st.sidebar.markdown(f"**筛选结果：{len(filtered_df)} 人**")

if st.session_state.role == "管理员":
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 管理员工具")
    uploaded = st.sidebar.file_uploader("上传新数据（Excel）", type="xlsx")
    if uploaded:
        try:
            new_df = pd.read_excel(uploaded)
            new_df.to_excel("prosecutors_data.xlsx", index=False)
            st.sidebar.success("数据更新成功！")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"上传失败：{e}")
    csv_backup = df.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("📥 下载数据备份 CSV", csv_backup, "backup.csv", "text/csv")

# ==================== 通用变量 ====================
categories = ['业务能力', '信调宣能力', '创新能力', '学习能力', '综合能力', '政治素养']
avatar_url = "https://imgs.699pic.com/images/505/813/424.jpg!list1x.v2"

# --- 主页画像 ---
if page == "主页画像":
    cols = st.columns(5)
    metrics = [len(df), len(filtered_df), filtered_df['综合得分'].mean().round(2) if not filtered_df.empty else 0,
               filtered_df['综合得分'].max() if not filtered_df.empty else 0,
               filtered_df['综合得分'].min() if not filtered_df.empty else 0]
    labels = ["总人数", "筛选人数", "平均得分", "最高分", "最低分"]
    for col, val, lab in zip(cols, metrics, labels):
        col.markdown(f"<div class='metric-card'><h3>{val}</h3><p>{lab}</p></div>", unsafe_allow_html=True)

    # 新：多人对比模式
    compare_mode = st.checkbox("启用多人对比模式（选择2-5人）")
    if compare_mode:
        selected_names = st.multiselect("选择对比人员", filtered_df["姓名"].tolist(), max_selections=5)
        if len(selected_names) >= 2:
            compare_df = filtered_df[filtered_df["姓名"].isin(selected_names)]
            st.subheader("多人能力对比雷达图")
            fig_compare = go.Figure()
            for _, row in compare_df.iterrows():
                values = [row[c] for c in categories]
                fig_compare.add_trace(go.Scatterpolar(
                    r=values + [values[0]],
                    theta=categories + [categories[0]],
                    fill='toself',
                    name=row['姓名']
                ))
            fig_compare.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=600)
            st.plotly_chart(fig_compare, use_container_width=True)

    if filtered_df.empty:
        st.info("无匹配人员，请调整筛选条件。")
    else:
        for _, row in filtered_df.iterrows():
            with st.expander(f"**{row['姓名']}** - 综合得分：{row['综合得分']} （点击展开）", expanded=False):
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(avatar_url, width=150)
                    st.markdown(f"**部门：** {row['部门']}<br>**政治面貌：** {row['政治面貌']}", unsafe_allow_html=True)
                    st.markdown(f"**备注：** {row.get('备注', '暂无')}")
                with col2:
                    values = [row[c] for c in categories]
                    fig_radar = go.Figure(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]],
                                                          fill='toself', line_color='#003366'))
                    fig_radar.update_layout(polar=dict(radialaxis=dict(range=[0,10])), height=450)
                    st.plotly_chart(fig_radar, use_container_width=True)

                    fig_bar = go.Figure(go.Bar(x=values, y=categories, orientation='h',
                                               text=values, textposition='outside', marker_color='#0958d9'))
                    fig_bar.update_layout(height=450, xaxis=dict(range=[0,10]))
                    st.plotly_chart(fig_bar, use_container_width=True)

                # 新：导出个人 PDF
                if st.button(f"📄 导出 {row['姓名']} PDF"):
                    buffer = io.BytesIO()
                    c = canvas.Canvas(buffer, pagesize=letter)
                    c.drawString(100, 750, f"检察官画像: {row['姓名']}")
                    c.drawString(100, 730, f"部门: {row['部门']} | 政治面貌: {row['政治面貌']}")
                    c.drawString(100, 710, f"综合得分: {row['综合得分']}")
                    y = 680
                    for cat, val in zip(categories, values):
                        c.drawString(100, y, f"{cat}: {val}")
                        y -= 20
                    c.save()
                    buffer.seek(0)
                    st.download_button("下载 PDF", buffer, f"{row['姓名']}_画像.pdf", "application/pdf")

# --- 统计分析 ---
elif page == "统计分析":
    st.subheader("能力热力图（筛选人员）")
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(10, max(4, len(filtered_df)/2)))
        sns.heatmap(filtered_df.set_index("姓名")[categories], annot=True, cmap="YlGnBu", ax=ax)
        st.pyplot(fig)

    st.subheader("综合得分分布（带KDE曲线）")
    if not filtered_df.empty:
        fig, ax = plt.subplots()
        sns.histplot(filtered_df['综合得分'], kde=True, bins=15, ax=ax)
        st.pyplot(fig)

    # 新：相关性分析
    st.subheader("能力维度相关性矩阵")
    if not filtered_df.empty:
        corr = filtered_df[categories].corr()
        fig, ax = plt.subplots(figsize=(8,6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    st.subheader("部门平均能力对比")
    dept_avg = df.groupby("部门")[categories].mean().round(2)
    fig_dept = px.bar(dept_avg.reset_index(), x="部门", y=categories, barmode="group")
    st.plotly_chart(fig_dept, use_container_width=True)

    st.subheader("Top 10 高分人员")
    st.dataframe(filtered_df.head(10)[["姓名", "部门", "综合得分"] + categories])

    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 导出筛选数据 CSV", csv, "筛选结果.csv", "text/csv")

# --- 数据管理 ---
elif page == "数据管理":
    if st.session_state.role == "管理员":
        st.subheader("在线编辑数据")
        edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("💾 保存修改"):
            edited.to_excel("prosecutors_data.xlsx", index=False)
            st.success("数据已保存！")
            st.rerun()
    else:
        st.warning("仅管理员可编辑。")
    st.subheader("完整数据预览")
    st.dataframe(df)

# --- AI推荐 ---
elif page == "AI推荐":
    st.markdown("### 🤖 AI智能推荐")
    st.markdown("**高创新人才（创新能力 ≥ 9.0）**")
    high_innov = filtered_df[filtered_df["创新能力"] >= 9.0][["姓名", "部门", "创新能力", "综合得分"]]
    st.dataframe(high_innov if not high_innov.empty else "暂无")

    st.markdown("**综合最强前5人（适合领导岗位）**")
    top5 = filtered_df.nlargest(5, "综合得分")[["姓名", "部门", "综合得分", "政治素养"]]
    st.dataframe(top5)

# --- 设置 ---
else:
    st.subheader("系统设置")
    st.write(f"当前用户：{st.session_state.username}（{st.session_state.role}）")
    dark_mode = st.checkbox("启用深色模式")
    if dark_mode:
        st.markdown("<style>.main {background-color: #1e1e1e; color: #fff;}</style>", unsafe_allow_html=True)
    if st.button("🚪 退出登录"):
        st.session_state.authenticated = False
        st.rerun()

# ==================== 底部 ====================
st.markdown("""
    <hr>
    <p style='text-align: center; color: #666;'>
    检力资源科学管理平台 v3.2 • 2025年12月31日 • 仅限内部使用
    </p>
    """, unsafe_allow_html=True)
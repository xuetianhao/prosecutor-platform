import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="检力资源科学管理暨检察官业绩数智平台",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 自定义 CSS 美化 ====================
st.markdown("""
    <style>
    .main {background-color: #f8f9fc;}
    .css-1d391kg {padding-top: 2rem;}
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        margin-bottom: 30px;
    }
    .title-header {
        font-size: 2.8rem;
        color: #003366;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #555;
        font-size: 1.3rem;
        margin-bottom: 3rem;
    }
    .metric-card {
        background-color: #e6f0ff;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .avatar {
        border-radius: 50%;
        border: 4px solid #003366;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== 简单登录系统 ====================
VALID_USERS = {
    "admin": "123456",
    "leader": "leader2025",
    "user": "prosecutor",
}

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""

def login():
    st.markdown("<h2 style='text-align: center; color: #003366;'>⚖️ 系统登录</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submit = st.form_submit_button("登录", use_container_width=True)
        
        if submit:
            if username in VALID_USERS and VALID_USERS[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"欢迎 {username} 登录成功！")
                st.rerun()
            else:
                st.error("用户名或密码错误")

if not st.session_state.authenticated:
    login()
    st.stop()

# ==================== 主界面标题 ====================
st.markdown('<h1 class="title-header">检力资源科学管理暨检察官业绩数智平台</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">—— 科学定岗 • 人岗适配 • 精准画像 ——</p>', unsafe_allow_html=True)

# ==================== 读取数据 ====================
@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_excel("prosecutors_data.xlsx")
        # 计算综合得分平均（如果没有综合能力列，可自行添加）
        abilities = ['业务能力', '信调宣能力', '创新能力', '学习能力', '综合能力', '政治素养']
        df['综合得分'] = df[abilities].mean(axis=1).round(2)
        return df
    except FileNotFoundError:
        st.error("未找到 prosecutors_data.xlsx 文件，请上传数据。")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("暂无数据，请管理员上传 Excel 文件。")
    st.stop()

# ==================== 侧边栏 ====================
st.sidebar.image("https://photo.16pic.com/00/86/23/16pic_8623259_b.jpg", width=120)  # 正式检察院徽章
st.sidebar.markdown("### 🔍 智能筛选与排序")

dept_options = ["全部"] + sorted(df["部门"].unique().tolist())
selected_dept = st.sidebar.selectbox("选择部门", dept_options)

min_innovation = st.sidebar.slider("最低创新能力分数", 0.0, 10.0, 7.0, 0.1)
min_political = st.sidebar.slider("最低政治素养分数", 0.0, 10.0, 8.0, 0.1)

sort_order = st.sidebar.radio("综合得分排序", ["从高到低", "从低到高"])

# 数据筛选与排序
filtered_df = df.copy()
if selected_dept != "全部":
    filtered_df = filtered_df[filtered_df["部门"] == selected_dept]
filtered_df = filtered_df[filtered_df["创新能力"] >= min_innovation]
filtered_df = filtered_df[filtered_df["政治素养"] >= min_political]

filtered_df = filtered_df.sort_values(by="综合得分", ascending=(sort_order == "从低到高"))

st.sidebar.markdown(f"**筛选结果：{len(filtered_df)} 人**")

# 管理员数据上传
if st.session_state.username == "admin":
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 管理员专区")
    uploaded = st.sidebar.file_uploader("上传更新后的 Excel 数据", type=["xlsx"])
    if uploaded is not None:
        try:
            new_df = pd.read_excel(uploaded)
            new_df.to_excel("prosecutors_data.xlsx", index=False)
            st.sidebar.success("数据更新成功！页面即将刷新...")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"更新失败：{e}")

# ==================== 整体统计概览 ====================
st.markdown("### 📈 全院/部门关键指标概览")
cols = st.columns(4)
total_people = len(df) if selected_dept == "全部" else len(df[df["部门"] == selected_dept])
avg_score = filtered_df['综合得分'].mean().round(2) if not filtered_df.empty else 0
top_score = filtered_df['综合得分'].max() if not filtered_df.empty else 0
cols[0].markdown(f"<div class='metric-card'><h3>{total_people}</h3><p>总人数</p></div>", unsafe_allow_html=True)
cols[1].markdown(f"<div class='metric-card'><h3>{len(filtered_df)}</h3><p>筛选后人数</p></div>", unsafe_allow_html=True)
cols[2].markdown(f"<div class='metric-card'><h3>{avg_score}</h3><p>平均综合得分</p></div>", unsafe_allow_html=True)
cols[3].markdown(f"<div class='metric-card'><h3>{top_score}</h3><p>最高综合得分</p></div>", unsafe_allow_html=True)

# ==================== 人员画像展示 ====================
if filtered_df.empty:
    st.info("当前筛选条件无匹配人员，请调整筛选条件。")
else:
    # 默认头像（检察官职业照）
    avatar_url = "https://imgs.699pic.com/images/505/813/424.jpg!list1x.v2"
    
    categories = ['业务能力', '信调宣能力', '创新能力', '学习能力', '综合能力', '政治素养']
    
    for idx, row in filtered_df.iterrows():
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            # 姓名 + 综合得分 + 基本信息
            col_name, col_avatar = st.columns([3, 1])
            with col_name:
                score_color = "#d4380d" if row['综合得分'] < 7 else "#089e60" if row['综合得分'] < 8.5 else "#0958d9"
                st.markdown(f"""
                <h3>{row['姓名']} <span style='font-size:1.8rem; color:{score_color};'>（综合得分：{row['综合得分']}/10）</span></h3>
                <p><strong>部门：</strong>{row['部门']} &nbsp;&nbsp; <strong>政治面貌：</strong>{row['政治面貌']}</p>
                <p><strong>备注/亮点：</strong><br><i>{row.get('备注', '暂无')}</i></p>
                """, unsafe_allow_html=True)
            with col_avatar:
                st.image(avatar_url, width=140, caption="检察官头像", use_column_width=False)
            
            # 图表区：雷达图 + 条形图
            col_radar, col_bar = st.columns(2)
            
            values = [row[c] for c in categories]
            
            with col_radar:
                st.subheader("能力雷达画像")
                fig_radar = go.Figure(data=go.Scatterpolar(
                    r=values + [values[0]],
                    theta=categories + [categories[0]],
                    fill='toself',
                    fillcolor='rgba(0, 102, 204, 0.4)',
                    line_color='rgba(0, 51, 102, 1)',
                    marker=dict(size=8)
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 10], showticklabels=True, ticks='outside', tickfont_size=12),
                        angularaxis=dict(tickfont_size=13, rotation=90)
                    ),
                    showlegend=False,
                    height=500,
                    margin=dict(l=60, r=60, t=60, b=60)
                )
                # 添加分数标注
                for i, v in enumerate(values):
                    fig_radar.add_annotation(
                        x=0.5, y=0.5,
                        text=f"{categories[i]}: {v}",
                        showarrow=False,
                        font_size=12,
                        xref="paper", yref="paper",
                        xshift= (100 if i % 2 == 0 else -100),
                        yshift= (80 if i < 3 else -80)
                    )
                st.plotly_chart(fig_radar, use_container_width=True)
            
            with col_bar:
                st.subheader("能力强度对比")
                fig_bar = go.Figure(go.Bar(
                    x=values,
                    y=categories,
                    orientation='h',
                    marker_color=['#0958d9', '#089e60', '#d4380d', '#faad14', '#722ed1', '#eb2f96'],
                    text=values,
                    textposition='outside'
                ))
                fig_bar.update_layout(
                    height=500,
                    xaxis=dict(range=[0, 10], title="分数"),
                    yaxis=dict(autorange="reversed"),
                    margin=dict(l=100, r=60, t=60, b=60)
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# ==================== 底部 ====================
st.markdown("""
    <hr style='margin: 60px 0;'>
    <p style='text-align: center; color: #666;'>
    数据来源于检察官业绩评价体系 | 仅限内部使用 | 持续迭代优化中 • 更新日期：2025-12-31
    </p>
    """, unsafe_allow_html=True)
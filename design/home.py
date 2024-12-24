import streamlit as st
import matplotlib.pyplot as plt


st.set_page_config(layout="wide")

st.markdown("<h1 style='text-align: center;'>😊台风数据分析系统</h1>", unsafe_allow_html=True)
st.markdown(">欢迎来到台风分析系统。请选择左侧的页面查看具体分析，此处为数据集说明部分。")

# 数据集说明
st.subheader("数据集说明")
st.image("design/assets/dataset_cover.png")

st.markdown("**RSMC 最佳轨迹数据集**")
st.markdown("该数据集包含与台风相关的天气信息。台风是在北半球形成的热带气旋。")

import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv("typhoon_data.csv")
    return df
df = load_data()

df = pd.read_csv("typhoon_data.csv")
# 显示数据集的前几行
st.subheader("数据集预览")
st.write(df.head())

# 显示数据集样本数和台风编号和年代范围
st.subheader("数据集样本数和台风编号和年代范围")
st.markdown(f"**数据集包含**: {df.shape[0]} 条记录")
st.markdown(f"**台风编号范围**: {df['International number ID'].min()} - {df['International number ID'].max()}")
st.markdown(f"**年代范围**: {df['year'].min()} - {df['year'].max()}")


# 按年份统计台风数量（以台风编号为准）
typhoon_counts = df.drop_duplicates(subset='International number ID')['year'].value_counts().sort_index()

# 绘制台风数量和年份的关系图
fig, ax = plt.subplots()
ax.plot(typhoon_counts.index, typhoon_counts.values, marker='o')
ax.set_title('Number of Typhoons per Year')
ax.set_xlabel('Year')
ax.set_ylabel('Typhoons')
fig.set_size_inches(8, 5)
# 显示图表
st.pyplot(fig)

# 显示数据集的描述性统计信息
st.subheader("数据集描述性统计信息")
st.write(df.describe())

# 显示数据集列信息和说明
st.subheader("数据集列信息和说明")
columns_info = {
    "International number ID": "台风的国际编号。前两位数字表示台风发生的年份，后两位是从 1 开始的递增整数索引。如果前导数字为零，则省略。例如，2004 年的第二个台风编号为 402；1960 年的第十个台风编号为 6010。",
    "year": "台风发生的年份。范围：1951 到 2022。",
    "month": "台风发生的月份。范围：1 到 12。",
    "day": "台风发生的日期。",
    "hour": "台风发生的小时。范围：0 到 23。",
    "grade": "台风的等级。可能的选项包括：'Tropical Depression', 'Tropical Cyclone of TS intensity or higher', 'Extra-tropical Cyclone', 'Just entering into the responsible area of RSMC Tokyo-Typhoon Center', 'Severe Tropical Storm', 'Tropical Storm', 'Typhoon'。",
    "Latitude of the center": "台风中心的纬度，缩放因子为 10。例如，如果实际纬度为 25.3，则保存为 253。",
    "Longitude of the center": "台风中心的经度，缩放因子为 10。例如，如果实际经度为 135.7，则保存为 1357。",
    "Central pressure": "台风中心的气压，单位为百帕（hPa）。中央气压是衡量台风强度的重要指标之一，通常气压越低，台风强度越强。",
    "Maximum sustained wind speed": "台风中心附近的最大持续风速，单位为节（kt）。最大持续风速是衡量台风强度的另一个重要指标。",
    "Direction of the longest radius of 50kt winds or greater": "50节（kt）或更大风速的最长半径的方向。可能的方向包括北（N）、东北（NE）、东（E）、东南（SE）、南（S）、西南（SW）、西（W）和西北（NW）。",
    "The longest radius of 50kt winds or greater": "50节（kt）或更大风速的最长半径，单位为海里（nm）。这是台风风场的一个重要指标，表示台风影响范围的大小。",
    "The shortest radius of 50kt winds or greater": "50节（kt）或更大风速的最短半径，单位为海里（nm）。这是台风风场的另一个重要指标。",
    "Direction of the longest radius of 30kt winds or greater": "30节（kt）或更大风速的最长半径的方向。可能的方向包括北（N）、东北（NE）、东（E）、东南（SE）、南（S）、西南（SW）、西（W）和西北（NW）。",
    "The longest radius of 30kt winds or greater": "30节（kt）或更大风速的最长半径，单位为海里（nm）。这是台风风场的一个重要指标，表示台风影响范围的大小。",
    "The shortest radius of 30kt winds or greater": "30节（kt）或更大风速的最短半径，单位为海里（nm）。这是台风风场的另一个重要指标。",
    "Indicator of landfall or passage": "指示台风是否登陆或经过陆地。可能的值包括空格（' '）和井号（'#'）。井号（'#'）表示台风中心已经到达陆地。首次出现井号是在1991年。"
}

columns_df = pd.DataFrame(list(columns_info.items()), columns=["列名", "说明"])
st.table(columns_df)


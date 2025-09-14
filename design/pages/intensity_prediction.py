import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.markdown("<h1 style='text-align: center;'>😈强度预测</h1>", unsafe_allow_html=True)

# 获取脚本所在目录的父目录（design目录）
script_dir = Path(__file__).parent.parent

@st.cache_data
def looad_intensity_data():
    grade_file = script_dir / "result" / "grade_trend" / "part-00000-7dcf4de8-72b3-42bb-bf65-4d2d581f866e-c000.csv"
    intensity_file = script_dir / "result" / "intensity_trend" / "part-00000-230f148b-8c77-4f42-bc0c-4d0236d48799-c000.csv"
    
    if not grade_file.exists():
        st.error(f"等级趋势文件不存在: {grade_file}")
        return None, None
    if not intensity_file.exists():
        st.error(f"强度趋势文件不存在: {intensity_file}")
        return None, None
        
    df_grade = pd.read_csv(grade_file)
    df_intensiy = pd.read_csv(intensity_file)
    return df_grade, df_intensiy


def looad_intensity_prediction_data():
    prediction_file = script_dir / "result" / "intensity_prediction" / "part-00000-651bd2cc-72c9-443e-95a8-0bd1fc307dce-c000.csv"
    
    if not prediction_file.exists():
        st.error(f"强度预测文件不存在: {prediction_file}")
        return None
        
    df = pd.read_csv(prediction_file)
    return df

# 加载数据
df_grade, df_intensity = looad_intensity_data()
df_intensity_prediction = looad_intensity_prediction_data()

# 检查数据是否成功加载
if df_grade is None or df_intensity is None or df_intensity_prediction is None:
    st.error("数据文件加载失败，请检查文件是否存在")
    st.stop()


st.markdown("### 一、历史数据分析")
st.markdown("##### 台风级别分布")
grade_distribution = df_grade['grade'].value_counts()
fig, ax = plt.subplots()
ax.pie(grade_distribution, labels=grade_distribution.index, autopct='%1.1f%%', startangle=90)
ax.axis('equal')  
st.pyplot(fig)

st.markdown("##### 台风强度变换趋势")
fig, ax1 = plt.subplots(figsize=(10, 6))

ax2 = ax1.twinx()
ax1.plot(df_intensity['year'], df_intensity['avg_central_pressure'], 'g-')
ax2.plot(df_intensity['year'], df_intensity['avg_wind_speed'], 'b-')

ax1.set_xlabel('Date')
ax1.set_ylabel('Average Central Pressure', color='g')
ax2.set_ylabel('Average Wind Speed', color='b')
plt.title('Typhoon Intensity Change Over Time')
plt.xticks(rotation=45)
st.pyplot(fig)

st.markdown("##### 台风类型变化趋势")
fig, ax = plt.subplots(figsize=(10, 6))
for grade in df_grade['grade'].unique():
    subset = df_grade[df_grade['grade'] == grade]
    ax.plot(subset['year'], subset['count'], label=grade)

ax.set_xlabel('Year')
ax.set_ylabel('Count')
plt.title('Typhoon Type Change Over Time')
plt.legend()
plt.xticks(rotation=45)
st.pyplot(fig)

st.markdown("### 二、强度预测分析")
st.markdown("##### 预测的强度与实际值比较")
fig, ax1 = plt.subplots(figsize=(10, 6))

# 选择最近30年
df_intensity_last_30_years = df_intensity[df_intensity['year'] >= df_intensity['year'].max() - 30]

# 最近30年的实际值
fig, ax1 = plt.subplots(figsize=(10, 6))

ax2 = ax1.twinx()
ax1.plot(df_intensity_last_30_years['year'], df_intensity_last_30_years['avg_central_pressure'], 'g-')
ax2.plot(df_intensity_last_30_years['year'], df_intensity_last_30_years['avg_wind_speed'], 'b-')

ax1.plot(df_intensity_prediction['year'], df_intensity_prediction['predicted_pressure'], 'g--')
ax2.plot(df_intensity_prediction['year'], df_intensity_prediction['predicted_wind_speed'], 'b--')

ax1.set_xlabel('Date')
ax1.set_ylabel('Average Central Pressure', color='g')
ax2.set_ylabel('Average Wind Speed', color='b')
plt.title('Typhoon Intensity Change Over Time')
plt.xticks(rotation=45)
st.pyplot(fig)

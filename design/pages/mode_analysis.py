import streamlit as st
import folium
import pandas as pd
import plotly.express as px
from pathlib import Path

st.markdown("<h1 style='text-align: center;'>🤓👆模式分析</h1>", unsafe_allow_html=True)

# 获取脚本所在目录的父目录（design目录）
script_dir = Path(__file__).parent.parent

@st.cache_data
def load_data():
    track_file = script_dir / "result" / "track" / "part-00000-a99a94b6-e428-49f1-b3b0-411b1034eaac-c000.csv"
    if not track_file.exists():
        st.error(f"轨迹文件不存在: {track_file}")
        return None
    df_track = pd.read_csv(track_file)
    return df_track

@st.cache_data
def load_distance_data():
    distance_file = script_dir / "result" / "avg_distance" / "part-00000-688ae885-e7d1-43d7-b5c1-8574a0eae789-c000.csv"
    if not distance_file.exists():
        st.error(f"平均距离文件不存在: {distance_file}")
        return None
    df_distance = pd.read_csv(distance_file)
    return df_distance

@st.cache_data
def load_intensity_data():
    intensity_file = script_dir / "result" / "intensity_trend" / "part-00000-230f148b-8c77-4f42-bc0c-4d0236d48799-c000.csv"
    if not intensity_file.exists():
        st.error(f"强度趋势文件不存在: {intensity_file}")
        return None
    df_intensity = pd.read_csv(intensity_file)
    return df_intensity

@st.cache_data
def load_predict_data():
    predict_file = script_dir / "result" / "position_predict.csv"
    if not predict_file.exists():
        st.error(f"位置预测文件不存在: {predict_file}")
        return None
    df = pd.read_csv(predict_file)
    return df

@st.cache_data
def load_landed_history_data():
    history_file = script_dir / "result" / "landed_history_pressure.csv"
    if not history_file.exists():
        st.error(f"登陆历史文件不存在: {history_file}")
        return None
    df = pd.read_csv(history_file)
    return df

# 加载所有数据
df_track = load_data()
df_distance = load_distance_data()
df_intensity = load_intensity_data()
df_predict = load_predict_data()
df_predict_history = load_landed_history_data()

# 检查关键数据是否加载成功
if df_track is None:
    st.error("轨迹数据加载失败，无法继续")
    st.stop()

# 其他数据如果缺失，显示警告但继续运行
missing_data = []
if df_distance is None:
    missing_data.append("平均距离数据")
if df_intensity is None:
    missing_data.append("强度趋势数据")
if df_predict is None:
    missing_data.append("位置预测数据")
if df_predict_history is None:
    missing_data.append("登陆历史数据")

if missing_data:
    st.warning(f"以下数据文件缺失，部分功能可能受限: {', '.join(missing_data)}")


################################################################################################################
from folium.plugins import HeatMap
@st.cache_resource
def generate_typhoon_heatmap(df_track, start_year, end_year):
# 过滤指定年份范围内的数据
    typhoon_data = df_track[(df_track['year'] >= start_year) & (df_track['year'] <= end_year)]
    # 创建 Folium 地图对象
    m = folium.Map(location=[20, 120], zoom_start=5)
    # 提取坐标数据
    heat_data = [[row['latitude'], row['longitude']] for index, row in typhoon_data.iterrows()]
    # 添加热力图层
    HeatMap(heat_data, radius=5, blur=10).add_to(m)
    
    return m
@st.cache_resource
def get_map_by_id(storm_id):
    if df_track is None:
        return None
    typhoon = df_track[df_track['storm_id'] == storm_id]
    typhoon['latitude'] = typhoon['latitude'].astype(float)
    typhoon['longitude'] = typhoon['longitude'].astype(float)
    typhoon['date'] = pd.to_datetime(typhoon['date'])
    return get_map(typhoon[['latitude', 'longitude']].to_records(index=False), typhoon['date'], storm_id)

@st.cache_resource
def get_map(coordinates, dates, storm_id):
    m = folium.Map()  # Folium 地图对象 
    m.fit_bounds(coordinates.tolist())  # 调整地图视角
    folium.PolyLine(locations=coordinates, color='blue').add_to(m)  # 绘制一条蓝色的折线，表示台风路径
    folium.Marker(location=coordinates[0], popup="start").add_to(m)  # 起点标记
    for coord, date in zip(coordinates, dates):
        folium.Circle(location=coord,
                      color='yellow' if date.hour else 'orange').add_to(m)
    
    # 添加预测路径（如果预测数据可用）
    if df_predict is not None:
        predicted_path = df_predict[df_predict['International number ID'] == storm_id]
        if not predicted_path.empty:
            predicted_coordinates = predicted_path[['Latitude of the center', 'Longitude of the center']].to_records(index=False)
            folium.PolyLine(locations=predicted_coordinates, color='red', dash_array='5').add_to(m)  # 绘制红色虚线表示预测路径
            folium.Marker(location=predicted_coordinates[-1], popup="predicted end", icon=folium.Icon(color='red')).add_to(m)  # 预测终点标记
    
    return m
################################################################################################################
st.markdown("### 一、时序分析")
with st.expander("热力图选项"):
    year_range = st.slider("选择年份范围", min_value=int(df_track['year'].min()), max_value=int(df_track['year'].max()), value=(1990, 2000), key="year_range")
    start_year, end_year = year_range
    radius = st.number_input("选择热力图半径", min_value=1, max_value=10, value=5, key="radius")
    blur = st.number_input("选择热力图模糊度", min_value=5, max_value=20, value=10, key="blur")
if st.button("显示热力图", key="show_heatmap"):
    heatmap = generate_typhoon_heatmap(df_track, start_year, end_year)
    st.components.v1.html(heatmap._repr_html_(), height=500)

################################################################################################################
st.markdown("### 二、单台风轨迹可视化")

if df_predict is not None:
    landed_storms = df_predict['International number ID']
else:
    landed_storms = pd.Series([], dtype='int64')  # 空的Series

def get_name(x):
    global landed_storms
    if x["storm_id"] in landed_storms.values:
        name = f"{x['storm_id']} ({x['year']}) #"
    else:
        name = f"{x['storm_id']} ({x['year']})"
    return name

selected_year_for_id = st.number_input("输入年份", min_value=int(df_track['year'].min()), max_value=int(df_track['year'].max()),
                                       value=1994, key="selected_year_for_id")
filtered_df = df_track[(df_track['year'] == selected_year_for_id)]


selected_storm_id = st.selectbox("选择台风ID(含有#的为有登陆过的台风)", filtered_df[['storm_id', 'year']].drop_duplicates()
                                 .sort_values(by='year', ascending=True).apply(get_name, axis=1), index=0)
st.write("注：路径和强度预测只针对有登陆的台风")
selected_storm_id = int(selected_storm_id.split(" (")[0])

if st.button("显示地图", key="show_map"):
    typhoon_info = df_track[df_track['storm_id'] == selected_storm_id]
    
    # 显示平均距离信息（如果数据可用）
    if df_distance is not None:
        avg_distance_data = df_distance[df_distance['storm_id'] == selected_storm_id]['avg_distance']
        if not avg_distance_data.empty:
            avg_distance = avg_distance_data.values[0]
            st.markdown(f"<div style='text-align: left;'><strong>台风等级:</strong> {typhoon_info['grade'].iloc[0]}<br><strong>平均移动距离:</strong> {avg_distance:.4f} km</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align: left;'><strong>台风等级:</strong> {typhoon_info['grade'].iloc[0]}<br><strong>平均移动距离:</strong> 数据不可用</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align: left;'><strong>台风等级:</strong> {typhoon_info['grade'].iloc[0]}<br><strong>平均移动距离:</strong> 数据不可用</div>", unsafe_allow_html=True)
    
    folium_map = get_map_by_id(selected_storm_id)
    if folium_map is not None:
        st.components.v1.html(folium_map._repr_html_(), height=500)

        # 显示强度预测（如果数据可用）
        if df_predict is not None and selected_storm_id in landed_storms.values:
            predicted_intensity = df_predict[df_predict['International number ID'] == selected_storm_id]
            if df_predict_history is not None:
                history_intensity = df_predict_history[df_predict_history['International number ID'] == selected_storm_id]
                fig = px.line(predicted_intensity, x='date', y='Central pressure', title='强度趋势')
                fig.add_scatter(x=history_intensity['datetime'], y=history_intensity['Central pressure'], mode='lines', name='历史强度')
                fig.add_scatter(x=predicted_intensity['date'], y=predicted_intensity['Central pressure'], mode='lines', name='预测强度')
                st.plotly_chart(fig)
            else:
                st.warning("历史强度数据不可用")
        elif df_predict is None:
            st.info("预测数据不可用")
    else:
        st.error("无法生成地图，数据可能有误")
    
    

    



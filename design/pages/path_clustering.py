import streamlit as st
import pandas as pd
import folium
from pathlib import Path

st.markdown("<h1 style='text-align: center;'>😎路径聚类</h1>", unsafe_allow_html=True)

# 获取脚本所在目录的父目录（design目录）
script_dir = Path(__file__).parent.parent

@st.cache_data
def load_data():
    cluster2_file = script_dir / 'result' / 'clusters' / 'cluster2' / 'part-00000-2de41987-4dd4-4354-bb79-0d88682d2fe8-c000.csv'
    cluster3_file = script_dir / 'result' / 'clusters' / 'cluster3' / 'part-00000-44c3cb5e-cbaf-425f-bc3b-6e3dc2b8473f-c000.csv'
    cluster4_file = script_dir / 'result' / 'clusters' / 'cluster4' / 'part-00000-db54e985-6431-4359-b6e7-ff0de7c78cad-c000.csv'
    features_file = script_dir / 'result' / 'clusters' / 'features' / 'part-00000-532e7d9b-f021-41d5-b3f4-494d20e975cc-c000.csv'
    
    # 检查文件是否存在
    files_status = {
        'cluster2': cluster2_file.exists(),
        'cluster3': cluster3_file.exists(),
        'cluster4': cluster4_file.exists(),
        'features': features_file.exists()
    }
    
    missing_files = [name for name, exists in files_status.items() if not exists]
    if missing_files:
        st.error(f"以下聚类文件缺失: {', '.join(missing_files)}")
        st.info("请确保以下文件存在:")
        for name, file_path in [('cluster2', cluster2_file), ('cluster3', cluster3_file), 
                               ('cluster4', cluster4_file), ('features', features_file)]:
            if name in missing_files:
                st.write(f"- {file_path}")
    
    # 尝试加载存在的文件
    df_cluster2 = pd.read_csv(cluster2_file) if files_status['cluster2'] else None
    df_cluster3 = pd.read_csv(cluster3_file) if files_status['cluster3'] else None
    df_cluster4 = pd.read_csv(cluster4_file) if files_status['cluster4'] else None
    df_features = pd.read_csv(features_file) if files_status['features'] else None
    
    return df_cluster2, df_cluster3, df_cluster4, df_features

# 加载数据
c2, c3, c4, features = load_data()

@st.cache_resource
def show_cluster(clusters):
    if clusters is None:
        return None
        
    # 将聚类结果转换为 Pandas DataFrame
    clusters_pd = clusters[["prediction", "points"]]
    # 创建一个地图对象
    m = folium.Map(location=[20, 130], zoom_start=3)

    # 为每个聚类添加点
    for cluster in clusters_pd['prediction'].unique():
        if cluster == 0:
            color = 'red'
        elif cluster == 1:
            color = 'blue'
        elif cluster == 2:
            color = 'yellow'
        else:
            color = 'green'
 
        cluster_points = clusters_pd[clusters_pd['prediction'] == cluster]['points']
        for points in cluster_points:
            points = eval(points)
            folium.PolyLine(points, color=color, weight=0.2).add_to(m) 
    # 显示地图
    return m

st.markdown("### 一、提取的特征")
if features is not None:
    st.write(features.head())
else:
    st.error("特征数据不可用")

st.markdown("### 二、查看聚类")
cluster_option = st.selectbox("选择聚类数", [2, 3, 4])

# 选择对应的聚类数据
clusters = None
if cluster_option == 2 and c2 is not None:
    clusters = c2
elif cluster_option == 3 and c3 is not None:
    clusters = c3
elif cluster_option == 4 and c4 is not None:
    clusters = c4

if clusters is None:
    st.error(f"聚类{cluster_option}的数据不可用")
else:
    if st.button("查看分布图"):
        folium_map = show_cluster(clusters)
        if folium_map is not None:
            st.components.v1.html(folium_map._repr_html_(), height=500)
            st.markdown("##### 分布直方图")
            cluster_counts = clusters['prediction'].value_counts().sort_index()
            cluster_counts.index = cluster_counts.index.map({0: 'red', 1: 'blue', 2: 'yellow', 3: 'green'})
            st.bar_chart(cluster_counts)
        else:
            st.error("无法生成聚类地图")


    
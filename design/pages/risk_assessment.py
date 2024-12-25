import streamlit as st
from zhipuai import ZhipuAI
import os
import httpx
from pathlib import Path
import json
st.markdown("<h1 style='text-align: center;'>😰风险评估</h1>", unsafe_allow_html=True)




template = """
    使用知识库中的信息{knowledge},其中
    'year_season_typhoon.csv'包括历年的各季节的台风数量,
    ’year_landings_addr.csv‘包含各年出现的登陆的台风的登陆位置坐标和经纬度，如果有多对位置则说明有多个台风登陆。
    你需要2利用这两个文件的信息来进行台风气象数据的风险评估{question}总结
    你可能需要关注如：
    台风频率随年份的变化趋势、
    不同强度台风的分布特性（如路径集中区域、登陆地点统计）、
    不同时间段（如夏季 vs 冬季）的台风活动对比。
"""

zhipu_api_key="6328b91e5a03d4284108b0f6065f936e.qa0IS6bGvUmeRp8f"
os.environ["ZHIPUAI_API_KEY"] = zhipu_api_key



client = ZhipuAI(api_key=zhipu_api_key) 

file_01 = client.files.create(file=Path("design/result/llmdata/year_landings_addr.csv"), purpose="file-extract")
content_01 = json.loads(client.files.content(file_01.id).content)["content"]
client.files.delete(file_id=file_01.id)

file_02 = client.files.create(file=Path("design/result/llmdata/year_season_typhoon.csv"), purpose="file-extract")
content_02 = json.loads(client.files.content(file_02.id).content)["content"]
client.files.delete(file_id=file_02.id)

user_input = st.text_input(label='user input:',value="生成台风分析报告")
if st.button('生成'):
    
    input_template=f"{user_input}\n需要根据文件的内容进行分风险评价，你的回答不应该太长，不能超过20行\n文件一包括历年的各季节的台风数量，内容为：{content_02}\n文件二包括各年出现的登陆的台风的登陆位置地址和经纬度，如果有多对位置则说明有多个台风登陆，内容为：{content_01}"
    
    
    response = client.chat.completions.create(
        model="glm-4-air",  
        messages=[
            {"role": "user", "content": input_template},
        ],
        # tools=[
        #         {
        #             "type": "retrieval",
        #             "retrieval": {
        #                 "knowledge_id": "1871359571260534784",
        #                 "prompt_template": template
        #             }
        #         }
        #         ],
        stream=True,
    )
    result = ""
    with st.container():
        result_container = st.empty()
        k=0
        for chunk in response:
            result += chunk.choices[0].delta.content
            k=k+1
            result_container.text_area("Result", result, height=300,key=k)
            

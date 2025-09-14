import streamlit as st
import os
import sys
from pathlib import Path
# LangChain imports
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import our custom DeepSeek LLM
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from deepseek_llm import DeepSeekLLM

st.markdown("<h1 style='text-align: center;'>😰风险评估</h1>", unsafe_allow_html=True)


def init_deepseek_chain():
    """Initialize DeepSeek LLM with LangChain chain"""
    # 尝试多种方式获取API密钥
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    # 如果环境变量未设置，检查是否有配置文件
    if not api_key:
        config_file = Path(__file__).parent.parent / "config.json"
        if config_file.exists():
            try:
                import json
                with open(config_file, 'r',encoding='utf-8') as f:
                    config = json.load(f)
                    api_key = config.get("deepseek_api_key")
            except Exception as e:
                st.error(f"读取配置文件失败: {e}")
                return None
    
    try:
        # Create DeepSeek LLM instance
        llm = DeepSeekLLM(
            model="deepseek-chat",
            api_key=api_key,
            temperature=0.7,
            max_tokens=1024
        )
        
        # 简单的API连接测试（不显示成功消息）
        test_response = llm._call("Hi", max_tokens=5)
        
    except Exception as e:
        st.error(f"❌ DeepSeek API 初始化失败: {str(e)}")
        return None
######################################################################
    # Create prompt template using ChatPromptTemplate
    system_template = """你是一个专业的台风气象数据分析专家。请基于提供的历史台风数据进行风险评估分析。
    
数据说明：
- 数据一：历年各季节的台风数量统计
- 数据二：各年登陆台风的地理位置坐标和经纬度信息

分析要求：
1. 台风频率随年份的变化趋势
2. 不同强度台风的分布特性（如路径集中区域、登陆地点统计）
3. 不同时间段（如夏季 vs 冬季）的台风活动对比
4. 基于历史数据的风险评估

请确保回答简洁明了，不超过20行。"""

    human_template = """{user_query}

数据一（历年各季节台风数量）：
{seasonal_data}

数据二（登陆台风位置信息）：
{landing_data}"""
#######################################################################
    
    # prompt
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", human_template)
    ])
    
    # Create output parser
    output_parser = StrOutputParser()
    
    # the chain
    chain = chat_prompt | llm | output_parser
    return chain


def load_typhoon_data():
    """Load typhoon data files"""
    try:
        # 获取脚本所在目录的父目录（design目录）
        script_dir = Path(__file__).parent.parent
        
        # Load seasonal typhoon data
        seasonal_file = script_dir / "result" / "llmdata" / "year_season_typhoon.csv"
        if not seasonal_file.exists():
            st.error(f"季节数据文件不存在: {seasonal_file}")
            return None, None
            
        with open(seasonal_file, 'r', encoding='utf-8') as f:
            seasonal_data = f.read()
        
        # Load landing data
        landing_file = script_dir / "result" / "llmdata" / "year_landings_addr.csv"
        if not landing_file.exists():
            st.error(f"登陆数据文件不存在: {landing_file}")
            return None, None
            
        with open(landing_file, 'r', encoding='utf-8') as f:
            landing_data = f.read()
            
        return seasonal_data, landing_data
    except Exception as e:
        st.error(f"数据文件加载失败: {e}")
        return None, None


# User interface
user_input = st.text_input(
    label='请输入您的分析需求:',
    value="生成台风分析报告",
    help="例如：生成台风风险评估报告、分析台风登陆趋势等"
)

if st.button('生成风险评估报告'):
    # 只在点击按钮时初始化并检查API
    with st.spinner('初始化 DeepSeek LLM...'):
        chain = init_deepseek_chain()
    
    if chain is None:
        st.error("LLM 初始化失败，请检查 API 配置")
    else:
        # Load data
        seasonal_data, landing_data = load_typhoon_data()
        
        if seasonal_data and landing_data:
            try:
                with st.spinner('正在生成风险评估报告...'):
                    # Use the LangChain chain to generate response
                    response = chain.invoke({
                        "user_query": user_input,
                        "seasonal_data": seasonal_data,
                        "landing_data": landing_data
                    })
                    
                    # Display the result
                    st.subheader("🌪️ 台风风险评估报告")
                    st.markdown(response)
                    
            except Exception as e:
                st.error(f"生成报告时出错: {e}")
        else:
            st.error("无法加载数据文件，请确保数据文件存在")



# Add configuration section in sidebar
st.sidebar.header("⚙️ 配置")
st.sidebar.markdown("""
**当前配置:**
- 模型: DeepSeek Chat
- 框架: LangChain
- 温度: 0.7
- 最大令牌: 1024

**数据源:**
- 历年季节台风统计
- 登陆台风位置数据
""")

if st.sidebar.button("检查数据文件"):
    script_dir = Path(__file__).parent.parent
    seasonal_file = script_dir / "result" / "llmdata" / "year_season_typhoon.csv"
    landing_file = script_dir / "result" / "llmdata" / "year_landings_addr.csv"
    
    st.sidebar.write("文件状态:")
    st.sidebar.write(f"- 季节统计文件: {'✅ 存在' if seasonal_file.exists() else '❌ 缺失'}")
    st.sidebar.write(f"- 登陆数据文件: {'✅ 存在' if landing_file.exists() else '❌ 缺失'}")
    
    if not seasonal_file.exists():
        st.sidebar.write(f"  路径: {seasonal_file}")
    if not landing_file.exists():
        st.sidebar.write(f"  路径: {landing_file}")
import sys
from pathlib import Path

import streamlit as st
from streamlit_lottie import st_lottie

project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    print(project_root)
    sys.path.append(project_root)

from code_agent.code_finance.Streamline_Analyst.app.util import load_lottie
from code_agent.code_finance.Streamline_Analyst.app.prediction_model import prediction_model_pipeline
from code_agent.code_finance.Streamline_Analyst.app.cluster_model import cluster_model_pipeline
from code_agent.code_finance.Streamline_Analyst.app.regression_model import regression_model_pipeline
from code_agent.code_finance.Streamline_Analyst.app.visualization import data_visualization
from code_agent.code_finance.Streamline_Analyst.app.src.util import read_file_from_streamlit

# C:\Users\m01216.METAX-TECH\Desktop\code\awesome-llm-apps\code_agent\code_finance\Streamline-Analyst
def main_Streamline_Analyst():
    st.set_page_config(page_title="Streamline Analyst", page_icon=":rocket:", layout="wide")

    openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
    openai_api_model_type = st.sidebar.text_input("LLM API Model Type",
                                                  value=st.session_state.get('openai_api_model_type'))
    # openai_api_base_url = st.sidebar.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))
    openai_api_base_url = st.session_state.get('openai_api_base_url')
    st.title("数据分析师Agent")
    # st.markdown("""Analyst Agent🪄是一个开源的基于LLM大语言模型的Agent应用，目标简化数据分析中从数据清洗到模型测试的全部流程。分类预测、聚类、回归、数据集可视化、数据预处理、编码、特征选择、目标属性判断、可视化、最佳模型选择等等任务都可自主决策和执行。用户需要做的只有选择数据文件、选择分析模式，剩下的工作就可以让AI来接管了🔮。所有处理后的数据和训练的模型都可下载。
    #
    # """)

    # TITLE SECTION
    # with st.container():
    #     st.subheader("Hello there 👋")
    #     st.title("Welcome to Streamline Analyst!")
    #     if 'initialized' not in st.session_state:
    #         st.session_state.initialized = True
    #     if st.session_state.initialized:
    #         st.session_state.welcome_message = welcome_message()
    #         st.write(stream_data(st.session_state.welcome_message))
    #         time.sleep(0.5)
    #         st.write("[Github > ](https://github.com/Wilson-ZheLin/Streamline-Analyst)")
    #         st.session_state.initialized = False
    #     else:
    #         st.write(st.session_state.welcome_message)
    #         st.write("[Github > ](https://github.com/Wilson-ZheLin/Streamline-Analyst)")

    # INTRO SECTION
    with st.container():
        st.divider()
        if 'lottie' not in st.session_state:
            st.session_state.lottie_url1, st.session_state.lottie_url2 = load_lottie()
            st.session_state.lottie = True

        left_column_r1, right_column_r1 = st.columns([6, 4])
        with left_column_r1:
            st.header("数据分析师Agent可以做什么?")
            st.markdown("""作为数据分析师Agent，**Analyst Agent**能够根据您的数据做出自主决策：
  - 轻松的数据预处理
  - 智能编码与平衡
  - 自动模型选择和训练
  - 动态数据可视化""")
        with right_column_r1:
            if st.session_state.lottie:
                st_lottie(st.session_state.lottie_url1, height=280, key="animation1")

        left_column_r2, _, right_column_r2 = st.columns([6, 1, 5])
        with left_column_r2:
            if st.session_state.lottie:
                st_lottie(st.session_state.lottie_url2, height=200, key="animation2")
        with right_column_r2:
            st.header("简单易用")
            # st.write(introduction_message()[1])
            st.markdown("""**您只需**:
  1. **选择**您的数据文件
  2. **选择**分析模式
  3. **按下**开始按钮
            """)
    st.markdown("""#### 核心功能

1. **全流程自动化分析**

- 支持完整数据分析流程：从数据清洗到模型训练
- 自动处理关键环节：
  - 数据预处理（缺失值填充/数据标准化）
  - 特征工程（编码/降维）
  - 模型选择与训练
  - 结果可视化

1. **智能决策辅助**

- 自动识别分析目标属性
- 智能推荐最佳处理方案：
  - 数据平衡策略（SMOTE等）
  - 数据集划分比例
  - 最优算法选择

#### 技术特点

- 基于大语言模型（LLM）的自主决策引擎
- 支持常见分析任务：
  - 预测分析（分类/回归）
  - 聚类分析
  - 数据可视化
- 处理结果可下载（数据/模型）

#### 适用场景
  - 自动化财务数据清洗与分析
  - 风险预测模型快速构建
  - 财务指标可视化呈现
  - 案件数据模式识别
  - 法律风险量化分析
  - 诉讼结果预测建模

#### 支持的建模任务：

| **分类模型**                      | **聚类模型**                   | **回归模型**                         |
|----------------------------------|-------------------------------|-------------------------------------|
| 逻辑回归                          | K-均值聚类                    | 线性回归                             |
| 随机森林                          | DBSCAN                        | 岭回归                               |
| 支持向量机                        | 高斯混合模型                  | Lasso回归                            |
| 梯度提升机                        | 层次聚类                      | 弹性网回归                           |
| 高斯朴素贝叶斯                    | 谱聚类                        | 随机森林回归                         |
| AdaBoost                          | 其他                          | 梯度提升回归                         |
| XGBoost                           |                               | 其他                                 |

#### 实时计算模型指标与结果可视化：

| **分类指标 & 图表**                | **聚类指标 & 图表**            | **回归指标 & 图表**                   |
|------------------------------------|--------------------------------|---------------------------------------|
| 模型分数                            | 轮廓分数                        | R平方分数                             |
| 混淆矩阵                            | Calinski-Harabasz 分数         | 均方误差 (MSE)                        |
| AUC                                 | Davies-Bouldin 分数            | 均方根误差 (RMSE)                     |
| F1 分数                             | 聚类散点图                      | 绝对误差 (MAE)                        |
| ROC 曲线                            | 其他                           | 残差图                                |
| 其他                                |                                | 预测值 vs 实际值图                    |
|                                    |                                | 分位数-分位数图                       |


#### 可视化分析工具包:

Analyst Agent 🪄 提供了一系列直观的可视化工具，这部分的使用**无需 API Key**：

* **单属性可视化**: 深入个别数据方面的洞察视图
* **单属性可视化**: 变量间关系的全面分析
* **三维绘图**: 复杂数据关系的3D可视化
* **Word Clouds**: 通过词频突出关键主题和概念
* **世界热力图**: 使地理趋势和分布可视化
    
    """)
    # MAIN SECTION
    with st.container():
        st.divider()
        st.header("开始操作")
        left_column, right_column = st.columns([6, 4])
        with left_column:
            # API_KEY = st.text_input(
            #     "Your API Key won't be stored or shared!",
            #     placeholder="Enter your API key here...",
            # )
            API_KEY=openai_api_key
            # st.write("👆Your OpenAI API key:")
            uploaded_file = st.file_uploader("选择上传一个数据文件。上传的数据不会被存储！", accept_multiple_files=False, type=['csv', 'json', 'xls', 'xlsx'])
            if uploaded_file:
                if uploaded_file.getvalue():
                    uploaded_file.seek(0)
                    st.session_state.DF_uploaded = read_file_from_streamlit(uploaded_file)
                    st.session_state.is_file_empty = False
                else:
                    st.session_state.is_file_empty = True

        with right_column:
            # SELECTED_MODEL = st.selectbox(
            # 'Which OpenAI model do you want to use?',
            # ('GPT-4-Turbo', 'GPT-3.5-Turbo'))
            SELECTED_MODEL=openai_api_model_type
            MODE = st.selectbox(
            '选择合适的数据分析模式',
            ('Predictive Classification', 'Clustering Model', 'Regression Model', 'Data Visualization'))

            # st.write(f'xuan: :green[{SELECTED_MODEL}]')
            # st.write(f'Data analysis mode: :green[{MODE}]')

        # Proceed Button
        is_proceed_enabled = uploaded_file is not None and API_KEY != "" or uploaded_file is not None and MODE == "Data Visualization"

        # Initialize the 'button_clicked' state
        if 'button_clicked' not in st.session_state:
            st.session_state.button_clicked = False
        if st.button('开始分析', disabled=(not is_proceed_enabled) or st.session_state.button_clicked, type="primary"):
            st.session_state.button_clicked = True
        if "is_file_empty" in st.session_state and st.session_state.is_file_empty:
            st.caption('Your data file is empty!')

        # Start Analysis
        if st.session_state.button_clicked:
            GPT_MODEL = 4 if SELECTED_MODEL == 'GPT-4-Turbo' else 3.5
            with st.container():
                if "DF_uploaded" not in st.session_state:
                    st.error("File is empty!")
                else:
                    # openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
                    #     openai_api_model_type = st.sidebar.text_input("LLM API Model Type",
                    #                                                   value=st.session_state.get('openai_api_model_type'))
                    #     openai_api_base_url
                    if MODE == 'Predictive Classification':
                        prediction_model_pipeline(st.session_state.DF_uploaded, openai_api_key, GPT_MODEL,openai_api_model_type,openai_api_base_url)
                    elif MODE == 'Clustering Model':
                        cluster_model_pipeline(st.session_state.DF_uploaded, openai_api_key, GPT_MODEL,openai_api_model_type,openai_api_base_url)
                    elif MODE == 'Regression Model':
                        regression_model_pipeline(st.session_state.DF_uploaded, openai_api_key, GPT_MODEL,openai_api_model_type,openai_api_base_url)
                    elif MODE == 'Data Visualization':
                        data_visualization(st.session_state.DF_uploaded)
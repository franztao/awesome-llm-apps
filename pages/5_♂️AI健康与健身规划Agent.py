import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAILike

st.set_page_config(
    page_title="AI Health & Fitness Planner",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0fff4;
        border: 1px solid #9ae6b4;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fffaf0;
        border: 1px solid #fbd38d;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

def display_dietary_plan(plan_content):
    with st.expander("📋 您的个性化饮食计划", expanded=True):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 🎯 Why this plan works")
            st.info(plan_content.get("why_this_plan_works", "Information not available"))
            st.markdown("### 🍽️ Meal Plan")
            st.write(plan_content.get("meal_plan", "Plan not available"))

        with col2:
            st.markdown("### ⚠️ Important Considerations")
            considerations = plan_content.get("important_considerations", "").split('\n')
            for consideration in considerations:
                if consideration.strip():
                    st.warning(consideration)

def display_fitness_plan(plan_content):
    with st.expander("💪 Your Personalized Fitness Plan", expanded=True):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 🎯 目标")
            st.success(plan_content.get("goals", "Goals not specified"))
            st.markdown("### 🏋️‍♂️ 锻炼计划")
            st.write(plan_content.get("routine", "Routine not available"))

        with col2:
            st.markdown("### 💡 专业提示")
            tips = plan_content.get("tips", "").split('\n')
            for tip in tips:
                if tip.strip():
                    st.info(tip)

def main():
    if 'dietary_plan' not in st.session_state:
        st.session_state.dietary_plan = {}
        st.session_state.fitness_plan = {}
        st.session_state.qa_pairs = []
        st.session_state.plans_generated = False

    st.title("🏋AI 健康与健身规划师Agent🏋️‍♂️")
    # st.markdown("""
    #     <div style='background-color: #00008B; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;'>
    #     Get personalized dietary and fitness plans tailored to your goals and preferences.
    #     Our AI-powered system considers your unique profile to create the perfect plan for you.
    #     </div>
    # """, unsafe_allow_html=True)
    st.markdown("""
    AI 健康与健身规划师Agent是一款个性化的健康和健身Agent，由 Agno AI Agent 框架提供支持。该应用根据用户输入（例如年龄、体重、身高、活动水平、饮食偏好和健身目标）生成量身定制的饮食和健身计划。
    ## 特征
    - **健康Agent和健身Agent**
      - 该应用程序有两个 Agent，分别专门提供饮食建议和健身/锻炼建议。
    - **个性化饮食计划**：
      - 生成详细的膳食计划（早餐、午餐、晚餐和零食）。
      - 包括水合作用、电解质和纤维摄入量等重要考虑因素。
      - 支持各种饮食偏好，如生酮饮食、素食、低碳水化合物等。
    - **个性化健身计划**：
      - 根据健身目标提供定制的锻炼方案。
      - 包括热身、主要锻炼和放松。
      - 包括可操作的健身技巧和进度跟踪建议。
    - **交互式问答**：允许用户询问有关其计划的后续问题。
    """)

    with st.sidebar:
        st.header("🔑 API 配置")
        # gemini_api_key = st.text_input(
        #     "Gemini API Key",
        #     type="password",
        #     help="Enter your Gemini API key to access the service"
        #     ,value=st.session_state.openai_api_key
        # )
        openai_api_key = st.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
        openai_api_model_type = st.text_input("LLM API Model Type",
                                              value=st.session_state.get('openai_api_model_type'))
        openai_api_base_url = st.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))

        if not openai_api_key:
            st.warning("⚠️ Please enter your  API Key to proceed")
            # st.markdown("[Get your API key here](https://aistudio.google.com/apikey)")
            return

        st.success("API Key accepted!")

    if openai_api_key:
        try:
            # gemini_model = Gemini(id="gemini-1.5-flash", api_key=gemini_api_key)
            gemini_model = OpenAILike(id=openai_api_model_type, api_key=openai_api_key,
                               base_url=openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文")
        except Exception as e:
            st.error(f"❌ Error initializing Gemini model: {e}")
            return

        st.header("👤 个人资料")

        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input("年龄", min_value=10, max_value=100, step=1, help="Enter your age")
            height = st.number_input("身高 (cm)", min_value=100.0, max_value=250.0, step=0.1)
            activity_level = st.selectbox(
                "运动水平",
                options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"],
                help="Choose your typical activity level"
            )
            dietary_preferences = st.selectbox(
                "饮食偏好",
                options=["Vegetarian", "Keto", "Gluten Free", "Low Carb", "Dairy Free"],
                help="Select your dietary preference"
            )

        with col2:
            weight = st.number_input("体重 (kg)", min_value=20.0, max_value=300.0, step=0.1)
            sex = st.selectbox("性别", options=["Male", "Female", "Other"])
            fitness_goals = st.selectbox(
                "健身目标",
                options=["Lose Weight", "Gain Muscle", "Endurance", "Stay Fit", "Strength Training"],
                help="What do you want to achieve?"
            )

        if st.button("🎯 生成我的个性化计划", use_container_width=True):
            with st.spinner("Creating your perfect health and fitness routine..."):
                try:
                    dietary_agent = Agent(
                        name="Dietary Expert",
                        role="Provides personalized dietary recommendations",
                        model=gemini_model,
                        instructions=[
                            "Consider the user's input, including dietary restrictions and preferences.",
                            "Suggest a detailed meal plan for the day, including breakfast, lunch, dinner, and snacks.",
                            "Provide a brief explanation of why the plan is suited to the user's goals.",
                            "Focus on clarity, coherence, and quality of the recommendations.",
                        ]
                    )

                    fitness_agent = Agent(
                        name="Fitness Expert",
                        role="Provides personalized fitness recommendations",
                        model=gemini_model,
                        instructions=[
                            "Provide exercises tailored to the user's goals.",
                            "Include warm-up, main workout, and cool-down exercises.",
                            "Explain the benefits of each recommended exercise.",
                            "Ensure the plan is actionable and detailed.",
                        ]
                    )

                    user_profile = f"""
                    Age: {age}
                    Weight: {weight}kg
                    Height: {height}cm
                    Sex: {sex}
                    Activity Level: {activity_level}
                    Dietary Preferences: {dietary_preferences}
                    Fitness Goals: {fitness_goals}
                    """

                    dietary_plan_response = dietary_agent.run(user_profile)
                    dietary_plan = {
                        "why_this_plan_works": "高蛋白、健康脂肪、适量碳水化合物和热量平衡",
                        "meal_plan": dietary_plan_response.content,
                        "important_considerations": """
                        - 补充水分：全天喝大量的水
                        - 电解质：监测钠、钾和镁的含量
                        - 纤维：确保通过蔬菜和水果摄入足够的纤维
                        - 倾听身体的声音：根据需要调整份量
                        """
                    }

                    fitness_plan_response = fitness_agent.run(user_profile)
                    fitness_plan = {
                        "goals": "增强力量、提高耐力并保持整体健康",
                        "routine": fitness_plan_response.content,
                        "tips": """
                        - 定期跟踪进度
                        - 在锻炼之间适当休息
                        - 专注于正确的锻炼方式
                        - 坚持日常锻炼
                        """
                    }

                    st.session_state.dietary_plan = dietary_plan
                    st.session_state.fitness_plan = fitness_plan
                    st.session_state.plans_generated = True
                    st.session_state.qa_pairs = []

                    display_dietary_plan(dietary_plan)
                    display_fitness_plan(fitness_plan)

                except Exception as e:
                    st.error(f"❌ An error occurred: {e}")

        if st.session_state.plans_generated:
            st.header("❓ 对你的计划有疑问吗？")
            question_input = st.text_input("您想知道什么？")

            if st.button("Get Answer"):
                if question_input:
                    with st.spinner("Finding the best answer for you..."):
                        dietary_plan = st.session_state.dietary_plan
                        fitness_plan = st.session_state.fitness_plan

                        context = f"Dietary Plan: {dietary_plan.get('meal_plan', '')}\n\nFitness Plan: {fitness_plan.get('routine', '')}"
                        full_context = f"{context}\nUser Question: {question_input}"

                        try:
                            agent = Agent(model=gemini_model, show_tool_calls=True, markdown=True)
                            run_response = agent.run(full_context)

                            if hasattr(run_response, 'content'):
                                answer = run_response.content
                            else:
                                answer = "Sorry, I couldn't generate a response at this time."

                            st.session_state.qa_pairs.append((question_input, answer))
                        except Exception as e:
                            st.error(f"❌ An error occurred while getting the answer: {e}")

            if st.session_state.qa_pairs:
                st.header("💬 Q&A History")
                for question, answer in st.session_state.qa_pairs:
                    st.markdown(f"**Q:** {question}")
                    st.markdown(f"**A:** {answer}")

if __name__ == "__main__":
    main()
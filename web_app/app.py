import streamlit as st
import subprocess
import json
import os
from pathlib import Path
import time

# 환경 변수 설정
DATA_ROOT = os.getenv('DATA_ROOT', '/app/data')
OUTPUT_ROOT = os.getenv('OUTPUT_ROOT', '/app/results')

# 데이터 경로 설정
SCIENCEQA_DATA_ROOT = os.path.join(DATA_ROOT, 'scienceqa')
TABMWP_DATA_ROOT = os.path.join(DATA_ROOT, 'tabmwp')

# Streamlit 설정
st.set_page_config(
    page_title="Chameleon LLM Demo",
    page_icon="🦎",
    layout="wide"
)

# API 키를 세션 상태에 저장
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""
if 'bing_api_key' not in st.session_state:
    st.session_state.bing_api_key = ""

st.title("🦎 Chameleon LLM Demo")

# 사이드바 설정
st.sidebar.title("Configuration")

# API 키 입력
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=st.session_state.openai_api_key)
bing_api_key = st.sidebar.text_input("Bing Search API Key", type="password", value=st.session_state.bing_api_key)

# API 키 저장
if openai_api_key:
    st.session_state.openai_api_key = openai_api_key
    os.environ["OPENAI_API_KEY"] = openai_api_key
if bing_api_key:
    st.session_state.bing_api_key = bing_api_key
    os.environ["BING_SEARCH_API_KEY"] = bing_api_key

# API 키 상태 표시
if st.session_state.openai_api_key:
    st.sidebar.success("OpenAI API Key is set")
if st.session_state.bing_api_key:
    st.sidebar.success("Bing Search API Key is set")

# 네비게이션
page = st.sidebar.radio("Go to", ["Home", "ScienceQA", "TabMWP", "Results Analysis"])

def check_api_keys():
    if not st.session_state.openai_api_key:
        st.error("Please set your OpenAI API Key in the sidebar")
        return False
    return True

def run_experiment(command, env_vars=None):
    if env_vars is None:
        env_vars = {}
    env = dict(os.environ, **env_vars)
    
    # 실험 시작 시간 기록
    start_time = time.time()
    
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env
    )
    
    # 실험 종료 시간 기록
    end_time = time.time()
    duration = end_time - start_time
    
    # 결과를 JSON 형식으로 변환
    output = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "success": result.returncode == 0,
        "duration": f"{duration:.2f} seconds"
    }
    return output

def display_results(results):
    # 결과를 더 작은 단위로 나누어 표시
    if isinstance(results, dict):
        for key, value in results.items():
            st.subheader(f"{key}:")
            if isinstance(value, (dict, list)):
                st.json(value)
            else:
                st.text(value)
    else:
        st.text(results)

if page == "Home":
    st.header("Welcome to Chameleon LLM Demo")
    st.write("""
    This is a web interface for running and analyzing the Chameleon LLM framework.
    
    You can:
    1. Run ScienceQA experiments
    2. Run TabMWP experiments
    3. Analyze results from notebooks
    """)
    
    if not check_api_keys():
        st.stop()

elif page == "ScienceQA":
    st.header("ScienceQA Experiments")
    
    if not check_api_keys():
        st.stop()
    
    # 모델 선택
    model = st.selectbox(
        "Select Model",
        ["chameleon", "cot"]
    )
    
    # 엔진 선택
    engine = st.selectbox(
        "Select Engine",
        ["gpt-4", "gpt-3.5-turbo"]
    )
    
    # 테스트 데이터 수 선택
    test_number = st.number_input(
        "Number of test examples",
        min_value=1,
        max_value=1000,
        value=10,
        help="Number of examples to process (smaller number = faster execution)"
    )
    
    if st.button("Run Experiment"):
        with st.spinner("Running ScienceQA experiment..."):
            try:
                result = run_experiment(
                    [
                        "python", "run_scienceqa/run.py",
                        "--model", model,
                        "--label", f"{model}_{engine}",
                        "--policy_engine", engine,
                        "--kr_engine", engine,
                        "--qg_engine", engine,
                        "--sg_engine", engine,
                        "--test_split", "test",
                        "--test_number", str(test_number),
                        "--data_root", SCIENCEQA_DATA_ROOT,
                        "--output_root", os.path.join(OUTPUT_ROOT, "scienceqa")
                    ],
                    {"OPENAI_API_KEY": st.session_state.openai_api_key}
                )
                
                if result["success"]:
                    st.success(f"Experiment completed successfully in {result['duration']}!")
                    st.subheader("Output:")
                    display_results(result["stdout"])
                    if result["stderr"]:
                        st.warning("Warnings/Errors:")
                        display_results(result["stderr"])
                else:
                    st.error("Experiment failed!")
                    st.subheader("Error output:")
                    display_results(result["stderr"])
            except Exception as e:
                st.error(f"Error running experiment: {str(e)}")

elif page == "TabMWP":
    st.header("TabMWP Experiments")
    
    if not check_api_keys():
        st.stop()
    
    # 모델 선택
    model = st.selectbox(
        "Select Model",
        ["chameleon", "cot", "pot"]
    )
    
    # 엔진 선택
    engine = st.selectbox(
        "Select Engine",
        ["gpt-4", "gpt-3.5-turbo"]
    )
    
    # 테스트 데이터 수 선택
    test_number = st.number_input(
        "Number of test examples",
        min_value=1,
        max_value=1000,
        value=10,
        help="Number of examples to process (smaller number = faster execution)"
    )
    
    if st.button("Run Experiment"):
        with st.spinner("Running TabMWP experiment..."):
            try:
                result = run_experiment(
                    [
                        "python", "run_tabmwp/run.py",
                        "--model", model,
                        "--label", f"{model}_{engine}",
                        "--test_split", "test",
                        "--policy_engine", engine,
                        "--rl_engine", engine,
                        "--cl_engine", engine,
                        "--tv_engine", engine,
                        "--kr_engine", engine,
                        "--sg_engine", engine,
                        "--pg_engine", engine,
                        "--test_number", str(test_number),
                        "--rl_cell_threshold", "18",
                        "--cl_cell_threshold", "18",
                        "--data_root", TABMWP_DATA_ROOT,
                        "--output_root", os.path.join(OUTPUT_ROOT, "tabmwp")
                    ],
                    {"OPENAI_API_KEY": st.session_state.openai_api_key}
                )
                
                if result["success"]:
                    st.success(f"Experiment completed successfully in {result['duration']}!")
                    st.subheader("Output:")
                    display_results(result["stdout"])
                    if result["stderr"]:
                        st.warning("Warnings/Errors:")
                        display_results(result["stderr"])
                else:
                    st.error("Experiment failed!")
                    st.subheader("Error output:")
                    display_results(result["stderr"])
            except Exception as e:
                st.error(f"Error running experiment: {str(e)}")

elif page == "Results Analysis":
    st.header("Results Analysis")
    
    # 결과 파일 선택
    results_dir = Path(OUTPUT_ROOT)
    available_results = []
    
    for task_dir in results_dir.iterdir():
        if task_dir.is_dir():
            for result_file in task_dir.glob("*.json"):
                available_results.append(str(result_file))
    
    selected_result = st.selectbox(
        "Select Result File",
        available_results
    )
    
    if selected_result and st.button("Load Results"):
        try:
            with open(selected_result, 'r') as f:
                results = json.load(f)
                display_results(results)
        except Exception as e:
            st.error(f"Error loading results: {str(e)}")
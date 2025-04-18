import streamlit as st
import subprocess
import json
import os
from pathlib import Path
import time
import sys
from threading import Thread
from queue import Queue, Empty

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

st.title("🦎 Chameleon Agent Demo")

# 사이드바 설정
st.sidebar.title("Configuration")

# API 키 입력
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=st.session_state.openai_api_key)

# API 키 저장
if openai_api_key:
    st.session_state.openai_api_key = openai_api_key
    os.environ["OPENAI_API_KEY"] = openai_api_key

# API 키 상태 표시
if st.session_state.openai_api_key:
    st.sidebar.success("OpenAI API Key is set")

# 네비게이션
page = st.sidebar.radio("Go to", ["Home", "ScienceQA", "TabMWP", "Results Analysis"])

def check_api_keys():
    if not st.session_state.openai_api_key:
        st.error("OpenAI API를 입력해주십시오.")
        return False
    return True

def stream_process_output(process, queue):
    """프로세스의 출력을 큐에 저장하는 함수"""
    for line in iter(process.stdout.readline, b''):
        queue.put(('stdout', line.decode('utf-8')))
    for line in iter(process.stderr.readline, b''):
        queue.put(('stderr', line.decode('utf-8')))
    process.stdout.close()
    process.stderr.close()

def run_experiment(command, env_vars=None):
    if env_vars is None:
        env_vars = {}
    env = dict(os.environ, **env_vars)
    
    # 출력을 표시할 placeholder 생성
    output_area = st.empty()
    output_text = []
    
    # 프로세스 시작
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        bufsize=1,
        universal_newlines=False  # 바이너리 모드 사용
    )
    
    # 출력을 저장할 큐 생성
    output_queue = Queue()
    
    # 출력을 읽는 스레드 시작
    thread = Thread(target=stream_process_output, args=(process, output_queue))
    thread.daemon = True
    thread.start()
    
    # 실시간 출력 처리
    while True:
        try:
            # 큐에서 출력 읽기
            stream_name, line = output_queue.get(timeout=0.1)
            
            # 출력 저장 및 표시
            if stream_name == 'stderr':
                output_text.append(f"Error: {line}")
            else:
                output_text.append(line)
            
            # 현재까지의 모든 출력 표시
            output_area.code(''.join(output_text))
            
        except Empty:
            # 프로세스가 종료되었는지 확인
            if process.poll() is not None:
                break
    
    # 프로세스 종료 대기
    process.wait()
    
    # 결과 반환
    return {
        "returncode": process.returncode,
        "success": process.returncode == 0,
        "output": ''.join(output_text)
    }

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
    st.header("Welcome to Chameleon Agent Demo")
    st.write("""
    
    해당 사이트는 DDPS 연구실 지원을 위한 Chameleon Agent Demo Site입니다.
    
    좀 더 커스텀하여 제어를 원하시면 아래의 github repo에서 Dockerfile.local을 실행하여 주십시오.
    https://github.com/DevMinGeonPark/chameleon-llm-demo
    
    - 원본 코드의 중요 폴더, 파일 별 역활
        - run_scienceqa: scienceqa 실험 실행
        - run_tabmwp: tabmwp 실험 실행
        - notebooks: 실험 결과 시각화
        - data: 실험 데이터 및 설치 bash script
        - results: 실험 결과
        - utilities.py: 유틸리티 코드 파일
        - task/model.py: 모델 코드 파일
        - task/run.py: 실험 실행 코드 파일
        - task/demos: 자연어로 된 Prompt files
        
    - mingeon fork git의 특수 파일
        - Dockerfile.local: /bin/bash로 진입하여 자유로운 실험을 할 수 있는 환경 구성
        - Dockerfile: 웹 애플리케이션 실행 파일 빌드 및 실행
        - requirements.txt: 실험에 필요한 패키지 목록 구성
        - render.yaml: 웹 애플리케이션 실행 파일 빌드 및 실행 파일 실행
        
    실행 방법:
    - Docker 이미지 빌드:
     docker build -t chameleon-agent-demo .
     
    - Docker 컨테이너 실행:
     docker run -it --rm \
        -p 8501:8501 \
        -p 8000:8000 \
        -e DATA_ROOT=/app/data \
        -e OUTPUT_ROOT=/app/results \
        chameleon-agent-demo
        
    - 진입 후 테스트 방법
    1. scienceqa 테스트
        - 모델 선택: chameleon, cot
        - 엔진 선택: gpt-4, gpt-3.5-turbo
        - 테스트 데이터 수 선택: 10, 100, 1000
        - 실험 실행
        
        - GPT-4를 사용한 10개 test 실험
        명령어 : python run_scienceqa/run.py \ 
                    --model chameleon \
                    --label chameleon_gpt4 \
                    --policy_engine gpt-4 \
                    --kr_engine gpt-4 \
                    --qg_engine gpt-4 \
                    --sg_engine gpt-4 \
                    --test_split test \
                    --test_number 10 \
        - 이외에는 공식 문서를 참고하십시오.
        
    2. tabmwp 테스트
        - 모델 선택: chameleon, cot
        - 엔진 선택: gpt-4, gpt-3.5-turbo
        - 테스트 데이터 수 선택: 10, 100, 1000
        - 실험 실행
        
        - GPT-4를 사용한 10개 test 실험
        명령어 : python run_tabmwp/run.py \
                --model chameleon \
                --label chameleon_gpt4 \
                --test_split test \
                --policy_engine gpt-4 \
                --rl_engine gpt-4 \
                --cl_engine gpt-4 \
                --tv_engine gpt-4 \
                --kr_engine gpt-4 \
                --sg_engine gpt-4 \
                --pg_engine gpt-4 \
                --test_number -1 \
                --rl_cell_threshold 18 \
                --cl_cell_threshold 18
        
    
    3. 결과 분석
        
    You can:
    1. 실험을 실행하세요.
    2. 실험 결과는 /app/results 폴더에 저장됩니다.
    3. 필요하다면, 각 폴더의 evaluate.py를 수정하여 결과를 받으세요.
    4. results_viewer_scienceqa.ipynb를 적절히 수정하면 시각화된 형태를 볼 수 있습니다.
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
        value=10
    )
    
    if st.button("Run Experiment"):
        try:
            st.info("실험을 시작합니다...")
            
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
                    "--output_root", os.path.join(OUTPUT_ROOT, "scienceqa"),
                    "--debug"  # 디버그 모드 활성화
                ],
                {"OPENAI_API_KEY": st.session_state.openai_api_key}
            )
            
            if result["success"]:
                st.success("실험이 완료되었습니다!")
            else:
                st.error("실험 실행 중 오류가 발생했습니다.")
                st.error(result["output"])
                
        except Exception as e:
            st.error(f"Error running experiment: {str(e)}")
            st.error(f"상세 에러: {sys.exc_info()}")

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
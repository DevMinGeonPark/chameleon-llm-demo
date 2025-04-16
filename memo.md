Chameleon 프로젝트에서 공식적으로 제공하는 **도구 호출 비율(Percentage of Called Tools) 그래프**는 실제로 코드로 직접 뽑아볼 수 있습니다. 다만, 기본적으로 제공되는 `results_viewer_scienceqa.ipynb`에는 이 그래프 시각화 코드가 포함되어 있지 않으나, 결과 파일(`results/scienceqa/[label]_[split]_cache.jsonl`)을 활용해 아래와 같이 직접 구현할 수 있습니다[2][4].

---

## 도구 호출 비율(Percentage of Called Tools) 그래프 시각화 코드 예시

아래 코드는 ScienceQA 결과 파일에서 각 도구(모듈)가 호출된 비율을 계산해 막대그래프로 시각화하는 예시입니다.

```python
import json
import matplotlib.pyplot as plt

# 결과 파일 경로 (실제 경로에 맞게 수정)
result_file = 'results/scienceqa/chameleon_gpt4_test_cache.jsonl'

# 사용할 도구(모듈) 목록
tools = [
    "knowledge_retrieval:output",
    "bing_search:output",
    "text_detector:output",
    "image_captioner:output",
    "solution_generator:output",
    "query_generator:output"
]

# 도구별 호출 횟수 카운트
tool_counts = {tool: 0 for tool in tools}
total = 0

with open(result_file, 'r') as f:
    for line in f:
        result = json.loads(line)
        total += 1
        for tool in tools:
            if tool in result:
                tool_counts[tool] += 1

# 비율 계산
tool_percentages = {tool: 100 * count / total for tool, count in tool_counts.items()}

# 시각화
plt.figure(figsize=(10, 6))
plt.bar(tool_percentages.keys(), tool_percentages.values(), color='skyblue')
plt.ylabel('Percentage of Called Tools (%)')
plt.title('Percentage of Called Tools in Chameleon (ScienceQA)')
plt.xticks(rotation=30)
plt.ylim(0, 100)
plt.show()
```

---

## 설명

- **결과 파일**: Chameleon 실행 결과가 저장된 `.jsonl` 파일을 사용합니다.
- **도구 목록**: 논문 및 공식 페이지에 언급된 주요 도구(knowledge_retrieval, bing_search 등)를 대상으로 합니다.
- **카운트 및 비율**: 각 도구가 한 샘플에서 한 번이라도 호출되었으면 카운트합니다. 전체 샘플 대비 비율(%)로 변환합니다.
- **시각화**: matplotlib을 이용해 막대그래프로 도구별 호출 비율을 보여줍니다.

---

## 참고

- 실제 Chameleon 공식 저장소에는 transition 그래프, 도구 사용 빈도 그래프 등 분석용 노트북(`notebooks/transition_[TASK]_[Model]_Engine.ipynb`)이 별도로 제공됩니다. 이 노트북을 실행하면 논문/공식 페이지와 동일한 그래프를 얻을 수 있습니다[2][4].
- 위 코드는 ScienceQA 기준 예시이며, TabMWP 등 다른 태스크에도 동일하게 적용할 수 있습니다.

---

# TransportationLink API: 리스크 예측 기반 최적 경험 동선 분석 시스템
## Version 1.0 - Tier 3 Licensing Candidate
**작성 목적:** 본 문서는 bosstak의 핵심 기술인 `TransportationLink` API가 단순한 지리적 최단 경로 탐색을 넘어, **현지 교통 혼잡도 리스크와 환승 예측 시간을 통합하여 경험적 대비점을 극대화하는 동선 분석 솔루션**임을 입증합니다. 잠재 고객사(IT 개발팀)의 시스템 설계 및 기술 도입 검토를 위해 작성되었습니다.

---

### 🚀 1. 개요 및 핵심 가치 (Core Value Proposition)

#### 1.1 문제 정의 (Problem Statement)
기존 경로 탐색 솔루션은 주로 Euclidean Distance (유클리드 거리) 또는 Haversine Formula(지구 곡률 기반 최단 직선 거리)에 의존하여, 실제 이동 시 발생하는 **'비효율적 시간 손실'**을 간과합니다. 특히 대중교통 환경에서는 다음 변수들이 누적되어 경험의 질을 급격히 저하시킵니다:
1.  **환승 지연 리스크 (Transfer Delay Risk):** 환승역에서의 예상치 못한 대기 및 이동 시간.
2.  **현지 혼잡도 리스크 (Local Congestion Risk):** 특정 시간대/지역의 예측 불가한 교통 정체 또는 인파 밀집.

#### 1.2 솔루션 개요 (Solution Overview)
`TransportationLink` API는 Graph Theory 기반의 경로 탐색 알고리즘을 활용하며, 전통적인 비용 함수 $Cost_{traditional}$ 대신 다음과 같은 **가중치 최적화된 총 경험 비용 함수** $\text{TotalExperienceCost}$를 최소화하는 동선 시나리오를 제안합니다.

$$\min \left( \sum_{i=1}^{N-1} (T_{travel, i} + T_{transfer, i} + R_{congestion, i}) \right)$$

*   $N$: 총 경유지(Spot)의 개수
*   $T_{travel}$: Spot $i$와 $i+1$ 간 순수 이동 시간.
*   $T_{transfer}$: 환승역에서의 예상 대기 및 전환 시간.
*   $R_{congestion}$: 현지 교통 혼잡도 리스크 가중치 (핵심 지표).

---

### 📐 2. 데이터 스키마 정의 (Schema Definition)

#### 2.1 입력 데이터 스키마 (`Input_Spots`)
사용자 또는 시스템이 API에 제공해야 하는 Spot 정보의 표준화된 JSON Schema입니다. 모든 경유지는 이 포맷을 따릅니다.

| 필드명 | 타입 | 설명 | 제약 조건 (Constraint) |
| :--- | :--- | :--- | :--- |
| `spot_id` | String | 고유 식별자 (예: 'BPA-001') | Not Null, Unique |
| `name` | String | 명소 이름 (예: 감천문화마을) | Max 50 chars |
| `lat` | Float | 위도 좌표 (Decimal Degrees) | -90.0 $\le$ lat $\le$ 90.0 |
| `lon` | Float | 경도 좌표 (Decimal Degrees) | -180.0 $\le$ lon $\le$ 180.0 |
| `suggested_visit_time` | Interval | 권장 체류 시간 (예: '2h 30m') | Must be positive interval |

#### 2.2 출력 결과 스키마 (`Output_Scenario`)
API가 반환하는 최적화된 동선 시나리오 보고서의 JSON Schema입니다. 최소 3개의 대안적 시나리오를 제공합니다.

```json
{
  "scenarios": [
    {
      "scenario_id": "S1",
      "optimization_strategy": "Flow-Optimized (Low Risk)",
      "total_estimated_time": {
        "value": 320, // Minutes
        "breakdown": {
          "travel_minutes": 250,
          "transfer_minutes": 40,
          "risk_buffer_minutes": 30
        }
      },
      "route_sequence": [
        {"spot_id": "BPA-001", "arrival_time": "...", "departure_time": "..." },
        {"spot_id": "BPA-002", "transfer_details": {"station": "환승역명", "predicted_delay": 8}}
        // ... 나머지 Spot들
      ],
      "score_metrics": {
        "risk_score": 0.75, // [0.0 (최적) ~ 1.0 (위험)]
        "experience_max_diff": "Drama Transition Point: A -> B"
      }
    }
  ],
  "metadata": {
    "timestamp": "2026-08-22T15:00:00Z",
    "api_version": "1.2.0"
  }
}
```

---

### ⚙️ 3. 핵심 알고리즘 상세 정의 (Algorithmic Deep Dive)

#### 3.1 환승 예측 시간 모델 ($T_{transfer}$)
환승 지점($S_{trans}$), 이전 Spot($S_A$), 다음 Spot($S_B$) 간의 이동을 가정합니다. 순수 이동 시간이 아닌, 실제 사람이 경험하는 **'여유 시간(Buffer Time)'** 개념이 도입됩니다.

$$T_{transfer} = \text{MinTravelTime}(S_A \to S_{trans}) + W_{\text{Exit}} + C_{\text{AvgWait}} + T_{\text{buffer}}$$

*   $\text{MinTravelTime}$: $S_A$에서 환승역까지의 최단 대중교통 이동 시간 (API 조회).
*   $W_{\text{Exit}}$: 해당 역/출구에서의 평균 예상 도보 이탈 시간 (하드코딩 또는 지역별 데이터 테이블 참조, $\approx 5-10 \text{ minutes}$).
*   $C_{\text{AvgWait}}$: 평균적인 대중교통 배차 간격 기반의 최대 대기 시간 예측.
*   $T_{\text{buffer}}$: **핵심 요소.** 경로 최적화에 필요한 의도적인 최소 여유 시간 (경험 대비점 극대화를 위해 5분 이상 할당).

#### 3.2 현지 교통 혼잡도 리스크 측정 공식 ($R_{congestion}$)
이는 단순한 '교통 체증 지수'를 넘어, **데이터 기반의 예측 불가능성**을 수치화합니다. $R_{congestion}$는 [0.0 (최적) ~ 1.0 (매우 위험)] 사이의 값을 가집니다.

$$R_{\text{congestion}}(S_i, T_{\text{time}}) = \frac{W_{P}(\text{Day}) \times V_{\text{density}}(\text{Time})}{\alpha + E(\text{Seasonality})} + \beta$$

*   $W_{P}(\text{Day})$: 요일별/시간대별 예측 가중치 (예: 주말 오후 2시 $\rightarrow$ 높은 $W_P$).
*   $V_{\text{density}}(\text{Time})$: 시간당 평균 유동 인구 밀도 지수 (실측 데이터 기반).
*   $E(\text{Seasonality})$: 계절성 변수. 관광 성수기($\text{Summer}$)는 $E$ 값을 높여 전반적인 리스크를 상향 조정합니다. ($\alpha$는 정규화 상수, $\beta$는 기본 오차율).

> **[기술적 해석]** 이 공식은 이동 자체의 어려움(교통)과 시간/계절에 따른 외부 변수(인파)를 곱하여 *누적 리스크*로 정의함으로써, 단순 경로가 아닌 '안정적인 경험 흐름'을 보장하는 데 초점을 맞춥니다.

---
**[검증 및 테스트]**

본 백서의 모든 개념과 공식은 내부적으로 구축된 `TransportationLink` API 로직에 기반합니다. 이 기술력을 외부 파트너에게 투명하게 공개하기 위해, 별도의 **"API 사용 매뉴얼 (Swagger/OpenAPI)"** 문서를 준비하여 개발팀이 즉시 참조할 수 있도록 제공해야 합니다.

<reveal_in_explorer path="technical_whitepaper_v1.md"/>
# project_MPP

3차원 벤투리형 레이싱카 언더플로어의 수직 진동에 따른 공력 히스테리시스와 포포이징 불안정 조건을 연구하기 위한 재현 가능한 CFD 프로젝트다.

이 저장소의 첫 번째 마일스톤은 2차원 moving-ground 정상 RANS 기준해석이다. 이후 강제 heave URANS, 3차원 언더플로어, 1자유도 구조동역학 결합 순서로 확장한다. 실제 F1 차량을 예측하는 것이 아니라 단순화한 형상에서 공력 히스테리시스가 진동에 에너지를 공급하는 조건을 규명하는 것이 목표다.

## 연구 질문

- 다운포스가 최대가 된 뒤 붕괴하는 임계 지상고는 어디인가?
- 동일 지상고에서 상승·하강 공기력이 달라지는 조건은 무엇인가?
- 한 주기 공력 일 `W_aero = integral(Fz dz)`의 부호가 언제 양수가 되는가?
- 공력 에너지 공급이 서스펜션 감쇠 손실을 초과하는 임계 유속과 감쇠비는 얼마인가?
- 측면 누설과 가장자리 와류 때문에 2차원과 3차원 결과가 얼마나 달라지는가?

## 저장소 구조

```text
config/                 연구 및 솔버 매개변수
docs/                   연구계획, 부호 규약, 검증 절차
geometry/               형상 원본과 향후 CAD 자산
templates/gmsh/         매개변수화 Gmsh 템플릿
templates/su2/          SU2 설정 템플릿
scripts/                케이스 생성·실행·후처리 도구
cases/                  생성된 계산 케이스(대용량 결과 제외)
results/                통합 표와 그림
tests/                  자동화 코드 단위시험
```

## 빠른 시작

요구 사항은 Python 3.10+, Gmsh 4.x, SU2 8.x다. 현재 검증 기준 버전은 Gmsh 4.15.2와 SU2 8.5.0이다. Python 패키지는 다음과 같이 설치한다.

```powershell
python -m pip install -r requirements.txt
```

정상 2차원 지상고 스윕 케이스를 생성한다.

```powershell
python scripts/setup_cases.py --study config/study.yaml
python scripts/check_geometry.py
```

Gmsh와 SU2 실행 파일이 PATH에 있을 때 계산을 순차 실행한다.

```powershell
python scripts/run_cases.py --manifest cases/case_manifest.csv --mesh --case steady2d_h_0p1_medium
python scripts/run_cases.py --manifest cases/case_manifest.csv --solve --case steady2d_h_0p1_medium
```

계산 완료 후 결과를 모은다.

```powershell
python scripts/postprocess_cases.py --manifest cases/case_manifest.csv
python scripts/postprocess_underfloor.py steady2d_h_0p3_medium
```

기존 `history.csv`, `su2.log`, `forces_breakdown.dat`가 있으면 다음 solve 전에 케이스의 `runs/<timestamp>/`로 자동 보관된다. 의도적으로 덮어쓸 때만 `--no-archive`를 사용한다.

## 현재 상태

- 연구 범위, 부호 규약, 무차원 변수 정의 완료
- 2차원 벤투리 수축부–목–디퓨저 형상과 물리 경계 태그 구축
- 하부·상부·전단·후단 차체 경계를 분리해 언더플로어 압력 기여를 별도 분석
- 3수준 격자 및 정상 RANS 케이스 생성·실행 인터페이스 구축
- SU2 8.5.0 기준 `h/L=0.10` 정상 RANS 실행 완료; 2차 정확도 해는 미수렴으로 provisional 판정
- `h/L=0.30` medium은 다음 지상고 선별용 screening 결과 확보
- `h/L=0.20` medium은 2,000회 2차 정확도에서도 힘이 표류해 provisional 판정
- `h/L=0.15` medium도 힘이 표류해 provisional 판정; 예비 다운포스 최대 구간은 `0.10 < h/L < 0.15`
- 다음 단계: `h/L=0.125` 적응형 정상 선별점 추가와 낮은 지상고 고정형상 URANS 준비

자세한 실행 순서는 [연구계획](docs/research_plan.md)과 [검증 절차](docs/verification_plan.md)를 따른다.

# AutoCaption Pro - 개발 명세서

## 📌 프로젝트 개요

**프로그램명:** AutoCaption Pro  
**목적:** DaVinci Resolve 타임라인의 SRT 자막을 디자인된 Text+ 템플릿으로 자동 변환  
**판매용 제품**

---

## 🎯 핵심 기능

타임라인의 자막 트랙(ST1)에 있는 자막들을 읽어서,  
Power Bin에 저장된 Text+ 템플릿을 적용한 클립으로 변환하여  
비디오 트랙 최상위에 자동 배치

---

## 🖥️ 개발 환경

| 항목 | 내용 |
|------|------|
| DaVinci Resolve | 20.2.3 (무료 버전) |
| 언어 | Python 3 |
| 실행 방식 | Resolve 내부 Scripts 메뉴 (외부 독립 실행 불가) |
| OS | Windows |
| 개발도구 | Cursor + Claude Code |

---

## 📥 설치 방법

### 1단계: 스크립트 파일 배치

```
C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility\
└── autocaption_pro.py
```

### 2단계: DaVinci Resolve 재시작

스크립트 파일을 추가한 후 Resolve를 완전히 종료하고 다시 실행해야 메뉴에 나타납니다.

### 3단계: 실행

**Workspace > Scripts > Utility > autocaption_pro**

---

## ⚠️ 중요: 실행 방식

```
✅ 이렇게 실행: Workspace > Scripts > Utility > autocaption_pro
✅ 이렇게 실행: Fusion > Scripts > Utility > autocaption_pro

❌ 이렇게는 안 됨: 외부 터미널에서 python autocaption_pro.py
   → 무료 버전에서는 외부 독립 실행이 지원되지 않습니다
```

---

## 📂 Power Bin 구조

```
Power Bins
└── Master
    └── AutoCaption Pro
        ├── 템플릿1.setting
        ├── 템플릿2.setting
        └── ... (Text+ 템플릿들이 바로 여기에 위치)
```

**템플릿 제작 권장사항:**
- Text+ 노드 이름을 "TextPlus"로 통일 (자동 인식 용이)
- 가능한 단순한 구조로 제작 (복잡한 중첩 구조 피하기)
- 텍스트 속성이 StyledText로 설정되어 있어야 함

---

## 🔄 워크플로우

```
[1] Resolve 연결
     ↓
[2] 현재 프로젝트/타임라인 가져오기
     ↓
[3] 자막 트랙(ST1)에서 정보 추출
    - 시작 시간 (프레임)
    - 끝 시간 (프레임)  
    - 자막 텍스트
     ↓
[4] Power Bin에서 Text+ 템플릿 찾기
    - 경로: Master > AutoCaption Pro
     ↓
[5] 각 자막마다 반복:
    - Text+ 템플릿을 타임라인에 추가
    - Fusion Composition 접근
    - Text+ 노드의 StyledText 속성 변경
    - duration(길이) 및 위치 설정
     ↓
[6] 비디오 트랙 최상위에 배치
     ↓
[7] 완료 메시지 출력
```

---

## ⚙️ 설정 파라미터

스크립트 상단에 위치 (사용자가 쉽게 수정 가능)

```python
# ========== 설정 (여기만 수정하세요) ==========
PROGRAM_NAME = "AutoCaption Pro"
TEMPLATE_FOLDER = "AutoCaption Pro"      # Power Bin 내 폴더명
TEMPLATE_NAME = ""                        # 사용할 Text+ 템플릿 이름 (비워두면 첫 번째 템플릿 사용)
SUBTITLE_TRACK_INDEX = 1                  # ST1 = 1번
OUTPUT_TRACK = "top"                      # "top" = 최상위, 숫자 = 특정 트랙
# =============================================
```

---

## 📋 필요한 API 함수들

### Resolve 연결
```python
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
```

### 프로젝트/타임라인
```python
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
timeline = project.GetCurrentTimeline()
```

### 자막 트랙 접근
```python
# 자막 트랙의 클립들 가져오기
subtitle_clips = timeline.GetItemListInTrack("subtitle", 1)
```

### 클립 정보 추출
```python
for clip in subtitle_clips:
    start_frame = clip.GetStart()
    end_frame = clip.GetEnd()
    duration = clip.GetDuration()
    
    # 자막 텍스트 추출 (여러 방법 시도)
    text = clip.GetName()  # 기본 방법
    # 또는 clip.GetClipProperty(), clip.GetMetadata() 등
```

### Power Bin 접근
```python
mediaPool = project.GetMediaPool()
rootFolder = mediaPool.GetRootFolder()
# 재귀적으로 폴더 탐색
```

### 타임라인에 클립 추가
```python
media_pool.AppendToTimeline([{
    "mediaPoolItem": template,
    "startFrame": 0,
    "endFrame": duration - 1,
    "trackIndex": target_track,
    "recordFrame": start_position
}])
```

### Fusion Composition 접근
```python
fusion_comp = clip.GetFusionCompByIndex(1)
text_node = fusion_comp.FindToolByID("TextPlus")
text_node.SetInput("StyledText", new_text)
```

---

## ⚠️ 제한사항 및 알려진 이슈

### 무료 버전 관련
- ✅ 모든 핵심 기능이 무료 버전에서 작동
- ✅ Resolve 내부 Scripts 메뉴에서 실행
- ❌ 외부 터미널에서 독립 실행 불가
- ❌ 외부 파이프라인 연동 불가 (렌더팜 등)

### API 관련
- 🔍 자막 텍스트 추출 방법은 Resolve 버전마다 다를 수 있음
  - GetName(), GetClipProperty(), GetMetadata() 등 여러 방법 시도 필요
- 🔍 Text+ 노드 이름은 템플릿마다 다를 수 있음
  - "TextPlus", "Text+", "Text", "Template" 등 가능
- 🔍 일부 Fusion Composition 접근이 안 될 수 있음
  - 템플릿 구조에 따라 다름

### 권장 사항
- Text+ 템플릿의 주 텍스트 노드 이름을 "TextPlus"로 통일
- 템플릿은 가능한 단순하게 제작 (복잡한 중첩 구조 피하기)
- 첫 실행 시 테스트용 자막 3-5개로 테스트

---

## 🧪 테스트 시나리오

### 1. 기본 테스트
- 자막 3개짜리 간단한 타임라인
- 템플릿 1개로 테스트
- 각 단계별 로그 확인

### 2. 예외 처리 테스트
- 자막 트랙이 없는 경우
- Power Bin에 템플릿이 없는 경우
- 빈 자막이 있는 경우
- 자막 트랙 번호가 잘못된 경우

### 3. 성능 테스트
- 자막 10개 처리
- 자막 50개 처리
- 자막 100개 이상 처리

### 4. 호환성 테스트
- 다양한 Text+ 템플릿으로 테스트
- 다른 프레임레이트 타임라인 (24fps, 30fps, 60fps)
- 다양한 자막 길이 (짧은/중간/긴 자막)

---

## 📁 파일 구조

```
AutoCaption Pro/
├── autocaption_pro.py           # 메인 스크립트
├── AutoCaption_Pro_명세서.md    # 개발 명세서 (이 파일)
└── README.md                    # 사용자용 설명서 (배포용)
```

---

## 🚀 향후 확장 가능 기능

- [ ] GUI 인터페이스 (tkinter 또는 PySide)
- [ ] 템플릿 선택 UI
- [ ] 여러 자막 트랙 지원 (ST1, ST2, ST3...)
- [ ] 자막 스타일별 다른 템플릿 적용 (키워드 기반)
- [ ] 배치 처리 (여러 타임라인)
- [ ] 진행률 표시 (프로그레스 바)
- [ ] 로그 파일 자동 생성
- [ ] 되돌리기(Undo) 기능
- [ ] 템플릿 프리셋 관리

---

## 📝 참고 자료

### DaVinci Resolve Scripting 문서
- 경로: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\README.txt`
- Python API 모듈: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules`

### 커뮤니티 리소스
- Blackmagic Forum - Scripting Section
- DaVinci Resolve API 비공식 문서
- GitHub - Resolve Scripts 예제들

---

## 📊 경쟁 제품 분석: Snap Captions

### Snap Captions v1.5 (Lua)
- **문제점**: Resolve 20.x에서 무료 버전 사용 불가
- **원인**: `timeline:AddTrack("video")` 메서드가 Studio 전용
- **팝업**: "You have reached a limitation with DaVinci Resolve"

### 핵심 차이점

| 기능 | Snap Captions (Lua) | AutoCaption Pro (Python) |
|------|---------------------|--------------------------|
| 언어 | Lua | Python 3 |
| GUI | 복잡한 UI | 간단한 콘솔 (또는 향후 GUI) |
| 트랙 생성 | `AddTrack()` 사용 (Studio 전용) | **기존 트랙 활용** (무료 버전 가능) |
| 템플릿 위치 | Media Pool의 "Snap Captions" 폴더 | Power Bin의 "AutoCaption Pro" 폴더 |
| Text+ 수정 | `GetToolList(false, "TextPlus")` | `FindToolByID("TextPlus")` |

### Snap Captions의 작동 방식 (참고용)

```lua
-- 1. 자막 데이터 추출
local subtitle_data = GetSubtitleData(track_index, in_frame, out_frame)
-- subtitle_data[i]["text"], ["start"], ["end"], ["duration"]

-- 2. 새 비디오 트랙 추가 (⚠️ Studio 전용!)
local track_created = timeline:AddTrack("video")

-- 3. 템플릿 복제 및 배치
for i, subtitle in ipairs(subtitle_data) do
    local newClip = {}
    newClip["mediaPoolItem"] = text_clip
    newClip["startFrame"] = 0
    newClip["endFrame"] = subtitle["duration"] - 1
    newClip["trackIndex"] = video_track
    newClip["recordFrame"] = subtitle["start"]
    
    local timelineItem = mediaPool:AppendToTimeline({newClip})[1]
    
    -- 4. Fusion Comp 접근하여 텍스트 변경
    local comp = timelineItem:GetFusionCompByIndex(1)
    local text_plus_tools = comp:GetToolList(false, "TextPlus")
    text_plus_tools[1]:SetInput("StyledText", subtitle["text"])
end
```

### 🔑 무료 버전 제한 우회 전략

#### ❌ Studio 전용 기능 (사용 불가)
```python
# 이렇게 하면 팝업 뜸
timeline.AddTrack("video")
```

#### ✅ 무료 버전 호환 방법
```python
# 방법 1: 기존 트랙 번호 활용
track_count = timeline.GetTrackCount("video")
target_track = track_count  # 기존 최상위 트랙 사용
# 또는
target_track = track_count + 1  # 자동으로 새 트랙 생성됨 (AppendToTimeline 사용 시)

# 방법 2: 사용자에게 수동 트랙 생성 요청
print("⚠️ 새 비디오 트랙을 수동으로 추가하고 다시 실행하세요")
```

### 개선 포인트

AutoCaption Pro는 Snap Captions의 장점을 유지하면서 **무료 버전 호환성**을 확보:

1. ✅ **무료 버전 작동**: AddTrack() 사용 안 함
2. ✅ **간단한 사용법**: 콘솔 기반, GUI 없음 (빠른 실행)
3. ✅ **Python 기반**: 더 많은 라이브러리, 확장성
4. ✅ **명확한 에러 메시지**: 디버깅 용이

---

## 🔍 디버깅 팁

### 콘솔 창 확인
```
Workspace > Console
```
- 모든 print() 출력이 여기 표시됨
- 에러 메시지 확인 가능

### 단계별 테스트
```python
# 각 함수를 개별적으로 테스트
resolve = get_resolve()
project, timeline = get_current_timeline(resolve)
subtitles = get_subtitle_clips(timeline, 1)
print(subtitles)  # 결과 확인
```

### 자주 발생하는 에러
1. **"Module not found"**: Resolve 내부에서 실행 안 함
2. **"Cannot connect to Resolve"**: Resolve가 실행 안 됨
3. **"Timeline not found"**: 타임라인이 열려있지 않음
4. **"Template folder not found"**: Power Bin 구조 확인
5. **"Studio limitation popup"**: AddTrack() 같은 Studio 전용 기능 사용함

---

## 📧 지원 및 문의

개발 중 문제가 발생하면:
1. Console 창에서 에러 메시지 확인
2. 명세서의 "디버깅 팁" 섹션 참고
3. 단계별로 나누어 테스트
4. 커뮤니티 포럼 검색

---

**버전:** 1.0  
**최종 수정:** 2024-11-26  
**개발자:** AutoCaption Pro Team

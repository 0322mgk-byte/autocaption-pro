#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AutoCaption Pro v1.0
====================
DaVinci Resolve 자막 → Text+ 템플릿 자동 변환

[사용 방법]
1. Power Bins > Master > AutoCaption Pro 폴더 클릭 (또는 Media Pool에 복사)
2. Workspace > Scripts > Utility > autocaption_pro 실행
3. 완료!

[요구사항]
- DaVinci Resolve 20.2+ (무료 버전 지원)
- AutoCaption Pro 폴더에 Text+ 템플릿 준비
- 타임라인에 자막 트랙(ST1) 준비
"""

# ============================================================================
# 설정
# ============================================================================
SUBTITLE_TRACK = 1  # ST1 = 1


def get_resolve():
    """Resolve 연결"""
    try:
        resolve = fusion.GetResolve()
        if resolve:
            return resolve
    except:
        pass

    try:
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")
        if resolve:
            return resolve
    except:
        pass

    print("ERROR: Resolve에 연결할 수 없습니다")
    print("Workspace > Scripts > Utility 에서 실행하세요")
    return None


def get_timeline(resolve):
    """현재 타임라인 가져오기"""
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    timeline = project.GetCurrentTimeline()

    if not timeline:
        print("ERROR: 타임라인을 열어주세요")
        return None, None

    print(f"Timeline: {timeline.GetName()}")
    return project, timeline


def get_subtitles(timeline):
    """자막 트랙에서 자막 정보 추출"""
    items = timeline.GetItemListInTrack("subtitle", SUBTITLE_TRACK)

    if not items:
        print(f"ERROR: ST{SUBTITLE_TRACK}에 자막이 없습니다")
        return []

    subtitles = []
    for item in items:
        subtitles.append({
            "text": item.GetName(),
            "start": item.GetStart(),
            "duration": item.GetDuration()
        })

    print(f"Subtitles: {len(subtitles)}개 발견")
    return subtitles


def find_template_folder(project):
    """현재 선택된 폴더를 템플릿 폴더로 사용"""
    media_pool = project.GetMediaPool()
    current = media_pool.GetCurrentFolder()

    if not current:
        print("ERROR: 폴더를 선택해주세요")
        return None

    folder_name = current.GetName()

    # "AutoCaption" 포함 여부 체크 (대소문자 무시)
    if "autocaption" not in folder_name.lower():
        print(f"\n⚠️  잘못된 폴더가 선택되었습니다")
        print(f"현재 선택: {folder_name}")
        print(f"\n다음 중 하나를 선택하고 다시 실행하세요:")
        print(f"  1) Power Bins > Master > AutoCaption Pro 폴더 선택")
        print(f"  2) Media Pool에 AutoCaption Pro 폴더 복사 후 선택\n")
        return None

    print(f"Template folder: {folder_name}")
    return current


def get_template(folder):
    """폴더에서 첫 번째 템플릿 가져오기"""
    clips = folder.GetClipList()
    if not clips:
        print("ERROR: 템플릿 폴더가 비어있습니다")
        return None

    print(f"Template: {clips[0].GetName()}")
    return clips[0]


def process_subtitles(project, timeline, subtitles, template):
    """자막을 Text+ 클립으로 변환"""
    media_pool = project.GetMediaPool()
    track = timeline.GetTrackCount("video") + 1

    print(f"Output: V{track}")
    print("Processing...")

    success = 0
    for i, sub in enumerate(subtitles):
        clip_info = {
            "mediaPoolItem": template,
            "startFrame": 0,
            "endFrame": sub["duration"],
            "trackIndex": track,
            "recordFrame": sub["start"]
        }

        items = media_pool.AppendToTimeline([clip_info])
        if not items:
            print(f"  [{i+1}] FAIL: 추가 실패")
            continue

        clip = items[0]

        comp = clip.GetFusionCompByIndex(1)
        if not comp:
            print(f"  [{i+1}] FAIL: Fusion Comp 없음")
            continue

        tools = comp.GetToolList(False, "TextPlus")
        if not tools:
            print(f"  [{i+1}] FAIL: TextPlus 노드 없음")
            continue

        text_node = tools[1]
        text_node.SetInput("StyledText", sub["text"])

        print(f"  [{i+1}] OK: {sub['text'][:20]}...")
        success += 1

    return success


def main():
    print("=" * 50)
    print("AutoCaption Pro v1.0")
    print("=" * 50)
    print("\n[사용 방법]")
    print("  1) Power Bins > AutoCaption Pro 폴더 선택")
    print("  2) 또는 Media Pool에 템플릿 복사 후 선택")
    print("  3) 이 스크립트 실행\n")

    # 1. Resolve 연결
    resolve = get_resolve()
    if not resolve:
        return

    # 2. 타임라인 가져오기
    project, timeline = get_timeline(resolve)
    if not timeline:
        return

    # 3. 자막 추출
    subtitles = get_subtitles(timeline)
    if not subtitles:
        return

    # 4. 템플릿 찾기
    folder = find_template_folder(project)
    if not folder:
        return

    template = get_template(folder)
    if not template:
        return

    # 5. 변환 실행
    success = process_subtitles(project, timeline, subtitles, template)

    # 6. 결과
    print("\n" + "=" * 50)
    if success == len(subtitles):
        print(f"완료! {success}/{len(subtitles)}개 변환 성공")
    else:
        print(f"부분 완료: {success}/{len(subtitles)}개 변환 성공")
    print("=" * 50)


if __name__ == "__main__":
    main()

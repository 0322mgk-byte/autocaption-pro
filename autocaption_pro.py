#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AutoCaption Pro v1.0 (Minimal)
==============================
자막 트랙 -> Text+ 템플릿 자동 변환
무료 버전 완벽 지원!

실행: Workspace > Scripts > Utility > autocaption_pro
"""

# ============================================================================
# 설정
# ============================================================================
TEMPLATE_FOLDER = "AutoCaption Pro"   # Power Bin 내 폴더명
SUBTITLE_TRACK = 1                     # ST1 = 1


def get_resolve():
    """Resolve 연결 (Fusion Scripts 메뉴에서 실행 시)"""
    try:
        # Fusion Scripts에서 실행 시 전역 변수 사용
        resolve = fusion.GetResolve()
        if resolve:
            return resolve
    except:
        pass

    try:
        # 외부 실행 시 (Studio 버전만 지원)
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

    print(f"Found {len(subtitles)} subtitles")
    return subtitles


def find_template_folder(project):
    """Media Pool 또는 현재 폴더에서 템플릿 폴더 찾기"""
    media_pool = project.GetMediaPool()

    # 재귀 탐색 함수
    def search(folder, depth=0):
        if depth > 10:
            return None
        name = folder.GetName()
        print(f"{'  '*depth}[Folder] {name}")

        # AutoCaption 포함하면 찾음
        if "AutoCaption" in name:
            return folder

        for sub in folder.GetSubFolderList():
            result = search(sub, depth + 1)
            if result:
                return result
        return None

    # 1. 현재 폴더에서 먼저 검색
    print("=== 현재 폴더 검색 ===")
    current = media_pool.GetCurrentFolder()
    if current:
        print(f"Current folder: {current.GetName()}")
        if "AutoCaption" in current.GetName():
            print(f"Found folder: {current.GetName()}")
            return current

    # 2. Root 폴더에서 검색
    print("=== Root 폴더 검색 ===")
    root = media_pool.GetRootFolder()
    folder = search(root)

    if folder:
        print(f"Found folder: {folder.GetName()}")
        return folder

    # 3. 못 찾으면 현재 폴더의 클립이라도 확인
    print("=== 폴더 못 찾음 - 현재 폴더 사용 ===")
    if current and current.GetClipList():
        print(f"Using current folder: {current.GetName()}")
        return current

    print(f"ERROR: '{TEMPLATE_FOLDER}' 폴더를 찾을 수 없습니다")
    print("해결방법: Media Pool에서 템플릿이 있는 폴더를 선택한 후 다시 실행하세요")
    return None


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
        # 1. 타임라인에 템플릿 추가 (Snap Captions 방식)
        # endFrame = duration (0-indexed가 아님, duration 그대로 사용)
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

        # 2. Fusion Comp 가져오기
        comp = clip.GetFusionCompByIndex(1)
        if not comp:
            print(f"  [{i+1}] FAIL: Fusion Comp 없음")
            continue

        # 3. Text+ 노드 찾기 (Snap Captions 방식: GetToolList)
        tools = comp.GetToolList(False, "TextPlus")
        if not tools:
            print(f"  [{i+1}] FAIL: TextPlus 노드 없음")
            continue

        # 4. 텍스트 변경
        text_node = tools[1]  # Lua는 1-indexed, Python에서도 dict key가 1
        text_node.SetInput("StyledText", sub["text"])

        print(f"  [{i+1}] OK: {sub['text'][:20]}...")
        success += 1

    return success


def main():
    print("=" * 50)
    print("AutoCaption Pro")
    print("=" * 50)

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
    print("=" * 50)
    print(f"Done! {success}/{len(subtitles)} converted")
    print("=" * 50)


if __name__ == "__main__":
    main()

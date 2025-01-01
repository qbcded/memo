import streamlit as st
import os
import datetime
import json

# 메모 데이터를 저장할 파일 경로
MEMO_FILE = "memos.json"

# UTC+9 시간대 고정
KST = datetime.timezone(datetime.timedelta(hours=9))
now = datetime.datetime.now(KST)

def load_memos():
    """메모 데이터를 파일에서 로드"""
    if not os.path.exists(MEMO_FILE):
        return {}
    with open(MEMO_FILE, "r") as f:
        memos = json.load(f)
        # Make sure the data is in the correct format (dictionary with "content" and "timestamp")
        for title, data in memos.items():
            if isinstance(data, str):  # In case we stored a string (incorrect format)
                memos[title] = {"content": data, "timestamp": now.strftime("%Y-%m-%d %H:%M")}
        return memos

def save_memos(memos):
    """메모 데이터를 파일에 저장"""
    with open(MEMO_FILE, "w") as f:
        json.dump(memos, f, ensure_ascii=False, indent=4)

def main():
    st.title("📝 메모장")
    st.write(now.strftime("%Y-%m-%d %H:%M"))

    # 메모 데이터 로드
    memos = load_memos()

    # Session state for selected memo
    if "selected_memo" not in st.session_state:
        st.session_state.selected_memo = None

    # 사이드바: 메모 관리
    st.sidebar.header("메모 관리")
    memo_titles = list(memos.keys())

    # "새로운 메모 만들기" 버튼 추가
    if st.sidebar.button("새로운 메모"):
        st.session_state.selected_memo = None  # Reset to None for new memo
        st.rerun()  # Rerun the app to refresh the state

    if st.session_state.selected_memo:
        # 기존 메모 편집
        st.sidebar.subheader("편집 중인 메모")
        st.sidebar.write(f"현재 선택: {st.session_state.selected_memo}")
        old_title = st.session_state.selected_memo
        memo_data = memos[old_title]
        content = memo_data["content"]
        timestamp = memo_data["timestamp"]


        # 제목 수정 입력 필드 추가
        new_title = st.text_input("제목", old_title)

        new_content = st.text_area("내용", content)

        # 작성 시간 우측 정렬: HTML을 이용하여 우측 정렬 적용
        st.markdown(f'<p style="text-align: right;">작성 시간: {timestamp}</p>', unsafe_allow_html=True)

        # 수정과 삭제 버튼을 바로 옆에 배치하기 위해 동일한 열을 사용
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            if st.button("메모 수정"):
                if new_title.strip() != old_title:
                    # 제목이 변경되었을 때 기존 제목을 삭제하고 새 제목으로 저장
                    memos[new_title] = {"content": new_content, "timestamp": timestamp}
                    del memos[old_title]
                else:
                    # 제목이 변경되지 않으면 그냥 수정
                    memos[old_title] = {"content": new_content, "timestamp": timestamp}
                save_memos(memos)
                st.success(f"'{new_title}' 메모가 수정되었습니다.")
                st.session_state.selected_memo = new_title  # Update selected memo
                st.rerun()  # Trigger a rerun to refresh the app

        with col2:
            if st.button("메모 삭제"):
                del memos[old_title]
                save_memos(memos)
                st.success(f"'{old_title}' 메모가 삭제되었습니다.")
                st.session_state.selected_memo = None  # Reset to None after deletion
                st.rerun()  # Trigger a rerun to refresh the app
    

    else:
        # 새 메모 추가
        title = st.text_input("제목", "")
        content = st.text_area("내용", "")

        if st.button("메모 저장"):
            if title.strip() == "":
                st.error("제목을 입력해주세요.")
            else:
                # Add timestamp when saving a new memo (without seconds)
                timestamp = now.strftime("%Y-%m-%d %H:%M")
                memos[title] = {"content": content, "timestamp": timestamp}
                save_memos(memos)
                st.success(f"'{title}' 메모가 저장되었습니다.")
                st.session_state.selected_memo = title  # Select the new memo
                st.rerun()  # Trigger a rerun to refresh the app

    # 검색 기능
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 메모 검색")
    search_query = st.sidebar.text_input("검색어 입력", "")

    if search_query:
        st.subheader("검색 결과")
        filtered_memos = {
            title: data
            for title, data in memos.items()
            if search_query.lower() in title.lower() or search_query.lower() in data["content"].lower()
        }
        if filtered_memos:
            for title, data in filtered_memos.items():
                st.write(f"📄 {title} - 작성 시간: {data['timestamp']}")
                if st.button(f"선택", key=f"{title}"):
                    st.session_state.selected_memo = title  # Select the memo directly when clicked
                    st.rerun()  # Trigger a rerun to refresh the app
        else:
            st.write("검색 결과가 없습니다.")
    else:
        # 모든 메모 목록 보기
        st.sidebar.markdown("---")
        st.sidebar.subheader("모든 메모")
        for memo_title in memo_titles:
            memo_data = memos[memo_title]
            st.sidebar.write(f"📄 {memo_title} - 작성 시간: {memo_data['timestamp']}")
            if st.sidebar.button(f"선택", key=f"{memo_title}"):
                st.session_state.selected_memo = memo_title  # Select the memo directly when clicked
                st.rerun()  # Trigger a rerun to refresh the app

if __name__ == "__main__":
    main()

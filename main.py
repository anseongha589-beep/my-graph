
import streamlit as st
import pandas as pd
import altair as alt


# ==========================================
# 기본 설정
# ==========================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)


# ==========================================
# 제목
# ==========================================

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")

st.write("KOBIS 일별 박스오피스 1년치 데이터를 이용한 영화 데이터 분석")


# ==========================================
# 데이터 주소
# ==========================================

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


# ==========================================
# 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL)


try:
    df = load_data()

except Exception:
    st.error("데이터를 불러오지 못했습니다.")
    st.info("인터넷 연결과 데이터 주소를 확인해 주세요.")
    st.stop()


# ==========================================
# 데이터 확인
# ==========================================

if df.empty:
    st.error("데이터가 없습니다.")
    st.stop()


required_columns = [
    "날짜",
    "순위",
    "영화코드",
    "영화명",
    "일관객",
    "누적관객",
    "스크린수",
    "상영횟수"
]

missing_columns = []

for column in required_columns:
    if column not in df.columns:
        missing_columns.append(column)

if missing_columns:
    st.error("필요한 열이 없습니다.")
    st.write("없는 열:", ", ".join(missing_columns))
    st.stop()


# ==========================================
# 날짜 변환
# ==========================================
# 20250101 같은 8자리 숫자를
# 실제 날짜 형식으로 변환합니다.

df["날짜"] = pd.to_datetime(
    df["날짜"].astype(str),
    format="%Y%m%d",
    errors="coerce"
)


# ==========================================
# 숫자 데이터 변환
# ==========================================
# 숫자가 문자로 저장되어 있을 경우를 대비합니다.

number_columns = [
    "순위",
    "일관객",
    "누적관객",
    "스크린수",
    "상영횟수"
]

for column in number_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ==========================================
# 잘못된 데이터 제거
# ==========================================

df = df.dropna(
    subset=["날짜", "영화명", "일관객"]
).copy()


# ==========================================
# 날짜순 정렬
# ==========================================

df = df.sort_values(
    by=["날짜", "순위"]
).reset_index(drop=True)


# ==========================================
# 데이터 정보
# ==========================================

start_date = df["날짜"].min()
end_date = df["날짜"].max()

movie_count = df["영화명"].nunique()


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "데이터 시작일",
        start_date.strftime("%Y-%m-%d")
    )

with col2:
    st.metric(
        "데이터 마지막 날짜",
        end_date.strftime("%Y-%m-%d")
    )

with col3:
    st.metric(
        "영화 종류",
        f"{movie_count:,}편"
    )


st.divider()


# ==========================================
# 그래프 1
# ==========================================

st.header("📈 그래프 1. 영화별 일관객 변화")

st.write("영화를 선택하면 날짜별 일관객 변화를 볼 수 있습니다.")


# ==========================================
# 영화 선택
# ==========================================

movie_list = sorted(
    df["영화명"].unique().tolist()
)

selected_movie = st.selectbox(
    "영화를 선택하세요",
    movie_list
)


# ==========================================
# 선택한 영화 데이터
# ==========================================

movie_df = df[
    df["영화명"] == selected_movie
].copy()

movie_df = movie_df.sort_values(
    by="날짜"
)


# ==========================================
# 선 그래프
# ==========================================
# 마우스를 그래프의 점에 올리면
# 날짜와 관객수가 표시됩니다.

chart = (
    alt.Chart(movie_df)
    .mark_line(
        point=True
    )
    .encode(
        x=alt.X(
            "날짜:T",
            title="날짜",
            axis=alt.Axis(
                format="%m-%d",
                labelAngle=-45
            )
        ),
        y=alt.Y(
            "일관객:Q",
            title="일관객수",
            axis=alt.Axis(
                format=","
            )
        ),
        tooltip=[
            alt.Tooltip(
                "날짜:T",
                title="날짜",
                format="%Y-%m-%d"
            ),
            alt.Tooltip(
                "일관객:Q",
                title="관객수",
                format=","
            )
        ]
    )
    .properties(
        height=450
    )
    .interactive()
)


st.altair_chart(
    chart,
    use_container_width=True
)


# ==========================================
# 사용자가 직접 작성하는 설명
# ==========================================

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "직접 작성하세요.",
    placeholder="여기에 내용을 입력하세요.",
    key="graph1_text",
    height=100
)


st.divider()


# ==========================================
# 그래프 2
# ==========================================

st.header("�

import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 1 - 시간")
st.write("KOBIS 일별 박스오피스 1년치 데이터를 이용합니다.")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL)


try:
    df = load_data()
except Exception:
    st.error("데이터를 불러오지 못했습니다.")
    st.info("데이터 주소 또는 인터넷 연결을 확인해주세요.")
    st.stop()


if df.empty:
    st.error("데이터가 비어 있습니다.")
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

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error("CSV 파일의 열 이름을 확인해주세요.")
    st.write("없는 열:", ", ".join(missing_columns))
    st.stop()


df["날짜"] = pd.to_datetime(
    df["날짜"].astype(str),
    format="%Y%m%d",
    errors="coerce"
)


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


df = df.dropna(
    subset=["날짜", "영화명", "일관객"]
).copy()


df = df.sort_values(
    by=["날짜", "순위"],
    ascending=[True, True]
).reset_index(drop=True)


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

st.header("그래프 1 - 영화별 일관객 변화")

st.write(
    "영화를 선택한 뒤 그래프의 점에 마우스를 올려보세요."
)


movie_list = sorted(
    df["영화명"].unique().tolist()
)


default_movie = "스파이더맨: 브랜드 뉴 데이"


if default_movie in movie_list:
    default_index = movie_list.index(default_movie)
else:
    default_index = 0


selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_list,
    index=default_index
)


movie_df = df[
    df["영화명"] == selected_movie
].copy()


movie_df = movie_df.sort_values("날짜")


hover1 = alt.selection_point(
    on="pointerover",
    nearest=True,
    fields=["날짜"],
    empty=False
)


base1 = alt.Chart(movie_df).encode(
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
        title="일관객",
        axis=alt.Axis(
            format=","
        )
    )
)


line1 = base1.mark_line(
    point=True
)


points1 = base1.mark_circle(
    size=80
).encode(
    opacity=alt.condition(
        hover1,
        alt.value(1),
        alt.value(0)
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
).add_params(hover1)


chart1 = (
    (line1 + points1)
    .properties(height=450)
    .interactive()
)


st.altair_chart(
    chart1,
    use_container_width=True
)


st.info(
    "그래프 위의 점에 마우스를 올리면 날짜와 관객수가 표시됩니다."
)


st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="여기에 직접 작성하세요.",
    key="graph1_explanation",
    height=100
)


st.divider()


# ==========================================
# 그래프 2
# ==========================================

st.header("그래프 2 - 일관객 합계 TOP 5 영화 날짜별 비교")

st.write(
    "전체 기간 동안 일관객 합계가 가장 큰 5편의 날짜별 일관객을 비교합니다."
)


# 전체 기간의 일관객 합계가 큰 영화 5편 계산
top5_summary = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .rename(columns={"일관객": "기간일관객합계"})
    .sort_values(
        "기간일관객합계",
        ascending=False
    )
    .head(5)
)


top5_movies = top5_summary["영화명"].tolist()


top5_df = df[
    df["영화명"].isin(top5_movies)
].copy()


top5_df = top5_df.sort_values(
    by=["날짜", "영화명"]
)


# 범례에서 영화를 클릭하기 위한 선택
legend_selection = alt.selection_point(
    fields=["영화명"],
    bind="legend"
)


# 마우스를 가까운 날짜에 가져갔을 때 정보를 보여주기 위한 선택
hover2 = alt.selection_point(
    on="pointerover",
    nearest=True,
    fields=["날짜"],
    empty=False
)


base2 = alt.Chart(top5_df).encode(
    x=alt.X(
        "날짜:T",
        title="날짜",
        axis=alt.Axis(
            format="%b %Y",
            labelAngle=0
        )
    ),
    y=alt.Y(
        "일관객:Q",
        title="일관객",
        axis=alt.Axis(
            format=","
        )
    ),
    color=alt.Color(
        "영화명:N",
        title="영화 목록 (클릭하여 토글)",
        legend=alt.Legend(
            orient="right",
            direction="vertical"
        )
    ),
    opacity=alt.condition(
        legend_selection,
        alt.value(1),
        alt.value(0.08)
    )
)


line2 = base2.mark_line(
    strokeWidth=2.5
)


points2 = base2.mark_circle(
    size=65
).encode(
    opacity=alt.condition(
        hover2,
        alt.value(1),
        alt.value(0)
    ),
    tooltip=[
        alt.Tooltip(
            "영화명:N",
            title="영화"
        ),
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
).add_params(hover2)


chart2 = (
    (line2 + points2)
    .add_params(legend_selection)
    .properties(
        height=500
    )
    .interactive()
)


st.altair_chart(
    chart2,
    use_container_width=True
)


st.info(
    "오른쪽 범례의 영화 이름을 클릭하면 해당 영화의 선을 켜고 끌 수 있습니다. "
    "그래프의 선 위에 마우스를 올리면 영화명, 날짜, 관객수가 표시됩니다."
)


st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="여기에 직접 작성하세요.",
    key="graph2_explanation",
    height=100
)


st.divider()



# ==========================================
# 그래프 3
# ==========================================

st.header("그래프 3 - 날짜별 10위권 일관객 합계")

st.write(
    "각 날짜의 10위권 영화 일관객을 모두 더해서 전체 관객 규모의 변화를 보여줍니다."
)


# 날짜별 10위권 일관객 합계 계산
daily_top10 = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .rename(columns={"일관객": "10위권 일관객 합계"})
    .sort_values("날짜")
)


# 일관객 합계가 가장 컸던 날짜 3일
top3_days = (
    daily_top10
    .nlargest(3, "10위권 일관객 합계")
    .sort_values("날짜")
    .copy()
)


# 영역 그래프
area = alt.Chart(daily_top10).mark_area(
    opacity=0.55
).encode(
    x=alt.X(
        "날짜:T",
        title="날짜",
        axis=alt.Axis(
            format="%b %Y",
            labelAngle=0
        )
    ),
    y=alt.Y(
        "10위권 일관객 합계:Q",
        title="10위권 일관객 합계",
        axis=alt.Axis(format=",")
    ),
    tooltip=[
        alt.Tooltip(
            "날짜:T",
            title="날짜",
            format="%Y-%m-%d"
        ),
        alt.Tooltip(
            "10위권 일관객 합계:Q",
            title="관객수",
            format=","
        )
    ]
)


line3 = alt.Chart(daily_top10).mark_line(
    strokeWidth=2
).encode(
    x=alt.X("날짜:T"),
    y=alt.Y("10위권 일관객 합계:Q")
)


# 가장 관객수가 많았던 3일의 점
highlight_points = alt.Chart(top3_days).mark_point(
    size=120,
    filled=True
).encode(
    x=alt.X("날짜:T"),
    y=alt.Y("10위권 일관객 합계:Q"),
    tooltip=[
        alt.Tooltip(
            "날짜:T",
            title="날짜",
            format="%Y-%m-%d"
        ),
        alt.Tooltip(
            "10위권 일관객 합계:Q",
            title="관객수",
            format=","
        )
    ]
)


# 가장 관객수가 많았던 3일의 날짜 표시
highlight_text = alt.Chart(top3_days).mark_text(
    dy=-18,
    fontSize=13,
    fontWeight="bold"
).encode(
    x=alt.X("날짜:T"),
    y=alt.Y("10위권 일관객 합계:Q"),
    text=alt.Text(
        "날짜:T",
        format="%Y-%m-%d"
    )
)


chart3 = (
    alt.layer(
        area,
        line3,
        highlight_points,
        highlight_text
    )
    .properties(height=500)
    .interactive()
)


st.altair_chart(
    chart3,
    use_container_width=True
)


st.info(
    "그래프 위에 표시된 날짜가 10위권 일관객 합계가 가장 컸던 상위 3일입니다."
)


st.subheader("이 그래프로 알 수 있는 것")


st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="여기에 직접 작성하세요.",
    key="graph3_explanation",
    height=100
)


st.divider()



# ==========================================
# 그래프 4
# ==========================================

st.header("그래프 4 - 기간 일관객 TOP 10 영화")

st.write(
    "전체 기간 동안 영화별 일관객을 모두 더해 TOP 10을 뽑았습니다. "
    "막대에 마우스를 올리면 10위권에 든 날수도 확인할 수 있습니다."
)

movie_summary = (
    df.groupby("영화명", as_index=False)
    .agg({
        "일관객": "sum",
        "날짜": "nunique"
    })
    .rename(columns={
        "일관객": "기간_일관객_합계",
        "날짜": "10위권_등장_날수"
    })
)

top10_summary = (
    movie_summary
    .sort_values(
        "기간_일관객_합계",
        ascending=False
    )
    .head(10)
    .copy()
)

chart4 = (
    alt.Chart(top10_summary)
    .mark_bar()
    .encode(
        x=alt.X(
            "기간_일관객_합계:Q",
            title="기간 일관객 합계",
            axis=alt.Axis(format=",")
        ),
        y=alt.Y(
            "영화명:N",
            title="영화",
            sort=alt.SortField(
                field="기간_일관객_합계",
                order="descending"
            )
        ),
        tooltip=[
            alt.Tooltip(
                "영화명:N",
                title="영화"
            ),
            alt.Tooltip(
                "기간_일관객_합계:Q",
                title="기간 일관객 합계",
                format=","
            ),
            alt.Tooltip(
                "10위권_등장_날수:Q",
                title="개봉 후 10위권에 든 날수",
                format=","
            )
        ]
    )
    .properties(
        height=450
    )
)

st.altair_chart(
    chart4,
    use_container_width=True
)

st.info(
    "관객이 많은 영화가 위쪽에 표시됩니다. "
    "막대에 마우스를 올리면 개봉 후 10위권에 든 날수도 표시됩니다."
)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="여기에 직접 작성하세요.",
    key="graph4_explanation",
    height=100
)

st.divider()


# ==========================================
# 그래프 5
# ==========================================

st.header("그래프 5 - 월 × 요일별 일관객 히트맵")

st.write(
    "날짜에서 월과 요일을 뽑아 월별·요일별 일관객 합계를 비교합니다. "
    "색이 진할수록 관객이 많습니다."
)


# 월과 요일 추출
heatmap_df = df.copy()

heatmap_df["월"] = heatmap_df["날짜"].dt.month

weekday_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]

heatmap_df["요일번호"] = heatmap_df["날짜"].dt.weekday
heatmap_df["요일"] = heatmap_df["요일번호"].map(
    dict(enumerate(weekday_order))
)


# 월 × 요일별 일관객 합계
heatmap_data = (
    heatmap_df
    .groupby(
        ["월", "요일번호", "요일"],
        as_index=False
    )["일관객"]
    .sum()
)


# 1월부터 12월, 월요일부터 일요일 순서로 정렬
heatmap_data = heatmap_data.sort_values(
    by=["월", "요일번호"]
)


# 히트맵
chart5 = (
    alt.Chart(heatmap_data)
    .mark_rect()
    .encode(
        x=alt.X(
            "요일:N",
            title="요일",
            sort=weekday_order
        ),
        y=alt.Y(
            "월:O",
            title="월",
            sort=[str(i) for i in range(1, 13)],
            axis=alt.Axis(
                labelExpr="datum.label + '월'"
            )
        ),
        color=alt.Color(
            "일관객:Q",
            title="일관객 합계",
            scale=alt.Scale(
                scheme="blues"
            )
        ),
        tooltip=[
            alt.Tooltip(
                "월:O",
                title="월",
                format="d"
            ),
            alt.Tooltip(
                "요일:N",
                title="요일"
            ),
            alt.Tooltip(
                "일관객:Q",
                title="일관객 합계",
                format=","
            )
        ]
    )
    .properties(
        height=500
    )
)


st.altair_chart(
    chart5,
    use_container_width=True
)


st.info(
    "색이 진할수록 해당 월·요일에 발생한 일관객 합계가 많습니다. "
    "요일은 월요일부터 일요일 순서로 표시됩니다."
)


st.subheader("이 그래프로 알 수 있는 것")


st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="여기에 직접 작성하세요.",
    key="graph5_explanation",
    height=100
)


st.divider()

st.caption(
    "데이터 출처: KOBIS 일별 박스오피스 데이터"
)

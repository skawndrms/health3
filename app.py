import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 1학년 학급별 건강검진 비교 통계")

# 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx"])

if uploaded_file:
    # 데이터 불러오기
    df = pd.read_excel(uploaded_file, sheet_name="데이터 엑셀다운")

    # 필요한 컬럼만 추출
    df_sel = df[[
        "반", "성별", "신장", "체중", "체질량지수_학생", "비만도_학생",
        "혈압(최고)", "혈압(최저)",
        "혈청지오티(AST)", "혈청지피티(ALT)",
        "혈색소(Hb)", "흉부X선검사",
        "시력(좌)", "시력(우)",
        "종합판정", "조치사항", "소견"
    ]].copy()

    # ---------------------------
    # Helper 함수들
    # ---------------------------
    def classify_bp(row):
        if row["혈압(최고)"] >= 130 or row["혈압(최저)"] >= 80:
            return "고혈압 의심"
        elif row["혈압(최고)"] < 90 or row["혈압(최저)"] < 60:
            return "저혈압 의심"
        else:
            return "정상"

    def classify_vision(row):
        left, right = row["시력(좌)"], row["시력(우)"]
        if abs(left - right) >= 0.3:
            return "좌우차 0.3 이상"
        elif left < 0.3 or right < 0.3:
            return "심한 시력저하 (0.3 미만)"
        elif left < 0.7 or right < 0.7:
            return "경도 시력저하 (0.3~0.7)"
        else:
            return "정상"

    # ---------------------------
    # 탭 구성
    # ---------------------------
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "체격", "혈압", "간기능", "시력", "종합판정", "조치사항/소견", "원본 데이터"
    ])

    # ---------------------------
    # 1. 체격
    # ---------------------------
    with tab1:
        st.subheader("체격 관련 (학급별 비만도 분포)")
        obesity_class = df_sel.groupby(["반", "비만도_학생"]).size().reset_index(name="학생 수")
        obesity_class["비율(%)"] = obesity_class.groupby("반")["학생 수"].transform(lambda x: x / x.sum() * 100)

        fig1 = px.bar(
            obesity_class,
            x="반", y="비율(%)", color="비만도_학생",
            title="학급별 비만도 분포 (%)",
            barmode="stack", text=obesity_class["비율(%)"].round(1)
        )
        st.plotly_chart(fig1)
        st.dataframe(obesity_class.pivot(index="반", columns="비만도_학생", values="비율(%)").round(1))

    # ---------------------------
    # 2. 혈압
    # ---------------------------
    with tab2:
        st.subheader("혈압 관련 (고혈압 / 저혈압 비율)")
        df_sel["혈압판정"] = df_sel.apply(classify_bp, axis=1)
        bp_class = df_sel.groupby(["반", "혈압판정"]).size().reset_index(name="학생 수")
        bp_class["비율(%)"] = bp_class.groupby("반")["학생 수"].transform(lambda x: x / x.sum() * 100)

        fig2 = px.bar(
            bp_class, x="반", y="비율(%)", color="혈압판정",
            title="학급별 혈압 판정 분포 (%)",
            barmode="stack", text=bp_class["비율(%)"].round(1)
        )
        st.plotly_chart(fig2)
        st.dataframe(bp_class.pivot(index="반", columns="혈압판정", values="비율(%)").round(1))

    # ---------------------------
    # 3. 간기능
    # ---------------------------
    with tab3:
        st.subheader("간기능 이상 비율 (AST 또는 ALT ≥ 40)")
        df_sel["간기능 이상"] = ((df_sel["혈청지오티(AST)"] >= 40) | (df_sel["혈청지피티(ALT)"] >= 40)).map({True: "이상", False: "정상"})
        liver_class = df_sel.groupby(["반", "간기능 이상"]).size().reset_index(name="학생 수")
        liver_class["비율(%)"] = liver_class.groupby("반")["학생 수"].transform(lambda x: x / x.sum() * 100)

        fig3 = px.bar(
            liver_class, x="반", y="비율(%)", color="간기능 이상",
            title="학급별 간기능 이상 분포 (%)",
            barmode="stack", text=liver_class["비율(%)"].round(1)
        )
        st.plotly_chart(fig3)
        st.dataframe(liver_class.pivot(index="반", columns="간기능 이상", values="비율(%)").round(1))

    # ---------------------------
    # 4. 시력
    # ---------------------------
    with tab4:
        st.subheader("시력 관련 (교육청 기준)")
        df_sel["시력판정"] = df_sel.apply(classify_vision, axis=1)
        vision_class = df_sel.groupby(["반", "시력판정"]).size().reset_index(name="학생 수")
        vision_class["비율(%)"] = vision_class.groupby("반")["학생 수"].transform(lambda x: x / x.sum() * 100)

        fig4 = px.bar(
            vision_class, x="반", y="비율(%)", color="시력판정",
            title="학급별 시력 판정 분포 (%)",
            barmode="stack", text=vision_class["비율(%)"].round(1)
        )
        st.plotly_chart(fig4)
        st.dataframe(vision_class.pivot(index="반", columns="시력판정", values="비율(%)").round(1))

    # ---------------------------
    # 5. 종합판정
    # ---------------------------
    with tab5:
        st.subheader("종합판정 분포")
        result_class = df_sel.groupby(["반", "종합판정"]).size().reset_index(name="학생 수")
        result_class["비율(%)"] = result_class.groupby("반")["학생 수"].transform(lambda x: x / x.sum() * 100)

        fig5 = px.bar(
            result_class, x="반", y="비율(%)", color="종합판정",
            title="학급별 종합판정 분포 (%)",
            barmode="stack", text=result_class["비율(%)"].round(1)
        )
        st.plotly_chart(fig5)
        st.dataframe(result_class.pivot(index="반", columns="종합판정", values="비율(%)").round(1))

    # ---------------------------
    # 6. 조치사항/소견
    # ---------------------------
    with tab6:
        st.subheader("조치사항/소견 키워드 분석")
        keywords = ["체중", "빈혈", "고혈압", "간", "추가검사", "시력"]
        text_df = pd.DataFrame(columns=["반", "키워드", "학생 수"])

        for ban in df_sel["반"].unique():
            class_data = df_sel[df_sel["반"] == ban]
            text = (class_data["조치사항"].fillna("") + " " + class_data["소견"].fillna("")).str.cat(sep=" ")
            for kw in keywords:
                count = text.count(kw)
                text_df = pd.concat([text_df, pd.DataFrame({"반": [ban], "키워드": [kw], "학생 수": [count]})])

        text_df["비율(%)"] = text_df.groupby("반")["학생 수"].transform(lambda x: x / (x.sum() if x.sum() > 0 else 1) * 100)

        fig6 = px.bar(
            text_df, x="반", y="비율(%)", color="키워드",
            title="학급별 조치사항/소견 키워드 비율 (%)",
            barmode="stack", text=text_df["비율(%)"].round(1)
        )
        st.plotly_chart(fig6)
        st.dataframe(text_df.pivot(index="반", columns="키워드", values="비율(%)").round(1))

    # ---------------------------
    # 7. 원본 데이터
    # ---------------------------
    with tab7:
        st.subheader("📑 원본 데이터 미리보기")
        st.dataframe(df_sel.head(30))

else:
    st.info("엑셀 파일을 업로드하면 학급별 비교 통계를 탭별로 확인할 수 있습니다.")

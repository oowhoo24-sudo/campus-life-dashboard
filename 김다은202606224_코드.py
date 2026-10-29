import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import re

# ==========================================
# 0. 한글 폰트 설정 (그래프 한글 깨짐 방지 🎨)
# ==========================================
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows 기준 (Mac일 경우 'AppleGothic')
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# ==========================================
# 1. 페이지 기본 설정 & 귀여운 제목 🌸
# ==========================================
st.set_page_config(
    page_title="캠퍼스 생활 실태 🏫",
    page_icon="🎓",
    layout="wide"
)

st.title("🏫 캠퍼스 생활 실태 분석 WebApp 🎓")
st.caption("인문사회대 친구들의 하루 생활 습관과 학교생활 만족도, 그리고 진솔한 의견을 알아봐요! ✨")
st.markdown("---")


# ==========================================
# 2. 데이터 불러오기 및 정제 (🧹 잘못된 데이터 처리)
# ==========================================
@st.cache_data
def load_data():
    df_raw = pd.read_csv("campus_life.csv")
    return df_raw


df_raw = load_data()

# 데이터 전처리 복사본 생성
df = df_raw.copy()

# '만족도' 컬럼에 있는 '모름' 등의 문자열을 숫자로 변환 (변환 안 되는 것은 NaN 처리)
df['만족도'] = pd.to_numeric(df['만족도'], errors='coerce')

# 공부시간 누락(NaN)이거나 만족도 정제 후 NaN이 된 행들을 이상치/누락 데이터로 판단하여 제외
df_clean = df.dropna(subset=['공부시간', '만족도']).copy()

# 제외된 데이터 건수 계산
excluded_count = len(df_raw) - len(df_clean)

# ==========================================
# 3. 사용자 학과 선택 필터 🎈
# ==========================================
st.subheader("🔍 학과를 선택하세요")

# 파일에 존재하는 학과 목록 추출
department_list = sorted(df_clean['학과'].unique().tolist())

selected_dept = st.selectbox(
    "알아보고 싶은 학과를 골라주세요! 👇",
    options=department_list
)

# 💡 작은 박스로 제외된 데이터 및 처리 안내 표시
with st.expander("ℹ️ 데이터 정제 안내 (클릭해서 확인해보세요!)", expanded=False):
    st.info(f"✨ 무응답, 누락 및 이상치 데이터 **{excluded_count}건**이 안전하게 제외되었습니다. 정제된 신뢰할 수 있는 데이터만 분석에 사용됩니다! 🧹")

st.markdown("---")

# 선택한 학과의 데이터만 필터링
dept_df = df_clean[df_clean["학과"] == selected_dept]

st.header(f"✨ [{selected_dept}] 학생들의 라이프 스타일 분석 📊")

# 예쁜 파스텔톤 컬러 정의
pastel_colors = ['#FFB3BA', '#BAFFC9', '#BAE1FF']

# ==========================================
# [파트 1] 생활 습관 & 만족도 그래프 (2열 배치 📉)
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. ⏰ 생활 시간 비중")
    avg_sleep = dept_df["수면시간"].mean()
    avg_study = dept_df["공부시간"].mean()
    avg_phone = dept_df["스마트폰"].mean()

    fig1, ax1 = plt.subplots(figsize=(4.5, 4.5))
    labels = ['수면 시간', '공부 시간', '스마트폰 사용']
    sizes = [avg_sleep, avg_study, avg_phone]

    ax1.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=pastel_colors,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    ax1.set_title(f"💖 {selected_dept} 생활 습관", fontsize=12, fontweight='bold')
    st.pyplot(fig1)

with col2:
    st.subheader("2. 🎯 공부시간과 만족도")

    fig2, ax2 = plt.subplots(figsize=(5.5, 4.5))

    ax2.scatter(
        dept_df["공부시간"],
        dept_df["만족도"],
        c='#FF9AA2',
        s=140,
        alpha=0.8,
        edgecolors='white',
        linewidth=1.5
    )

    ax2.set_xlabel("📖 공부 시간 (시간)", fontsize=10)
    ax2.set_ylabel("😊 만족도 점수", fontsize=10)
    ax2.set_title(f"⭐ 공부 시간 vs 만족도", fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig2)

st.markdown("---")

# ==========================================
# [파트 2] 한 줄 의견 분석 (워드클라우드 & 단어 통계 ☁️📊)
# ==========================================
st.subheader("3. 💬 한 줄 의견 심층 분석")
st.write("해당 학과 친구들이 남긴 솔직한 한 줄 의견을 워드클라우드와 상세 단어 통계로 확인해봐요!")

text_data = " ".join(dept_df["한줄의견"].dropna())

# (1) 워드클라우드 표시
wordcloud = WordCloud(
    font_path='malgun.ttf',
    background_color='white',
    width=700,
    height=280,
    colormap='Set3'
).generate(text_data)

fig3, ax3 = plt.subplots(figsize=(8, 3.2))
ax3.imshow(wordcloud, interpolation='bilinear')
ax3.axis("off")
st.pyplot(fig3)

st.markdown("---")

# ==========================================
# [파트 3] 상위 10개 단어 막대그래프 & 긍정/부정 단어 카운트 ✨
# ==========================================
st.subheader("📊 한줄의견 주요 단어 랭킹 & 긍정·부정 분석")

# 간단한 단어 토큰화 (2글자 이상 단어 추출 및 의미 없는 조사 제외)
stopwords = ['이', '가', '을', '를', '의', '에', '도', '는', '은', '에서', '으로', '고', '하', '아', '어요', '해서']
words = re.findall(r'[가-힣]{2,}', text_data)
filtered_words = [w for w in words if w not in stopwords]

# 상위 10개 단어 추출
word_counts = Counter(filtered_words)
top_10 = word_counts.most_common(10)

if top_10:
    df_top10 = pd.DataFrame(top_10, columns=['단어', '빈도수'])

    # 2열로 나누어 왼쪽은 막대그래프, 오른쪽은 긍정/부정 등장 횟수 표시
    col_stat1, col_stat2 = st.columns(2)

    with col_stat1:
        st.markdown("##### 🏆 자주 등장하는 단어 TOP 10")
        fig4, ax4 = plt.subplots(figsize=(6, 4))

        # 파스텔톤 막대그래프 생성 (seaborn 활용)
        sns.barplot(
            data=df_top10,
            x='빈도수',
            y='단어',
            palette='Pastel1',
            ax=ax4
        )
        ax4.set_xlabel("언급된 횟수 (번)", fontsize=10)
        ax4.set_ylabel("단어", fontsize=10)
        ax4.set_title(f"✨ {selected_dept} 인기 키워드 TOP 10", fontsize=11, fontweight='bold')
        st.pyplot(fig4)

    with col_stat2:
        st.markdown("##### 🌈 긍정 vs 부정 단어 감성 분석 횟수")
        st.write("의견 속에 포함된 감성 키워드들을 분류해 보았어요!")

        # 💡 [오류 해결 포인트] 형태소 활용형을 고려하여 키워드가 포함(in)되어 있으면 카운트되도록 수정!
        positive_keywords = ['좋아', '최고', '재미', '즐거', '맛있', '성공', '힐링', '도움', '예뻐']
        negative_keywords = ['불편', '부족', '피곤', '길어', '힘들', '걱정', '어려', '아쉬', '후회']

        pos_count = sum(text_data.count(kw) for kw in positive_keywords)
        neg_count = sum(text_data.count(kw) for kw in negative_keywords)

        # 메트릭 카드로 예쁘게 출력
        m_col1, m_col2 = st.columns(2)
        m_col1.metric(label="💚 긍정 감성 단어 횟수", value=f"{pos_count}회")
        m_col2.metric(label="💙 부정 감성 단어 횟수", value=f"{neg_count}회")

        # 간단한 해석 덧붙이기
        if pos_count >= neg_count:
            st.success(f"😊 전반적으로 긍정적인 반응({pos_count}회)이 부정적인 반응보다 많거나 비슷해요! 활기찬 대학 생활이 느껴지네요! 🌟")
        else:
            st.warning(f"🧐 부정적/고충 관련 단어({neg_count}회)가 조금 더 눈에 띄어요. 휴식과 힐링이 필요할 시간인가 봐요! ☕")
else:
    st.info("💡 분석할 충분한 한줄의견 데이터가 없습니다.")

# 상큼한 마무리 애니메이션 & 축하 메시지 💌
st.balloons()
st.success(f"🎉 [{selected_dept}] 심층 분석이 완벽하게 완료되었습니다! 중간고사도 대박 나세요! 🍀")
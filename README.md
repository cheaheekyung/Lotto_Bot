# 🎰 프로젝트 소개 [Lotto-Bot]  
로또 당첨번호 통계와 머신러닝 알고리즘 기반으로 사용자가 원하는 전략에 맞는 로또번호를 추천  
사용자 별 결과 및 히스토리 관리기능 제공

## 📖 주요기능  
이 프로젝트는 동행복권에서 제공하는 지난 10년간 당첨데이터를 기반으로 로또 번호를 추천하는 AI 챗봇입니다.  
- 머신러닝 모델(로지스틱 회귀)을 활용한 로또 번호 추천 -> 경향성, 다음 번호 예측
- 통계적 기반 번호 추천
    - 전략1 : 평균이상
    - 전략2 : (평균-표준편차) ~ 평균
- 매주 업데이트 되는 로또 당첨번호를 자동으로 크롤링하여 데이터 갱신
- 사용자가 전략 선택시 추천 번호 반환 (최대 5세트)    

## 🛠️ 사용 기술  
- **백엔드:** Python, Django, Django REST Framework(DRF), JWT   
- **AI 모델:** OPENAI API (GPT-4o-mini), LangChain  
- **데이터 처리:** Pandas, NumPy, BeautifulSoup4, Scikit-learn  
- **DB:** AWS RDS(PostgreSQL)  
- **프론트엔드:** HTML / CSS / Javascript  

## 🔧 설치 방법  
```bash
git clone https://github.com/your-repo/lotto-chatbot.git
cd lotto-chatbot
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

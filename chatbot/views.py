# views.py
import json
import logging
import random
from openai import OpenAI, APIError, RateLimitError, APITimeoutError
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.conf import settings
from django.contrib.auth.decorators import login_required  # 추가
from chatbot.services import get_recommendation, check_data_status
from .models import Recommendation  # 추가: Recommendation 모델 import
from rest_framework.views import APIView  # 추가
from rest_framework.response import Response  # 추가
from rest_framework.permissions import IsAuthenticated  # 추가
from rest_framework import status  # 추가
from chatbot.services import get_recommendation, check_data_status
from .models import Recommendation, LottoDraw  # LottoDraw 추가

from .serializers import RecommendationHistorySerializer, ChatHistorySerializer
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class ChatbotHomeView(TemplateView):
    """View for rendering the chatbot home page"""
    template_name = 'chatbot/home.html'

class CSRFTokenView(View):
    """View for getting CSRF token"""
    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        return JsonResponse({'csrfToken': csrf_token})

class DataStatusView(View):
    """View for checking data status"""
    def get(self, request, *args, **kwargs):
        success, message = check_data_status()
        return JsonResponse({
            'success': success,
            'message': message
        })

@method_decorator(csrf_exempt, name='dispatch')
class ChatAPIView(APIView):
    """Main API view for handling chat interactions"""
    
    def __init__(self):
        super().__init__()
        self.conversation_history = []
        self.lucky_messages = [
            "행운이 함께하길 바랍니다! ✨",
            "이번에는 좋은 결과가 있기를 기원합니다! 🍀",
            "당신의 꿈이 이루어지길 바라며 이 번호들을 선택했습니다! 🌟",
            "이 번호들과 함께 큰 행운이 찾아오길 바랍니다! 🎯",
            "당첨의 기쁨을 누리실 수 있기를 진심으로 응원합니다! ⭐",
            "이번 주는 특별한 행운이 함께하길 바랍니다! 🌈",
            "당신의 성공을 기원하며 이 번호들을 추천해드립니다! 💫",
            "모든 세트에 행운이 가득하길 기원합니다! 🌠",
            "이 번호들이 당신에게 좋은 기운을 가져다주길 바랍니다! 🎊",
            "당첨의 행운이 함께하시길 진심으로 바랍니다! 💫"
        ]

    def _get_gpt_response(self, user_message):
        """Get response from GPT API"""
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            system_prompt = """
안녕하세요! 로또 번호 추천 챗봇입니다.

두 가지 전략으로 번호를 추천해드릴 수 있습니다:

1. 자주 당첨된 번호 기반 추천
2. 잠재력 있는 번호 기반 추천

원하시는 전략을 선택해주세요! 
최대 5세트까지 추천 가능합니다.

(예: "전략1로 3세트 추천해주세요" 또는 "전략1 3세트, 전략2 2세트 추천해주세요")
"""
            messages = [
                {"role": "system", "content": system_prompt},
                *self.conversation_history,
                {"role": "user", "content": user_message}
            ]

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"GPT Error: {str(e)}")
            raise Exception("죄송합니다. 서버 연결에 문제가 발생했습니다.")

    def _process_strategy_counts(self, user_message):
        """Parse strategy counts from user message"""
        strategy_counts = {'1': 0, '2': 0}
        
        try:
            message = user_message.lower()
            words = message.split()
            
            i = 0
            while i < len(words):
                current_word = words[i]
                
                # 전략1/1번전략 처리
                if any(pattern in current_word for pattern in ["전략1", "1번전략", "1번"]):
                    if i + 1 < len(words):
                        next_word = words[i + 1]
                        number = ''.join(filter(str.isdigit, next_word))
                        if number:
                            count = int(number)
                            if count > 5:
                                logger.warning(f"Strategy 1 requested {count} sets (exceeds limit)")
                                return {'1': 0, '2': 0}  # 제한 초과 시 0 반환
                            strategy_counts['1'] = count
                            
                # 전략2/2번전략 처리
                elif any(pattern in current_word for pattern in ["전략2", "2번전략", "2번"]):
                    if i + 1 < len(words):
                        next_word = words[i + 1]
                        number = ''.join(filter(str.isdigit, next_word))
                        if number:
                            count = int(number)
                            if count > 5:
                                logger.warning(f"Strategy 2 requested {count} sets (exceeds limit)")
                                return {'1': 0, '2': 0}  # 제한 초과 시 0 반환
                            strategy_counts['2'] = count
                
                i += 1
            
            total_sets = sum(strategy_counts.values())
            if total_sets > 5:
                logger.warning(f"Total sets {total_sets} exceeds limit")
                return {'1': 0, '2': 0}  # 전체 세트 수 제한 초과 시 0 반환
                
            logger.info(f"Processed strategy counts: {strategy_counts}")
            logger.info(f"Total sets requested: {total_sets}")
            
            return strategy_counts
                
        except Exception as e:
            logger.error(f"Error processing strategy counts: {e}")
            return strategy_counts

    def _format_recommendations(self, recommendations, strategy_num=None, num_sets=None):
        """Format lottery number recommendations with better readability"""
        # 전략별로 번호를 분류
        strategy1_sets = []
        strategy2_sets = []
        
        for strategy, numbers in recommendations:
            if strategy == 1:
                strategy1_sets.append(f"□ {len(strategy1_sets)+1}세트: {', '.join(map(str, numbers))}")
            else:
                strategy2_sets.append(f"□ {len(strategy2_sets)+1}세트: {', '.join(map(str, numbers))}")
        
        formatted_message = ""
        
        # 전략 1 결과가 있으면 추가
        if strategy1_sets:
            formatted_message += """[전략 1: 자주 당첨된 번호 기반 추천]

====================================

{}

====================================""".format('\n'.join(strategy1_sets))

        # 두 전략 모두 있으면 구분선 추가
        if strategy1_sets and strategy2_sets:
            formatted_message += "\n\n"

        # 전략 2 결과가 있으면 추가
        if strategy2_sets:
            formatted_message += """[전략 2: 잠재력 있는 번호 기반 추천]

====================================

{}

====================================""".format('\n'.join(strategy2_sets))

        # 행운 메시지 추가
        lucky_message = random.choice(self.lucky_messages)
        formatted_message += f"\n\n▶ {lucky_message}"
        
        return formatted_message

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            logger.info(f"Received message: {user_message}")

            if not user_message:
                return JsonResponse({'response': '메시지를 입력해주세요.'}, status=400)

            # 전략 키워드가 있는 경우 GPT 응답 스킵하고 바로 번호 추천 처리
            if "전략" in user_message.lower():
                try:
                    strategy_counts = self._process_strategy_counts(user_message)
                    total_sets = sum(strategy_counts.values())

                    if total_sets == 0:
                        return JsonResponse({
                            'response': '최대 5세트까지 추천가능합니다.\n세트 수를 정확히 입력해주세요. (예: "전략1로 3세트 추천해주세요")'
                        }, status=400)
                    
                    if total_sets > 5:
                        return JsonResponse({
                            'response': '죄송합니다. 최대 5세트까지만 추천 가능합니다.\n전략1과 전략2를 조합해서 5세트를 추천해드릴까요?\n(예: "전략1 3세트, 전략2 2세트")'
                        }, status=200)

                    recommendations, error = get_recommendation(strategy_counts)
                    
                    if error:
                        return JsonResponse({'response': error}, status=400)

                    if not recommendations:
                        return JsonResponse({'response': '번호 추천 중 오류가 발생했습니다.'}, status=400)

                    # 번호 추천 결과만 반환
                    response_message = self._format_recommendations(recommendations)
                    
                    # # Chathistory DB저장 추가
                    # serializer = ChatHistorySerializer(data=request.data)
                    # if request.user.is_authenticated:
                    #     if serializer.is_valid():
                    #         serializer.save(user=request.user, user_message=user_message, bot_response=response_message)
                    #         print("db저장 성공 -> chathistory")
                    
                    # Recommendation DB저장 추가
                    import re
                    
                    pattern_num = r"□ \d+세트: ([\d, ]+)"
                    matches_num = re.findall(pattern_num, response_message)
                    
                    pattern_strategy = r"전략 (\d+):"
                    match_strategy = re.search(pattern_strategy, response_message)
                    strategy = match_strategy.group(1)
                    
                    for match in matches_num:
                        data_strategy = {"strategy": strategy, "numbers": match}
                        serializer_recomend = RecommendationHistorySerializer(data=data_strategy)
                        
                        if request.user.is_authenticated:
                            if serializer_recomend.is_valid():
                                serializer_recomend.save(user=request.user)
                                print("db저장 성공 -> recommend")
                            else:
                                print("유효성 검사 실패:", serializer_recomend.errors)
                    
                    return JsonResponse({'response': response_message}, status=200)
                    
                except Exception as e:
                    logger.error(f"Error in processing strategy: {str(e)}")
                    return JsonResponse({
                        'response': '번호 추천 처리 중 오류가 발생했습니다.'
                    }, status=400)
            
            # 전략 키워드가 없는 경우만 GPT 응답 처리
            else:
                try:
                    assistant_message = self._get_gpt_response(user_message)
                    
                    serializer = ChatHistorySerializer(data=request.data)
                    if request.user.is_authenticated:
                        if serializer.is_valid():
                            serializer.save(user=request.user, user_message=user_message, bot_response=assistant_message)
                            print("db저장 성공")
                            
                    return JsonResponse({'response': assistant_message}, status=200)
                except Exception as e:
                    logger.error(f"GPT Error: {str(e)}")
                    return JsonResponse({'response': str(e)}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'response': '잘못된 요청 형식입니다.'}, status=400)
        except Exception as e:
            logger.error(f"Error in ChatAPIView: {str(e)}")
            return JsonResponse({
                'response': '서버 에러가 발생했습니다. 잠시 후 다시 시도해주세요.'
            }, status=500)
        

# Mypage get요청 수행하는 로직
# ChatAPIView 클래스 다음에 추가
class HistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 최신 당첨 정보 가져오기
            latest_draw = LottoDraw.objects.order_by('-round_no').first()
            
            # 사용자의 추천 기록 가져오기
            recommendations = Recommendation.objects.filter(user=request.user).order_by('-recommendation_date')
            
            if latest_draw:
                latest_numbers = list(map(int, latest_draw.winning_numbers.split(',')))
                
                # 확인하지 않은 추천번호들 업데이트
                for rec in recommendations:
                    if not rec.is_checked:
                        rec_numbers = list(map(int, rec.numbers.split(',')))
                        matched = len(set(rec_numbers) & set(latest_numbers))
                        
                        rec.is_won = matched >= 3 # 3개 이상 맞으면 당첨
                        rec.is_checked = True    # 확인 완료 표시
                        rec.draw_round = latest_draw.round_no # 확인한 회차 저장
                        rec.draw_date = latest_draw.draw_date # 확인한 날짜 저장
                        rec.save()

            serializer = RecommendationHistorySerializer(recommendations, many=True)
            
            response_data = {
                'recommendations': serializer.data,
                'latest_draw': {
                    'round': latest_draw.round_no if latest_draw else None,
                    'date': latest_draw.draw_date if latest_draw else None,
                    'numbers': latest_draw.winning_numbers if latest_draw else None,
                    'bonus': latest_draw.bonus_number if latest_draw else None
                } if latest_draw else None
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SaveDBAPIView(APIView):
    def get(self, request):
        df = pd.read_csv("data/lotto_history.csv")

        for col in ['1', '2', '3', '4', '5', '6']:
            df[col] = df[col].astype(float).astype(int)
        df['추첨일'] = df['추첨일'].apply(lambda x: datetime.strptime(x, "%Y.%m.%d").strftime("%Y-%m-%d"))
        df = df.sort_values(by='회차', ascending=True)


        for _, row in df.iterrows():
            if not LottoDraw.objects.filter(round_no=int(row['회차'])).exists():
                LottoDraw.objects.create(
                    round_no=int(row['회차']),
                    draw_date=row['추첨일'],
                    winning_numbers=",".join(map(str, [row['1'], row['2'], row['3'], row['4'], row['5'], row['6']])),
                    bonus_number=int(row['보너스'])
                )
                print(f"회차 {row['회차']} DB에 저장 완료!")
            
        # LottoDraw.objects.filter(round_no=1159).delete()
        # print("1159회차 삭제 완료!")
        return Response({"msg": "DB저장 성공!"})
    
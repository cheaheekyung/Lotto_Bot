from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from chatbot.services import LottoDataCollector
from chatbot.models import Recommendation, LottoDraw
from rest_framework.views import APIView
from chatbot.serializers import MypageSerializer
from rest_framework.response import Response

@login_required
def main_view(request):
    # 최신 당첨 번호 가져오기
    collector = LottoDataCollector()
    latest_numbers = None
    try:
        df = collector.collect_initial_data()
        if df is not None and not df.empty:
            latest_numbers = {
                'round': df.iloc[0]['회차'],
                'date': df.iloc[0]['추첨일'],
                'numbers': [
                    df.iloc[0]['1'],
                    df.iloc[0]['2'],
                    df.iloc[0]['3'],
                    df.iloc[0]['4'],
                    df.iloc[0]['5'],
                    df.iloc[0]['6']
                ],
                'bonus': df.iloc[0]['보너스']
            }
    except Exception as e:
        print(f"Error fetching latest numbers: {e}")

    context = {
        'latest_numbers': latest_numbers
    }
    return render(request, 'lottobot/main.html', context)

class MypageAPIView(APIView):
    
    def get(self, request):
        recommendations = Recommendation.objects.filter(user=request.user).order_by('-created_at')[:10]  # 최근 10개
        
        data = []
        
        for recommendation in recommendations:
            # gte : greater than or equal to
            lotto_draw  = LottoDraw.objects.filter(draw_date__gte=recommendation.created_at.date()).order_by('draw_date').first()
            
            draw_date = lotto_draw .draw_date if lotto_draw  else "아직 추천이후 최신회차가 진행되지 않았습니다."
            
            rank = "미당첨"
            if lotto_draw:
                recommended_numbers = set(recommendation.numbers.split(','))
                winning_numbers = set(lotto_draw.winning_numbers.replace(" ","").split(','))
                bonus_number = str(lotto_draw.bonus_number)
                
                matched_count = len(recommended_numbers & winning_numbers)
                
                if matched_count == 6:
                    rank = "1등"
                elif matched_count == 5 and bonus_number in recommended_numbers:
                    rank = "2등"
                elif matched_count == 5:
                    rank = "3등"
                elif matched_count == 4:
                    rank = "4등"
                elif matched_count == 3:
                    rank = "5등"
            
            data.append({
                "created_at": recommendation.created_at,
                "strategy": recommendation.strategy,
                "numbers": recommendation.numbers,
                "draw_date": draw_date,
                "is_prized": rank
            })
        
        serializer = MypageSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
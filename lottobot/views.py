from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from chatbot.services import LottoDataCollector
from chatbot.models import Recommendation, LottoDraw
from rest_framework.views import APIView
from chatbot.serializers import MypageSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from chatbot.models import LottoDraw

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


class MainpageAPIView(APIView):
    permission_classes = [AllowAny]     # 메인페이지 로그인해야 볼수있게할건지?? 거기에맞게 수정만하면됨 일단 다 가능하게해둠
    
    def get(self, request):
        lottodraw = LottoDraw.objects.order_by('-round_no').first()
        if not lottodraw:
            return Response({"message": "DB에 로또데이터가 없습니다."})
        nums = lottodraw.winning_numbers.split(',')
        data = {
            "회차": lottodraw.round_no,
            "추첨 일자": lottodraw.draw_date,
            "번호1": nums[0],
            "번호2": nums[1],
            "번호3": nums[2],
            "번호4": nums[3],
            "번호5": nums[4],
            "번호6": nums[5],
            "보너스번호": lottodraw.bonus_number,
        }
        return Response(data)

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
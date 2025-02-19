from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from . models import LottoDraw
import pandas as pd


class SaveDBAPIView(APIView):
    def get(self, request):
        df = pd.read_csv("data/lotto_history.csv")

        for col in ['1', '2', '3', '4', '5', '6']:
            df[col] = df[col].astype(float).astype(int)
        df['추첨일'] = df['추첨일'].apply(lambda x: datetime.strptime(x, "%Y.%m.%d").strftime("%Y-%m-%d"))


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

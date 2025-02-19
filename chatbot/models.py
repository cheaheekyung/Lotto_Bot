from django.db import models

class LottoDraw(models.Model):
    round_no = models.IntegerField(unique=True, primary_key=True)  # 회차 번호
    draw_date = models.DateField()                                 # 추첨 날짜
    winning_numbers = models.CharField(max_length=50)              # 당첨 번호 (쉼표로 구분)
    bonus_number = models.IntegerField()                           # 보너스 번호

    def __str__(self):
        return f"회차: {self.round_no}, 날짜: {self.draw_date}"

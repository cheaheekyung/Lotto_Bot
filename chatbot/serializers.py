# chatbot/serializers.py
from rest_framework import serializers
from .models import LottoDraw, Recommendation, ChatHistory

class LottoDrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = LottoDraw
        fields = ['id', 'round_no', 'draw_date', 'winning_numbers', 'bonus_number']

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = "__all__"
        read_only_fields = ['user', 'created_at',]



class ChatHistorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ChatHistory
        fields = "__all__"
        read_only_fields = ("user_message", "bot_response", "user")


class MypageSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField()  
    strategy = serializers.CharField() 
    numbers = serializers.CharField()
    draw_date = serializers.CharField()
    is_prized = serializers.CharField()
    

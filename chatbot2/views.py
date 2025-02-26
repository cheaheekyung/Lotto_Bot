from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import create_response




class ChatAPIView(APIView):
    
    def post(self, request):
        message = request.data.get("message")
        if not message:
            return Response(
                {"error": "message is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        
        response = create_response(message)
        return Response({"message": message, "response": response})

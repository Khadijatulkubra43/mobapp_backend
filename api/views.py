from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
import os
import cv2
import numpy as np
from .apply_makup_script import apply_makeup, calculate_look_score
from .models import looks, current_look_indices
from .serializers import CustomRegisterSerializer

class IsLoggedin(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(
            {},
            status= status.HTTP_204_NO_CONTENT
        )

class GetUserName(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
         first_name = request.user.first_name
         last_name = request.user.last_name
         username = request.user.username
         return Response({
            "username": username,
            "firstname": first_name,
            "lastname": last_name,
        }, status=status.HTTP_200_OK)

class ImageUploadView(APIView):
    """
    API view to upload and resize an image and return it directly as a response.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        # Check if a file is provided
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']

        try:
            # Read the uploaded file using OpenCV
            file_bytes = uploaded_file.read()
            nparr = np.frombuffer(file_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return Response({'error': 'Invalid image format.'}, status=status.HTTP_400_BAD_REQUEST)

            # Resize the image
            resized_img = cv2.resize(img, (380, 380))

            # Apply makeup filters (example process)
            imgs_with_makeup = []
            look_scores = []
            for idx in current_look_indices:
                img_with_makeup = apply_makeup(resized_img, looks[idx])
                if img_with_makeup is not None:
                    imgs_with_makeup.append(img_with_makeup)
                    look_scores.append(calculate_look_score(img_with_makeup))

            # Select the best look
            best_suggestion_idx = np.argmax(look_scores)
            final_img = imgs_with_makeup[best_suggestion_idx]

            # Encode the final image to JPEG
            success, encoded_image = cv2.imencode('.jpg', final_img)
            if not success:
                return Response({'error': 'Error encoding the image.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Return the encoded image as an HTTP Response
            return HttpResponse(encoded_image.tobytes(), content_type='image/jpeg')

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomRegisterView(APIView):
    """
    Custom registration view to display proper validation errors in the response.
    """
    permission_classes = [AllowAny]
    serializer_class = CustomRegisterSerializer

    def post(self, request, *args, **kwargs):
        # Instantiate the serializer with incoming request data
        serializer = self.serializer_class(data=request.data)

        # Validate the serializer
        if serializer.is_valid():
            user = serializer.save(request)  # Save user
            return Response({
            }, status=status.HTTP_204_NO_CONTENT)

        # Return error response with detailed validation messages
        return Response(serializer.errors
        , status=status.HTTP_400_BAD_REQUEST)
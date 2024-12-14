from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.parsers import FileUploadParser
from django.core.files.storage import default_storage
from django.conf import settings
import os
import cv2
import numpy as np
from .apply_makup_script import apply_makeup, calculate_look_score
from .models import looks, current_look_indices

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
    API view to upload and resize an image.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Use parsers for multipart requests
    
    def post(self, request, *args, **kwargs):
        # Check if a file is provided
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the uploaded file
        uploaded_file = request.FILES['file']

        try:
            # Read the uploaded file using OpenCV
            file_bytes = uploaded_file.read()
            nparr = np.frombuffer(file_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Check if image is valid
            if img is None:
                return Response({'error': 'Invalid image format.'}, status=status.HTTP_400_BAD_REQUEST)

            # Resize the image (example: width=380, height=380)
            resized_img = cv2.resize(img, (380, 380))

            # Apply makeup filters to 3 different looks
            imgs_with_makeup = []
            look_scores = []
            for idx in current_look_indices:
                img_with_makeup = apply_makeup(resized_img, looks[idx])
                if img_with_makeup is not None:
                    imgs_with_makeup.append(img_with_makeup)
                    # Calculate score for each look
                    look_score = calculate_look_score(img_with_makeup)
                    look_scores.append(look_score)

            # # Select the look with the highest score as the "best suggestion"
            best_suggestion_idx = np.argmax(look_scores)

            # Save the resized image to the uploads directory
            output_filename = f"best_{uploaded_file.name}"
            output_path = os.path.join('uploads', output_filename)

            # Convert resized image back to file format and save
            success, encoded_image = cv2.imencode('.jpg', imgs_with_makeup[best_suggestion_idx])
            if not success:
                return Response({'error': 'Error encoding the image.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Save to storage
            with default_storage.open(output_path, 'wb') as file:
                file.write(encoded_image.tobytes())

            # Build the URL for accessing the file
            file_url = os.path.join(settings.MEDIA_URL, output_path)

            # Return the URL of the resized image
            return Response({'url': request.build_absolute_uri(file_url)}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

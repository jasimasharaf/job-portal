from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from authentication.serializer import ProfileSerializer, ProfileUpdateSerializer
from authentication.models import UserProfile

class ProfileDisplayAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get or create user profile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            serializer = ProfileSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'Failed to get profile: {str(e)}',
                'user_authenticated': request.user.is_authenticated,
                'user_id': request.user.id if request.user.is_authenticated else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request):
        try:
            # Check if user has a profile
            if not hasattr(request.user, 'userprofile'):
                return Response({
                    'detail': 'User profile not found',
                    'code': 'profile_not_found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                updated_profile = ProfileSerializer(request.user)
                return Response({
                    'message': 'Profile updated successfully',
                    'data': updated_profile.data
                }, status=status.HTTP_200_OK)
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Profile update error: {str(e)}")
            return Response({'error': f'Failed to update profile: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        return self.patch(request)
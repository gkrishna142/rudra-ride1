"""
Custom JWT Authentication for FrontendUser model
This allows JWT tokens to authenticate against the FrontendUser model instead of Django's default User model.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from .models import User as FrontendUser


class FrontendUserJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that uses FrontendUser model instead of Django's default User model.
    This is needed because tokens contain user_id from FrontendUser, not from auth_user table.
    """
    
    def get_user(self, validated_token):
        """
        Override to get user from FrontendUser model instead of default User model.
        """
        try:
            user_id = validated_token.get('user_id')
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')

        if user_id is None:
            raise InvalidToken('Token contained no user_id')

        try:
            # Look up user in FrontendUser model (frontend_user table)
            user = FrontendUser.objects.get(id=user_id)
        except FrontendUser.DoesNotExist:
            raise AuthenticationFailed('User not found', code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed('User is inactive', code='user_inactive')

        return user


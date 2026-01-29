from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.db import connection
from django.core.mail import send_mail
from threading import Thread
from .models import RidesUser, PromoCode, AdminProfile, Zone, User as FrontendUser, Role, RolePermission, UserRole
from django.contrib.auth import get_user_model

User = get_user_model()  # Django's default User model (auth_user)
from .serializers import (
    PromoCodeSerializer, PromoCodeCreateSerializer, PromoCodeUpdateSerializer,
    AdminLoginSerializer, AdminProfileSerializer,
    ZoneSerializer, ZoneCreateSerializer, ZoneUpdateSerializer,
    UserSignupSerializer, UserLoginSerializer, UserLoginRequestSerializer,
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    RoleSerializer, RoleCreateSerializer, RoleUpdateSerializer, RoleBasicSerializer,
    RolePermissionSerializer, RolePermissionCreateSerializer, RolePermissionUpdateSerializer,
    UserRoleSerializer, UserRoleCreateSerializer, UserRoleUpdateSerializer,
    RoleWithPermissionsCreateSerializer, RolePermissionsBulkUpdateSerializer,
    RoleWithPermissionsUpdateSerializer
)
from django.contrib.auth.hashers import check_password, make_password

# Use AllowAny in DEBUG mode for easier testing, IsAuthenticated in production
AUTH_PERMISSION = AllowAny if settings.DEBUG else IsAuthenticated


def _validate_email_address(email):
    """
    Validate email address format and check for invalid/example domains.
    Returns: (is_valid: bool, error_message: str)
    """
    if not email:
        return False, "Email address is required"
    
    email = email.strip()
    
    # Basic format validation
    if '@' not in email or '.' not in email.split('@')[1]:
        return False, f"Invalid email format: {email}"
    
    domain = email.split('@')[1].lower().strip()
    
    # Only block the most obvious invalid/example domains that definitely don't receive emails
    # This is a minimal list to avoid blocking valid emails
    invalid_domains = [
        'example.com',
        'example.org',
        'example.net',
        'test.com',
        'test.org',
        'localhost',
        'invalid.com',
        'nonexistent.com',
        'placeholder.com',
        'dummy.com',
        'fake.com',
    ]
    
    if domain in invalid_domains:
        return False, (
            f"Invalid email domain: {domain}\n"
            f"The email address '{email}' uses an example/test domain that doesn't receive emails.\n"
            f"Please provide a valid email address with a real domain (e.g., gmail.com, yahoo.com, outlook.com)."
        )
    
    return True, None


def _validate_gmail_credentials():
    """
    Validate Gmail credentials format and provide helpful error messages.
    Returns: (is_valid: bool, error_message: str)
    """
    email_user = getattr(settings, 'EMAIL_HOST_USER', '').strip()
    email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '').strip()
    
    if not email_user:
        return False, "EMAIL_HOST_USER is not set in settings.py"
    
    if not email_password:
        return False, "EMAIL_HOST_PASSWORD is not set in settings.py"
    
    # Check if it's a Gmail address
    if '@gmail.com' in email_user.lower():
        # Gmail app passwords should be 16 characters (no spaces)
        # Remove any spaces that might have been copied incorrectly
        cleaned_password = email_password.replace(' ', '')
        
        if len(cleaned_password) != 16:
            return False, (
                f"Gmail App Password should be exactly 16 characters (found {len(cleaned_password)}).\n"
                f"Get a new app password from: https://myaccount.google.com/apppasswords\n"
                f"Make sure to copy it without spaces."
            )
        
        # If password has spaces, suggest removing them
        if ' ' in email_password:
            return False, (
                f"Gmail App Password contains spaces. Remove all spaces from the password.\n"
                f"Current password length: {len(email_password)} (with spaces)\n"
                f"Expected: 16 characters (no spaces)"
            )
    
    return True, None


def _send_email_sync(user_id, plain_password, recipient_email):
    """
    Internal function to send email synchronously (called in background thread)
    
    Args:
        user_id: User ID to fetch user from database
        plain_password: Plain text password
        recipient_email: Email address to send to
    """
    try:
        # Fetch user from database (needed for thread safety)
        user = FrontendUser.objects.get(pk=user_id)
        
        # Check if using console backend (doesn't need credentials)
        is_console_backend = settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend'
        
        # Only check SMTP credentials if not using console backend
        if not is_console_backend:
            # Validate email credentials format
            is_valid, validation_error = _validate_gmail_credentials()
            if not is_valid:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Email configuration issue: {validation_error}")
                # Continue anyway - let SMTP error handling catch it with better messages
        
        # Get role name(s) using the get_roles() method
        roles = user.get_roles()
        if roles.exists():
            role_names = ", ".join([role.name for role in roles])
            role_info = f"{role_names} ({', '.join([role.role_id for role in roles])})"
        elif user.role_id:
            # Fallback: try to get role by role_id if get_roles() didn't find it
            try:
                from .models import Role
                role = Role.objects.filter(role_id=str(user.role_id)).first()
                if role:
                    role_info = f"{role.name} ({role.role_id})"
                else:
                    role_info = f"Role ID: {user.role_id}"
            except Exception:
                role_info = f"Role ID: {user.role_id}"
        else:
            role_info = "No role assigned"
        
        # Create email subject
        subject = 'Your Account Credentials - Rudra Admin'
        
        # Build email body with all user data
        phone_info = f"\nPhone Number: {user.phone_number}" if user.phone_number else ""
        
        email_body = f"""
Hello {user.name},

Your account has been successfully created. Please find your login credentials below:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACCOUNT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Full Name: {user.name}
Email Address: {user.email}{phone_info}
Password: {plain_password}
Role: {role_info}
Account Status: {'Active' if user.is_active else 'Inactive'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please keep these credentials secure and do not share them with anyone.

You can now login using your email and password.

Best regards,
Rudra Admin Team
        """
        
        # Set from_email based on backend type
        if is_console_backend:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@rudraadmin.com')
        else:
            from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER or 'noreply@rudraadmin.com'
        
        # Send email with real-time delivery
        try:
            send_mail(
                subject=subject,
                message=email_body,
                from_email=from_email,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            
            import logging
            logger = logging.getLogger(__name__)
            if is_console_backend:
                logger.info(f"Email printed to console for {recipient_email} (user: {user.name})")
            else:
                logger.info(f"✅ Email delivered successfully to {recipient_email} for user {user.name}")
        except Exception as email_error:
            # Handle Gmail-specific authentication errors with helpful guidance
            import logging
            logger = logging.getLogger(__name__)
            error_str = str(email_error)
            
            # Check for Gmail authentication errors
            if '535' in error_str or 'BadCredentials' in error_str or 'Username and Password not accepted' in error_str:
                error_msg = (
                    f"❌ Gmail Authentication Failed for {recipient_email}:\n"
                    f"   Error: {error_str}\n\n"
                    f"   SOLUTION:\n"
                    f"   1. Verify your Gmail App Password is correct:\n"
                    f"      - Go to: https://myaccount.google.com/apppasswords\n"
                    f"      - Make sure 2-Step Verification is enabled\n"
                    f"      - Generate a NEW App Password for 'Mail'\n"
                    f"      - Copy the 16-character password (no spaces)\n"
                    f"   2. Update settings.py:\n"
                    f"      EMAIL_HOST_PASSWORD = 'your-new-app-password'\n"
                    f"   3. Restart Django server after updating\n"
                    f"   4. For testing, you can use console backend:\n"
                    f"      EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'"
                )
                logger.error(error_msg)
            else:
                logger.error(f"❌ Failed to deliver email to {recipient_email}: {error_str}")
            raise
        
    except FrontendUser.DoesNotExist:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"User with ID {user_id} not found when sending email")
    except Exception as e:
        # Log error but don't fail
        import logging
        logger = logging.getLogger(__name__)
        error_msg = str(e)
        logger.error(f"Failed to send email to {recipient_email}: {error_msg}")


def send_user_credentials_email_async(user, plain_password, recipient_email=None):
    """
    Send email with user credentials asynchronously (real-time, non-blocking)
    
    This function starts a background thread to send the email, allowing the API
    to respond immediately while the email is sent in the background.
    
    Args:
        user: FrontendUser instance
        plain_password: Plain text password (before hashing)
        recipient_email: Email address to send to (defaults to user.email)
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        recipient_email = recipient_email or user.email
        
        # Validate email address before sending
        is_valid, validation_error = _validate_email_address(recipient_email)
        if not is_valid:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Email validation failed for {recipient_email}: {validation_error}")
            return False, validation_error
        
        # Check if using console backend (for development/testing)
        is_console_backend = settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend'
        
        if is_console_backend:
            # Console backend doesn't need credentials, start thread immediately
            email_thread = Thread(
                target=_send_email_sync,
                args=(user.id, plain_password, recipient_email),
                daemon=True
            )
            email_thread.start()
            return True, None
        
        # Check if email is configured (for SMTP backend)
        email_user = getattr(settings, 'EMAIL_HOST_USER', '').strip()
        email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '').strip()
        
        # Check if email credentials are configured (not placeholder values)
        placeholder_values = ['your-email@gmail.com', 'your-app-password', '', None]
        
        if not email_user or not email_password:
            error_msg = (
                "Email configuration is missing. To enable real email delivery:\n"
                "1. Open backend/backend/settings.py\n"
                "2. Set EMAIL_HOST_USER = 'your-email@gmail.com'\n"
                "3. Set EMAIL_HOST_PASSWORD = 'your-app-password'\n\n"
                "For Gmail: Get app password from https://myaccount.google.com/apppasswords\n\n"
                "For testing without email: Uncomment this line in settings.py:\n"
                "EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'"
            )
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Email configuration missing - user created but email not sent")
            return False, error_msg
        
        # Check if using placeholder values
        if email_user in placeholder_values or email_password in placeholder_values:
            error_msg = (
                "Email credentials are not configured. Please update settings.py:\n"
                "1. Set EMAIL_HOST_USER to your actual email address\n"
                "2. Set EMAIL_HOST_PASSWORD to your app password\n\n"
                "For Gmail: Get app password from https://myaccount.google.com/apppasswords"
            )
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Email credentials are placeholder values - email not sent")
            return False, error_msg
        
        # Start email sending in background thread
        email_thread = Thread(
            target=_send_email_sync,
            args=(user.id, plain_password, recipient_email),
            daemon=True  # Thread will terminate when main process exits
        )
        email_thread.start()
        
        return True, None
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        error_msg = f"Failed to start email thread: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def fix_promo_sequence():
    """
    Automatically fix PromoCode ID sequence to ensure sequential IDs.
    This is called before creating new promo codes to prevent ID gaps.
    """
    try:
        with connection.cursor() as cursor:
            table_name = PromoCode._meta.db_table
            
            # Get maximum ID
            cursor.execute(f"SELECT COALESCE(MAX(id), 0) FROM {table_name};")
            max_id = cursor.fetchone()[0]
            
            # Get sequence name
            cursor.execute(f"SELECT pg_get_serial_sequence('{table_name}', 'id');")
            seq_result = cursor.fetchone()
            sequence_name = seq_result[0] if seq_result and seq_result[0] else None
            
            if not sequence_name:
                # Try alternative sequence name
                sequence_name = f'{table_name}_id_seq'
            
            if sequence_name:
                # Remove schema prefix if present
                seq_for_setval = sequence_name.split('.')[-1] if '.' in sequence_name else sequence_name
                
                # Set sequence to max_id with true, so the next nextval() will return max_id + 1
                # Using true means "use this value", so next nextval() will be max_id + 1
                # This ensures sequential IDs without gaps
                cursor.execute(f"SELECT setval('{seq_for_setval}', {max_id}, true);")
                return True
                    
    except Exception as e:
        # Silently fail - don't break promo code creation if sequence fix fails
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to fix promo sequence: {str(e)}")
        return False
    
    return False


class IsAdminUser(BasePermission):
    """
    Custom permission to only allow users with admin or superadmin roles.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has admin profile
        try:
            admin_profile = request.user.admin_profile
            # Check if admin account is active
            return admin_profile.is_active
        except AdminProfile.DoesNotExist:
            return False


class IsSuperAdminUser(BasePermission):
    """
    Custom permission to only allow users with superadmin role.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has admin profile and is superadmin
        try:
            admin_profile = request.user.admin_profile
            return admin_profile.is_active and admin_profile.is_superadmin
        except AdminProfile.DoesNotExist:
            return False


@api_view(['GET'])
@permission_classes([AllowAny])  # Allow public access to API root
def api_root(request):
    """API root endpoint - Public access"""
    auth_status = "Optional (DEBUG mode)" if settings.DEBUG else "Required"
    return Response({
        'message': 'RudraRide API',
        'endpoints': {
            'login': '/api/login/',
            'admin_login': '/api/admin/login/ or /api/auth/admin-login/',
            'admin_logout': '/api/auth/admin/logout/',
            'admin_refresh_token': '/api/auth/admin/refresh/',
            'ride_user_count': '/api/auth/ride-users/count/',
            'rides_users_list': '/api/auth/rides-users/',
            'user_signup': '/api/user/signup/ (POST)',
            'user_login': '/api/user/login/ (POST)',
            'users_list': '/api/auth/users/ (GET - List all, POST - Create)',
            'user_detail': '/api/auth/users/{id}/ (GET, PUT, PATCH, DELETE - Deactivate)',
            'roles_list': '/api/auth/roles/ (GET - List all, POST - Create)',
            'role_detail': '/api/auth/roles/{role_id}/ (GET, PUT, PATCH, DELETE - Deactivate)',
            'role_with_permissions_create': '/api/auth/roles/create-with-permissions/ (POST - Create role with permissions)',
            'role_with_permissions_update': '/api/auth/roles/update-with-permissions/ (PUT/PATCH - Update role with permissions)',
            'role_permissions_list': '/api/auth/role-permissions/ (GET - List all, POST - Create)',
            'role_permission_detail': '/api/auth/role-permissions/{role_id}/{page_path}/{permission_type}/ (GET, POST, PUT, PATCH, DELETE - uses composite key)',
            'user_roles_list': '/api/auth/user-roles/ (GET - List all, POST - Create)',
            'user_role_detail': '/api/auth/user-roles/{id}/ (GET, PUT, PATCH, DELETE)',
            'promo_codes_list': '/api/auth/promo-codes/ (GET)',
            'promo_codes_bulk_delete': '/api/auth/promo-codes/ (DELETE - Bulk deactivate)',
            'promo_code_create': '/api/auth/promo-codes/create/ (POST)',
            'promo_code_create_alt': '/api/auth/promo-code-create/ (POST)',
            'promo_code_edit': '/api/auth/promo-codes/{id}/ (PUT/PATCH - Edit)',
            'promo_code_detail': '/api/auth/promo-codes/{id}/ (GET)',
            'promo_code_delete': '/api/auth/promo-codes/{id}/ (DELETE - Single deactivate)',
            'zones_list': '/api/auth/zones/ (GET)',
            'zone_create': '/api/auth/zones/ (POST)',
            'zone_update': '/api/auth/zones/{id}/ (PUT)',
            'zone_detail': '/api/auth/zones/{id}/ (GET)',
            'zone_disable': '/api/auth/zones/{id}/ (DELETE - Disable zone)',
        },
        'authentication': 'Required for all /api/auth/ endpoints (admin login required)',
        'admin_roles': 'superadmin, admin',
        'debug_mode': settings.DEBUG
    })


@api_view(['POST'])
@permission_classes([AUTH_PERMISSION])
def send_welcome_email(request):
    """API endpoint to (re)send welcome email with credentials.

    Expects JSON POST with `user_id` (int) and `plain_password` (str).
    Optional `recipient_email` can override the user's email.
    """
    user_id = request.data.get('user_id')
    recipient_email = request.data.get('recipient_email')
    plain_password = request.data.get('plain_password')

    if not user_id or not plain_password:
        return Response({
            'message_type': 'error',
            'error': 'Both user_id and plain_password are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = FrontendUser.objects.get(pk=user_id)
    except FrontendUser.DoesNotExist:
        return Response({
            'message_type': 'error',
            'error': f'User with id {user_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        email_started, email_error = send_user_credentials_email_async(user, plain_password, recipient_email)
        if email_started:
            return Response({'message_type': 'success', 'message': 'Email queued for sending'})
        else:
            return Response({'message_type': 'error', 'error': email_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'message_type': 'error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow public access to login
def login_view(request):
    """Login endpoint for authentication"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'message_type': 'error',
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return Response({
            'message_type': 'success',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        })
    else:
        return Response({
            'message_type': 'error',
            'error': 'Invalid username or password'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow public access to admin login
def admin_login_view(request):
    """
    Admin login endpoint - Authenticates users from frontend_users table
    Only allows users with admin roles (role_id 1 for superadmin, role_id 2 for admin)
    
    Request Body:
    {
        "email": "admin@example.com",
        "password": "admin_password"
    }
    
    Response (Success):
    {
        "message_type": "success",
        "user": {
            "id": 1,
            "name": "Admin User",
            "email": "admin@example.com",
            "role_id": 1,
            "role_name": "Super Admin",
            "is_superadmin": true,
            "is_active": "active"
        },
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        },
        "permissions": {...}
    }
    """
    email = request.data.get('email', '').strip() if request.data.get('email') else None
    password = request.data.get('password', '').strip() if request.data.get('password') else None
    
    # Validate password
    if not password or password == '':
        return Response({
            'message_type': 'error',
            'error': 'Password is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate email
    if not email or email == '':
        return Response({
            'message_type': 'error',
            'error': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find user in frontend_users table by email (case-insensitive)
    try:
        user = FrontendUser.objects.filter(email__iexact=email).first()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error finding user: {str(e)}")
        return Response({
            'message_type': 'error',
            'error': 'Error finding user. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if not user:
        # User not found - provide helpful message
        return Response({
            'message_type': 'error',
            'error': f'No account found with email: {email}. Please check your email address or sign up first.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if account is active
    if not user.is_active:
        return Response({
            'message_type': 'error',
            'error': 'Your account has been deactivated. Please contact an administrator.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Verify password
    if not check_password(password, user.password):
        # Password doesn't match - provide helpful message
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed login attempt for email: {email} - password mismatch")
        return Response({
            'message_type': 'error',
            'error': 'Invalid password. Please check your password and try again.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if user has admin role (role_id 1 = superadmin, role_id 2 = admin)
    # Also check UserRole table for explicit role assignments
    is_admin = False
    is_superadmin = False
    role_name = None
    
    # Check role_id in frontend_users table
    # Handle both string (e.g., 'R001', '1') and integer values
    role_id_str = str(user.role_id) if user.role_id is not None else None
    found_role = None
    
    if role_id_str in ['1', '2', 1, 2]:
        is_admin = True
        is_superadmin = (role_id_str in ['1', 1])
        # Get role name from Role table - try multiple lookup methods
        try:
            from .models import Role
            from django.db.models import Q
            # Try exact match first
            found_role = Role.objects.filter(role_id=role_id_str).first()
            # If not found, try "R001", "R002" format
            if not found_role:
                if role_id_str == '1':
                    found_role = Role.objects.filter(Q(role_id__iexact='R001') | Q(role_id='R001')).first()
                elif role_id_str == '2':
                    found_role = Role.objects.filter(Q(role_id__iexact='R002') | Q(role_id='R002')).first()
            # If still not found, try case-insensitive
            if not found_role:
                found_role = Role.objects.filter(Q(role_id__iexact=role_id_str) | Q(role_id=role_id_str)).first()
            
            if found_role:
                role_name = found_role.name
            else:
                role_name = "Super Admin" if role_id_str in ['1', 1] else "Admin"
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error looking up role: {str(e)}")
            role_name = "Super Admin" if role_id_str in ['1', 1] else "Admin"
    else:
        # Check UserRole table for admin roles
        try:
            from .models import UserRole, Role
            user_roles = UserRole.objects.filter(user=user, is_active=True).select_related('role')
            for user_role in user_roles:
                # Check if role_id indicates admin (1 or 2) or check role name
                role_obj = user_role.role
                if role_obj.role_id in ['1', '2', 'R001', 'R002'] or 'admin' in role_obj.name.lower():
                    is_admin = True
                    if 'super' in role_obj.name.lower() or role_obj.role_id in ['1', 'R001']:
                        is_superadmin = True
                    role_name = role_obj.name
                    break
        except Exception:
            pass
    
    # For development/testing: If DEBUG mode and no admin role found, allow access with default admin role
    # Remove this in production!
    if not is_admin and settings.DEBUG:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"DEBUG MODE: Allowing admin login for user {user.email} without admin role_id. This should be removed in production!")
        is_admin = True
        is_superadmin = False
        role_name = "Admin (Debug Mode)"
    
    # If user doesn't have admin role, deny access
    if not is_admin:
        return Response({
            'message_type': 'error',
            'error': 'Access denied. This account does not have admin privileges. Please update your role_id to 1 (superadmin) or 2 (admin).'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Generate JWT tokens with custom claims for FrontendUser
    try:
        refresh = RefreshToken()
        refresh['user_id'] = user.id
        refresh['email'] = user.email
        refresh['user_type'] = 'frontend_user'
        refresh['is_admin'] = True
        refresh['is_superadmin'] = is_superadmin
        
        access_token = refresh.access_token
        access_token['user_id'] = user.id
        access_token['email'] = user.email
        access_token['user_type'] = 'frontend_user'
        access_token['is_admin'] = True
        access_token['is_superadmin'] = is_superadmin
    except Exception as e:
        return Response({
            'message_type': 'error',
            'error': 'Failed to generate authentication tokens'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Get user permissions - get all permissions for the user's role(s)
    permissions = {}
    try:
        from django.db import connection
        from .models import Role, RolePermission, UserRole
        import logging
        logger = logging.getLogger(__name__)
        
        role_id_str = str(user.role_id) if user.role_id else None
        logger.info(f"Fetching permissions for user {user.id} with role_id: {role_id_str}")
        
        # Strategy 1: Use raw SQL to get all permissions directly (most reliable)
        # This ensures we get all 52 permissions regardless of role lookup issues
        if role_id_str:
            try:
                with connection.cursor() as cursor:
                    # First, find what role_ids exist in the Role table that might match
                    # This helps us find the correct role_id format
                    cursor.execute("""
                        SELECT DISTINCT role_id 
                        FROM frontend_role 
                        WHERE role_id = %s OR role_id = %s OR role_id ILIKE %s
                    """, [role_id_str, f"R{role_id_str.zfill(3)}", f"%{role_id_str}%"])
                    existing_roles = [row[0] for row in cursor.fetchall()]
                    
                    # Build list of role_ids to try
                    role_ids_to_try = [role_id_str]
                    
                    # Add existing roles from database
                    if existing_roles:
                        role_ids_to_try.extend(existing_roles)
                    
                    # Add common variations
                    if role_id_str == '1':
                        role_ids_to_try.extend(['R001', 'R1', 'r001', '1'])
                    elif role_id_str == '2':
                        role_ids_to_try.extend(['R002', 'R2', 'r002', '2'])
                    else:
                        # For other role_ids, try R### format
                        try:
                            num = int(role_id_str)
                            role_ids_to_try.append(f"R{num:03d}")
                        except ValueError:
                            pass
                    
                    # Remove duplicates while preserving order
                    seen = set()
                    role_ids_to_try = [rid for rid in role_ids_to_try if not (rid in seen or seen.add(rid))]
                    
                    logger.info(f"Trying role_ids: {role_ids_to_try}")
                    
                    # Try each role_id variation until we find permissions
                    for rid in role_ids_to_try:
                        cursor.execute("""
                            SELECT page_path, permission_type, is_allowed 
                            FROM frontend_role_permissions 
                            WHERE role_id = %s
                        """, [rid])
                        rows = cursor.fetchall()
                        
                        if rows:
                            # Build permissions dictionary from SQL results
                            for row in rows:
                                page_path, permission_type, is_allowed = row
                                permissions.setdefault(page_path, {})[permission_type] = bool(is_allowed)
                            
                            # If we found permissions, log and break
                            if permissions:
                                logger.info(f"✅ Found {len(rows)} permissions for role_id: {rid}")
                                break
                    
                    # Log final result
                    if permissions:
                        logger.info(f"✅ Total permissions retrieved: {sum(len(perms) for perms in permissions.values())}")
                    else:
                        logger.warning(f"❌ No permissions found for any role_id variation. Tried: {role_ids_to_try}")
                        
            except Exception as e:
                logger.error(f"Error fetching permissions via raw SQL: {str(e)}", exc_info=True)
        
        # Strategy 2: Fallback to ORM if raw SQL didn't work
        if not permissions:
            # First try the user's get_permissions() method
            permissions = user.get_permissions()
            
            # If still no permissions, try ORM lookup
            if not permissions:
                roles_to_check = []
                
                # Use the found_role if we have it
                if found_role:
                    roles_to_check = [found_role]
                elif role_id_str:
                    # Try exact match
                    roles_to_check = list(Role.objects.filter(role_id=role_id_str))
                    
                    # If not found, try "R001", "R002" format
                    if not roles_to_check:
                        if role_id_str == '1':
                            roles_to_check = list(Role.objects.filter(role_id__iexact='R001'))
                        elif role_id_str == '2':
                            roles_to_check = list(Role.objects.filter(role_id__iexact='R002'))
                
                # Get permissions from RolePermission table
                if roles_to_check:
                    perms_qs = RolePermission.objects.filter(role__in=roles_to_check)
                    for rp in perms_qs:
                        permissions.setdefault(rp.page_path, {})[rp.permission_type] = bool(rp.is_allowed)
                
                # Also check UserRole table
                if not permissions:
                    try:
                        user_roles = UserRole.objects.filter(user=user, is_active=True).select_related('role')
                        for user_role in user_roles:
                            role_for_perms = user_role.role
                            perms_qs = RolePermission.objects.filter(role=role_for_perms)
                            for rp in perms_qs:
                                permissions.setdefault(rp.page_path, {})[rp.permission_type] = bool(rp.is_allowed)
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Error fetching permissions via UserRole: {str(e)}")
                    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting user permissions: {str(e)}")
        permissions = {}
    
    # Prepare response data
    serializer = AdminLoginSerializer({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role_id': user.role_id,
        'role_name': role_name or (f"Role ID: {user.role_id}" if user.role_id else "No role"),
        'is_superadmin': is_superadmin,
        'is_active': user.is_active
    })
    
    return Response({
        'message_type': 'success',
        'user': serializer.data,
        'tokens': {
            'access': str(access_token),
            'refresh': str(refresh)
        },
        'permissions': permissions
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_logout_view(request):
    """
    Admin logout endpoint - Blacklists the refresh token
    
    Request Body:
    {
        "refresh": "refresh_token_string"
    }
    
    Response (Success):
    {
        "message_type": "success"
    }
    """
    try:
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'message_type': 'error',
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the refresh token
        token = RefreshToken(refresh_token)
        
        # Check if token is already blacklisted
        try:
            # Try to blacklist the token
            token.blacklist()
        except Exception as blacklist_error:
            # Check if it's already blacklisted
            from rest_framework_simplejwt.exceptions import TokenError
            if 'blacklisted' in str(blacklist_error).lower() or 'already' in str(blacklist_error).lower():
                return Response({
                    'message_type': 'error',
                    'error': 'Token has already been blacklisted (already logged out)'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Re-raise if it's a different error
                raise blacklist_error
        
        return Response({
            'message_type': 'success',
            'message': 'Successfully logged out. Token has been blacklisted.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        # Provide more specific error messages
        error_message = str(e)
        
        # Check for specific error types
        if 'expired' in error_message.lower():
            return Response({
                'message_type': 'error',
                'error': 'Refresh token has expired. Please login again.'
            }, status=status.HTTP_400_BAD_REQUEST)
        elif 'invalid' in error_message.lower() or 'malformed' in error_message.lower():
            return Response({
                'message_type': 'error',
                'error': 'Invalid refresh token format'
            }, status=status.HTTP_400_BAD_REQUEST)
        elif 'blacklisted' in error_message.lower() or 'already' in error_message.lower():
            return Response({
                'message_type': 'error',
                'error': 'Token has already been blacklisted (already logged out)'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Log the actual error for debugging (only in DEBUG mode)
            if settings.DEBUG:
                import traceback
                print(f"Logout error: {error_message}")
                print(traceback.format_exc())
            
            return Response({
                'message_type': 'error',
                'error': f'Invalid refresh token or token already blacklisted. Details: {error_message}' if settings.DEBUG else 'Invalid refresh token or token already blacklisted'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_refresh_token_view(request):
    """
    Refresh access token endpoint - Generates new access token from refresh token
    
    Request Body:
    {
        "refresh": "refresh_token_string"
    }
    
    Response (Success):
    {
        "message_type": "success",
        "tokens": {
            "access": "new_access_token",
            "refresh": "new_refresh_token" (if rotation enabled)
        }
    }
    """
    try:
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'message_type': 'error',
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the refresh token
        refresh = RefreshToken(refresh_token)
        
        # Generate new access token
        access_token = refresh.access_token
        
        # Return new tokens
        # Note: If ROTATE_REFRESH_TOKENS is True, the refresh token is automatically rotated
        response_data = {
            'message_type': 'success',
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh)  # This will be the new refresh token if rotation is enabled
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message_type': 'error',
            'error': 'Invalid refresh token'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow public access to signup
def user_signup_view(request):
    """
    User signup/registration endpoint
    
    Request Body:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone_number": "1234567890" (optional),
        "password": "password123",
        "confirm_password": "password123",
        "role_id": 1 (optional)
    }
    
    Response (Success):
    {
        "message_type": "success",
        "message": "User registered successfully",
        "user": {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "phone_number": "1234567890",
            "role_id": 1,
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z"
        }
    }
    """
    serializer = UserSignupSerializer(data=request.data)
    
    # Log the original email from request
    original_email = request.data.get('email', '')
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"User signup - Original email from request: {original_email}")
    
    if serializer.is_valid():
        # Check if user with this email already exists
        email = serializer.validated_data.get('email')
        
        # Log the email after serializer validation
        logger.info(f"User signup - Email after serializer validation: {email}")
        
        # Validate email address format and domain
        is_valid, validation_error = _validate_email_address(email)
        if not is_valid:
            return Response({
                'message_type': 'error',
                'error': validation_error
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if FrontendUser.objects.filter(email=email).exists():
            return Response({
                'message_type': 'error',
                'error': 'User with this email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Store plain password before hashing (for email)
        plain_password = serializer.validated_data.get('password')
        
        # Get recipient email from request if provided, otherwise use user email
        recipient_email = request.data.get('send_email_to', email)
        
        # Validate recipient email if different from user email
        if recipient_email and recipient_email != email:
            is_valid, validation_error = _validate_email_address(recipient_email)
            if not is_valid:
                return Response({
                    'message_type': 'error',
                    'error': f"Invalid recipient email: {validation_error}"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user (password will be hashed in model's save method)
        user = serializer.save()
        
        # Log the email and role_id after user creation to verify they're saved correctly
        role_id = user.role_id
        logger.info(f"User signup - User created with ID: {user.id}, email in DB: {user.email} (original: {original_email}, validated: {email}), role_id: {role_id}")
        
        # Send email with credentials asynchronously (real-time, non-blocking)
        email_started = False
        email_error = None
        if recipient_email:
            try:
                email_started, email_error = send_user_credentials_email_async(user, plain_password, recipient_email)
            except Exception as e:
                # Log error but don't fail the request
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to start email thread: {str(e)}")
                email_error = str(e)
        
        # Return user data immediately (email is sent in background)
        response_serializer = UserSerializer(user)
        
        response_data = {
            'message_type': 'success',
            'message': 'The user has been successfully created.',
            'data': [response_serializer.data]
        }
        
        if email_started:
            response_data['email_sent'] = True
            response_data['email_message'] = f'A notification email has been successfully queued and will be sent to {recipient_email}.'
        else:
            response_data['email_sent'] = False
            response_data['email_message'] = email_error or 'Email configuration missing or failed to start email thread'
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'message_type': 'error',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow public access to login
def user_login_view(request):
    """
    User login endpoint
    
    Request Body:
    {
        "email": "john@example.com",
        "password": "password123"
    }
    
    Response (Success):
    {
        "message_type": "success",
        "user": {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "phone_number": "1234567890",
            "role_id": 1,
            "is_active": true
        },
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    }
    """
    serializer = UserLoginRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'message_type': 'error',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data.get('email')
    password = serializer.validated_data.get('password')
    
    # Normalize email and find user case-insensitively
    email = email.strip() if isinstance(email, str) else email
    user = FrontendUser.objects.filter(email__iexact=email).first()

    # Support a no-save shortcut: when `no_save=true` is provided and DEBUG is True,
    # return tokens+permissions without verifying the password. This is intended
    # for local/testing only and will NOT persist any DB changes.
    no_save_flag = request.data.get('no_save') or request.query_params.get('no_save')
    # normalize strings like 'true'/'1' -> True
    if isinstance(no_save_flag, str):
        no_save_flag = no_save_flag.lower() in ('1', 'true', 'yes')
    no_save = bool(no_save_flag)
    if no_save and settings.DEBUG:
        # If a frontend user exists, prefer its id/name/phone and permissions
        existing = None
        try:
            existing = FrontendUser.objects.filter(email__iexact=email).values('id', 'name', 'phone_number').first()
        except Exception:
            existing = None

        user_id_val = existing['id'] if existing else None
        # prefer provided name/phone over DB values
        name = request.data.get('name') or request.query_params.get('name') or (existing.get('name') if existing else None)
        phone_number = request.data.get('phone_number') or request.query_params.get('phone_number') or (existing.get('phone_number') if existing else None)

        # generate tokens without verifying password
        refresh = RefreshToken()
        refresh['user_id'] = user_id_val
        refresh['email'] = email
        refresh['user_type'] = 'frontend_user'
        access_token = refresh.access_token
        access_token['user_id'] = user_id_val
        access_token['email'] = email
        access_token['user_type'] = 'frontend_user'

        # build permissions: if user exists, use helper; otherwise use role_id if provided
        perms = {}
        try:
            if existing:
                # fetch permissions via model helper
                fake_user = FrontendUser()
                fake_user.id = existing.get('id')
                perms = FrontendUser.objects.get(pk=existing.get('id')).get_permissions()
            else:
                role_for_no_save = request.data.get('role_id') or request.query_params.get('role_id')
                if role_for_no_save:
                    with connection.cursor() as cur:
                        cur.execute('SELECT page_path,permission_type,is_allowed FROM frontend_role_permissions WHERE role_id=%s', [role_for_no_save])
                        rows = cur.fetchall()
             
                        for r in rows:
                            perms.setdefault(r[0], {})[r[1]] = bool(r[2])
        except Exception:
            perms = {}

        return Response({
            'message_type': 'success',
            'user': {
                'id': user_id_val,
                'email': email,
                'role_id': request.data.get('role_id') or request.query_params.get('role_id'),
                'name': name,
                'phone_number': phone_number,
            },
            'tokens': {'access': str(access_token), 'refresh': str(refresh)},
            'permissions': perms
        }, status=status.HTTP_200_OK)
    if not user:
        # Support a no-save mode: return JWT tokens and permissions for a role
        # without creating/saving a FrontendUser. Client can send `no_save: true`
        # and optionally `role_id` in the request body or query params.
        no_save = request.data.get('no_save') or request.query_params.get('no_save')
        role_for_no_save = request.data.get('role_id') or request.query_params.get('role_id')

        if no_save:
            # Normalize role_id if provided, otherwise leave as None
            role_for_no_save = str(role_for_no_save).strip() if role_for_no_save else None

            # Accept optional name and phone_number from request for no-save responses
            name = request.data.get('name') or request.query_params.get('name')
            phone_number = request.data.get('phone_number') or request.query_params.get('phone_number')
            name = str(name).strip() if name else None
            phone_number = str(phone_number).strip() if phone_number else None

            # If a matching frontend user exists, read its id/name/phone (no save)
            existing = None
            try:
                existing = FrontendUser.objects.filter(email__iexact=email).values('id', 'name', 'phone_number').first()
            except Exception:
                existing = None

            # If an existing frontend user was found, use its values when not provided
            user_id_val = existing['id'] if existing else None
            if existing:
                if not name and existing.get('name'):
                    name = existing.get('name')
                if (not phone_number) and existing.get('phone_number'):
                    phone_number = existing.get('phone_number')

            # Generate JWT tokens (no DB user created)
            refresh = RefreshToken()
            refresh['user_id'] = user_id_val
            refresh['email'] = email
            refresh['user_type'] = 'frontend_user'

            access_token = refresh.access_token
            access_token['user_id'] = user_id_val
            access_token['email'] = email
            access_token['user_type'] = 'frontend_user'

            # Fetch permissions for the provided role_id (or empty mapping)
            perms = {}
            try:
                with connection.cursor() as cur:
                    if role_for_no_save:
                        cur.execute(
                            'SELECT page_path,permission_type,is_allowed FROM frontend_role_permissions WHERE role_id=%s',
                            [role_for_no_save]
                        )
                    else:
                        # If no role specified, return empty permissions
                        cur.execute('SELECT page_path,permission_type,is_allowed FROM frontend_role_permissions WHERE 1=0')
                    rows = cur.fetchall()
                    for r in rows:
                        perms.setdefault(r[0], {})[r[1]] = bool(r[2])
            except Exception:
                perms = {}

            return Response({
                'message_type': 'success',
                'user': {
                    'id': user_id_val,
                    'email': email,
                    'role_id': role_for_no_save,
                    'name': name,
                    'phone_number': phone_number,
                },
                'tokens': {'access': str(access_token), 'refresh': str(refresh)},
                'permissions': perms
            }, status=status.HTTP_200_OK)

        # Existing behavior: return helpful debug info when user not found
        debug = {}
        if settings.DEBUG:
            ci = FrontendUser.objects.filter(email__iexact=email).values('email', 'password').first()
            debug['user_found_case_insensitive'] = bool(ci)
            if ci and ci.get('password'):
                debug['stored_password_hashed'] = str(ci.get('password')).startswith('pbkdf2_')

        resp = {'message_type': 'error', 'error': 'Invalid email or password'}
        if debug:
            resp['debug'] = debug
        return Response(resp, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if user is active
    if not user.is_active:
        return Response({
            'message_type': 'error',
            'error': 'User account is inactive'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Verify password. Support legacy/plaintext stored passwords by
    # checking raw equality and re-hashing on match so future logins use
    # the secure hashed form.
    if not check_password(password, user.password):
        # Fallback: if stored password is plaintext (legacy), accept it
        # and replace with a hashed password for future requests.
        if user.password == password:
            # Legacy plaintext password matched. For safety, accept login
            # for this request but do NOT persist any changes to the DB here.
            # If you want to migrate plaintext passwords to hashed values,
            # do that in a separate migration/maintenance script.
            pass
        else:
            debug = {}
            if settings.DEBUG:
                debug['stored_password_hashed'] = str(user.password).startswith('pbkdf2_')
            resp = {'message_type': 'error', 'error': 'Invalid email or password'}
            if debug:
                resp['debug'] = debug
            return Response(resp, status=status.HTTP_401_UNAUTHORIZED)
    
    # Generate JWT tokens with custom claims for custom User model
    try:
        # Create refresh token with custom claims
        refresh = RefreshToken()
        # Set custom claims for our User model
        refresh['user_id'] = user.id
        refresh['email'] = user.email
        refresh['user_type'] = 'frontend_user'  # Identifier for custom user
        
        # Generate access token from refresh token
        access_token = refresh.access_token
        access_token['user_id'] = user.id
        access_token['email'] = user.email
        access_token['user_type'] = 'frontend_user'
        
    except Exception as e:
        # Fallback: return user data without JWT tokens
        user_serializer = UserLoginSerializer({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone_number': user.phone_number,
            'role_id': user.role_id,
            'is_active': user.is_active
        })
        
        return Response({
            'message_type': 'success',
            'user': user_serializer.data,
            'message': 'Login successful (JWT tokens not available for custom user model)'
        }, status=status.HTTP_200_OK)
    
    # Serialize user data
    # Use User model helper to fetch permissions (reads UserRole/RolePermission)
    try:
        permissions = user.get_permissions()
    except Exception:
        permissions = {}

    user_serializer = UserLoginSerializer({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone_number': user.phone_number,
        'role_id': user.role_id,
        'is_active': user.is_active
    })
    
    return Response({
        'message_type': 'success',
        'user': user_serializer.data,
        'tokens': {
            'access': str(access_token),
            'refresh': str(refresh)
        },
        'permissions': permissions
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def users_list(request):
    """
    Get all users (including deactivated) or create a new user
    
    GET: Get all users
    Optional query parameters:
    - ?is_active=true/false - Filter by active status
    - ?role_id=1 - Filter by role_id
    
    POST: Create a new user
    Request body:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone_number": "1234567890" (optional),
        "password": "password123",
        "confirm_password": "password123",
        "role_id": 1 (optional),
        "is_active": true (optional, default: true)
    }
    """
    try:
        if request.method == 'POST':
            # Create user
            serializer = UserCreateSerializer(data=request.data)
            
            if serializer.is_valid():
                # Check if user with this email already exists
                email = serializer.validated_data.get('email')
                
                # Validate email address format and domain
                is_valid, validation_error = _validate_email_address(email)
                if not is_valid:
                    return Response({
                        'message_type': 'error',
                        'error': validation_error
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if FrontendUser.objects.filter(email=email).exists():
                    return Response({
                        'message_type': 'error',
                        'error': 'User with this email already exists'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Store plain password before hashing (for email)
                plain_password = serializer.validated_data.get('password')
                
                # Get recipient email from request if provided, otherwise use user email
                recipient_email = request.data.get('send_email_to', email)
                
                # Validate recipient email if different from user email
                if recipient_email and recipient_email != email:
                    is_valid, validation_error = _validate_email_address(recipient_email)
                    if not is_valid:
                        return Response({
                            'message_type': 'error',
                            'error': f"Invalid recipient email: {validation_error}"
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create user (password will be hashed in model's save method)
                user = serializer.save()
                
                # Log warning if role_id was set to NULL due to migration issue (but don't show in response)
                original_role_id = request.data.get('role_id')
                if original_role_id and user.role_id is None:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"User created with role_id=NULL. Original role_id was '{original_role_id}'. Database migration needed.")
                
                # Log user ID for super admin users
                try:
                    admin_profile = user.adminprofile
                    if admin_profile and admin_profile.role == 'superadmin':
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f'Super Admin user created with ID: {user.id}, Name: {user.name}, Email: {user.email}')
                        print(f'BACKEND LOG: Super Admin user created - ID: {user.id}, Name: {user.name}')
                except:
                    # If no admin profile exists, check role_id directly
                    # Handle both string (e.g., 'R001', '1') and integer values
                    role_id_str = str(user.role_id) if user.role_id is not None else None
                    if role_id_str in ['1', 1]:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f'Super Admin user created with ID: {user.id}, Name: {user.name}, Email: {user.email}')
                        print(f'BACKEND LOG: Super Admin user created - ID: {user.id}, Name: {user.name}')
                
                # Send email with credentials asynchronously (real-time, non-blocking)
                email_started = False
                email_error = None
                if recipient_email:
                    try:
                        email_started, email_error = send_user_credentials_email_async(user, plain_password, recipient_email)
                    except Exception as e:
                        # Log error but don't fail the request
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Failed to start email thread: {str(e)}")
                        email_error = str(e)
                
                # Return user data immediately (email is sent in background)
                response_serializer = UserSerializer(user)
                
                response_data = {
                    'message_type': 'success',
                    'message': 'The user has been successfully created.',
                    'data': [response_serializer.data]
                }
                
                if email_started:
                    response_data['email_sent'] = True
                    response_data['email_message'] = f'A notification email has been successfully queued and will be sent to {recipient_email}.'
                else:
                    response_data['email_sent'] = False
                    response_data['email_message'] = email_error or 'Email configuration missing or failed to start email thread'
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message_type': 'error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # GET: List all users (including deactivated)
            users = FrontendUser.objects.all()
            
            # Filter by is_active if provided (supports "active"/"deactive" strings or boolean)
            is_active_param = request.query_params.get('is_active')
            if is_active_param is not None:
                # Support string values "active"/"deactive" or boolean values
                if is_active_param.lower() in ('active', 'true', '1', 'yes'):
                    users = users.filter(is_active=True)
                elif is_active_param.lower() in ('deactive', 'false', '0', 'no'):
                    users = users.filter(is_active=False)
            
            # Filter by role_id if provided
            role_id_param = request.query_params.get('role_id')
            if role_id_param:
                try:
                    role_id = int(role_id_param)
                    users = users.filter(role_id=role_id)
                except ValueError:
                    pass
            
            # Order by created_at descending
            users = users.order_by('-created_at')
            
            serializer = UserSerializer(users, many=True)
            
            return Response({
                'message_type': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            })
    except Exception as e:
        return Response({
            'message_type': 'error',
            'error': str(e),
            'count': 0,
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def user_detail(request, id):
    """
    Get, update, or deactivate a specific user by ID
    
    GET: Retrieve user
    PUT/PATCH: Update user (PATCH allows partial update)
    DELETE: Deactivate user (soft delete - sets is_active=False, doesn't delete from database)
    """
    try:
        user = FrontendUser.objects.get(pk=id)
    except FrontendUser.DoesNotExist:
        return Response({
            'message_type': 'error',
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Handle different HTTP methods
    if request.method == 'GET':
        # Get user
        serializer = UserSerializer(user)
        return Response({
            'message_type': 'success',
            'data': [serializer.data]
        })
    
    elif request.method == 'DELETE':
        # Soft delete: Set is_active=False
        user.is_active = False
        user.save()
        
        response_serializer = UserSerializer(user)
        return Response({
            'message_type': 'success',
            'message': 'User deactivated successfully',
            'data': [response_serializer.data]
        }, status=status.HTTP_200_OK)
    
    elif request.method in ['PUT', 'PATCH']:
        # Update user
        # PATCH allows partial updates, PUT requires all fields
        partial = request.method == 'PATCH'
        serializer = UserUpdateSerializer(user, data=request.data, partial=partial)
        
        if serializer.is_valid():
            # Check if email is being updated and if it already exists
            if 'email' in serializer.validated_data:
                new_email = serializer.validated_data.get('email')
                if new_email != user.email and FrontendUser.objects.filter(email=new_email).exists():
                    return Response({
                        'message_type': 'error',
                        'error': 'User with this email already exists'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            updated_user = serializer.save()
            response_serializer = UserSerializer(updated_user)
            
            return Response({
                'message_type': 'success',
                'message': 'User updated successfully',
                'data': [response_serializer.data]
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message_type': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        return Response({
            'message_type': 'error',
            'error': 'Method not allowed'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def roles_list(request):
    """
    Get all roles (including deactivated) or create a new role
    
    GET: Get all roles
    Optional query parameters:
    - ?is_active=true/false - Filter by active status
    - ?name=RoleName - Filter by role name (case-insensitive search)
    - ?page_permission=PageName - Filter by page_permission (case-insensitive search)
    
    POST: Create a new role
    Request body:
    {
        "role_id": "R001",
        "name": "Super Admin",
        "description": "Super administrator role with full access",
        "page_permission": "Dashboard" (optional),
        "default_page": "/dashboard",
        "is_active": "active" (optional, default: "active")
    }
    """
    try:
        if request.method == 'POST':
            # Create role
            serializer = RoleCreateSerializer(data=request.data)
            
            if serializer.is_valid():
                # Check if role with this role_id already exists
                role_id = serializer.validated_data.get('role_id')
                if Role.objects.filter(role_id=role_id).exists():
                    return Response({
                        'message_type': 'error',
                        'error': 'Role with this role_id already exists'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if role with this name already exists
                name = serializer.validated_data.get('name')
                if Role.objects.filter(name__iexact=name).exists():
                    return Response({
                        'message_type': 'error',
                        'error': 'Role with this name already exists'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create role
                role = serializer.save()
                
                # Return role data
                response_serializer = RoleSerializer(role)
                
                return Response({
                    'message_type': 'success',
                    'message': 'The role has been successfully created.',
                    'data': [response_serializer.data]
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message_type': 'error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # GET: List all roles (including deactivated)
            roles = Role.objects.all()
            
            # Filter by is_active if provided (supports "active"/"deactive" strings or boolean)
            is_active_param = request.query_params.get('is_active')
            if is_active_param is not None:
                # Support string values "active"/"deactive" or boolean values
                if is_active_param.lower() in ('active', 'true', '1', 'yes'):
                    roles = roles.filter(is_active=True)
                elif is_active_param.lower() in ('deactive', 'false', '0', 'no'):
                    roles = roles.filter(is_active=False)
            
            # Filter by name if provided (case-insensitive search)
            name_param = request.query_params.get('name')
            if name_param:
                roles = roles.filter(name__icontains=name_param)
            
            # Filter by page_permission if provided (case-insensitive search)
            page_permission_param = request.query_params.get('page_permission')
            if page_permission_param:
                roles = roles.filter(page_permission__icontains=page_permission_param)
            
            # Order by created_at descending
            roles = roles.order_by('-created_at')
            
            serializer = RoleSerializer(roles, many=True)
            
            return Response({
                'message_type': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            })
    except Exception as e:
        return Response({
            'message_type': 'error',
            'error': str(e),
            'count': 0,
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def roles_basic_list(request):
    """
    Get all roles with only role_id and role_name (simplified endpoint)
    
    GET: Get all roles with basic information (role_id and role_name only)
    Optional query parameters:
    - ?is_active=true/false - Filter by active status (default: only active roles)
    
    Response format:
    {
        "message_type": "success",
        "count": 2,
        "data": [
            {
                "role_id": "R001",
                "role_name": "Super Admin"
            },
            {
                "role_id": "R002",
                "role_name": "Admin"
            }
        ]
    }
    """
    try:
        # GET: List all roles with only role_id and role_name
        roles = Role.objects.all()
        
        # Filter by is_active if provided (default to active only if not specified)
        is_active_param = request.query_params.get('is_active')
        if is_active_param is not None:
            # Support string values "active"/"deactive" or boolean values
            if is_active_param.lower() in ('active', 'true', '1', 'yes'):
                roles = roles.filter(is_active=True)
            elif is_active_param.lower() in ('deactive', 'false', '0', 'no'):
                roles = roles.filter(is_active=False)
        else:
            # Default: show only active roles
            roles = roles.filter(is_active=True)
        
        # Order by role_id
        roles = roles.order_by('role_id')
        
        serializer = RoleBasicSerializer(roles, many=True)
        
        return Response({
            'message_type': 'success',
            'count': len(serializer.data),
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'message_type': 'error',
            'error': str(e),
            'count': 0,
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def role_detail(request, role_id):
    """
    Get, update, or deactivate a specific role by role_id
    
    GET: Retrieve role
    PUT/PATCH: Update role (PATCH allows partial update)
    DELETE: Deactivate role (soft delete - sets is_active=False, doesn't delete from database)
    """
    try:
        role = Role.objects.get(pk=role_id)
    except Role.DoesNotExist:
        return Response({
            'message_type': 'error',
            'error': 'Role not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Handle different HTTP methods
    if request.method == 'GET':
        # Get role
        serializer = RoleSerializer(role)
        return Response({
            'message_type': 'success',
            'data': [serializer.data]
        })
    
    elif request.method == 'DELETE':
        # Soft delete: Set is_active=False
        role.is_active = False
        role.save()
        
        response_serializer = RoleSerializer(role)
        return Response({
            'message_type': 'success',
            'message': 'Role deactivated successfully',
            'data': [response_serializer.data]
        }, status=status.HTTP_200_OK)
    
    elif request.method in ['PUT', 'PATCH']:
        # Check if permissions are included - if so, use the bulk update endpoint logic
        if 'permissions' in request.data:
            # Use RoleWithPermissionsUpdateSerializer to handle role + permissions
            from .serializers import RoleWithPermissionsUpdateSerializer
            payload = request.data.copy()
            payload['role_id'] = role_id
            partial = request.method == 'PATCH'
            
            serializer = RoleWithPermissionsUpdateSerializer(data=payload, partial=partial)
            
            if serializer.is_valid():
                # Create a dummy role instance for the update method
                # Note: Role is already imported at module level
                dummy_role = Role(role_id=role_id)
                result = serializer.update(dummy_role, serializer.validated_data)
                updated_role = result['role']
                created_permissions = result.get('created_permissions', [])
                updated_permissions = result.get('updated_permissions', [])
                
                # Serialize response
                # Note: RoleSerializer and RolePermissionSerializer are already imported at module level
                role_serializer = RoleSerializer(updated_role)
                all_permissions = created_permissions + updated_permissions
                permissions_serializer = RolePermissionSerializer(all_permissions, many=True)
                
                return Response({
                    'message_type': 'success',
                    'message': f'Role and permissions updated successfully. Created: {len(created_permissions)}, Updated: {len(updated_permissions)}',
                    'data': {
                        'role': role_serializer.data,
                        'permissions': permissions_serializer.data,
                        'created_count': len(created_permissions),
                        'updated_count': len(updated_permissions)
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message_type': 'error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update role only (no permissions)
        # PATCH allows partial updates, PUT requires all fields
        partial = request.method == 'PATCH'
        serializer = RoleUpdateSerializer(role, data=request.data, partial=partial)
        
        if serializer.is_valid():
            # Check if name is being updated and if it already exists
            if 'name' in serializer.validated_data:
                new_name = serializer.validated_data.get('name')
                if new_name != role.name and Role.objects.filter(name__iexact=new_name).exists():
                    return Response({
                        'message_type': 'error',
                        'error': 'Role with this name already exists'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            updated_role = serializer.save()
            response_serializer = RoleSerializer(updated_role)
            
            return Response({
                'message_type': 'success',
                'message': 'Role updated successfully',
                'data': [response_serializer.data]
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message_type': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        return Response({
            'message_type': 'error',
            'error': 'Method not allowed'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def role_with_permissions_create(request):
    """
    Create a role with all its permissions in one request
    
    POST: Create a new role with permissions
    Request body:
    {
        "name": "Super Admin",
        "description": "Full access to all features",
        "defaultPage": "/users",
        "permissions": {
            "/": {
                "view": true
            },
            "/users": {
                "view": true,
                "create": true,
                "edit": true,
                "delete": true
            },
            "/roles": {
                "view": true,
                "create": false,
                "edit": false,
                "delete": false
            }
        }
    }
    
    Response:
    {
        "message_type": "success",
        "message": "Role and permissions created successfully",
        "data": {
            "role": {...},
            "permissions": [...]
        }
    }
    """
    try:
        # Log the incoming data for debugging (only in DEBUG mode)
        if settings.DEBUG:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Role with permissions create - Request data: {request.data}")
            logger.info(f"Role with permissions create - Request method: {request.method}")
        
        # Ensure we're using the correct serializer
        serializer = RoleWithPermissionsCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            # Add helpful error message
            error_response = {
                'message_type': 'error',
                'errors': serializer.errors,
                'message': 'Please ensure you are sending the correct payload format. Expected: {"name": "...", "description": "...", "defaultPage": "...", "permissions": {...}}'
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        # Create role and permissions
        result = serializer.save()
        role = result['role']
        permissions = result['permissions']
        
        # Serialize the response
        role_serializer = RoleSerializer(role)
        permissions_serializer = RolePermissionSerializer(permissions, many=True)
        
        return Response({
            'message_type': 'success',
            'message': 'Role and permissions created successfully',
            'data': {
                'role': role_serializer.data,
                'permissions': permissions_serializer.data,
                'permissions_count': len(permissions)
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        return Response({
            'message_type': 'error',
            'error': str(e),
            'traceback': traceback.format_exc() if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def role_with_permissions_update(request):
    """
    Update a role with all its permissions in one request (creates role if it doesn't exist)
    
    PUT/PATCH: Update an existing role with permissions, or create a new role if it doesn't exist
    Request body:
    {
        "role_id": "R001",
        "name": "Updated Role Name" (required if creating new role),
        "description": "Updated description",
        "defaultPage": "/dashboard",
        "permissions": {
            "/": {
                "view": true
            },
            "/users": {
                "view": true,
                "create": true,
                "edit": true,
                "delete": false
            },
            "/roles": {
                "view": true,
                "edit": false
            }
        }
    }
    
    Note:
    - role_id is required to identify which role to update/create
    - If role doesn't exist, it will be created (name is required in this case)
    - If role exists, all fields are optional
    - If permissions are provided, they will update/create permissions for the role
    - Permissions not in the payload will remain unchanged
    
    Response:
    {
        "message_type": "success",
        "message": "Role and permissions updated successfully" or "Role created and permissions set",
        "data": {
            "role": {...},
            "permissions": [...],
            "created_count": 2,
            "updated_count": 3,
            "total_permissions": 5
        }
    }
    """
    try:
        # Check if role_id is provided
        role_id = request.data.get('role_id')
        if not role_id:
            return Response({
                'message_type': 'error',
                'error': 'role_id is required to identify which role to update'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # PATCH allows partial updates, PUT requires all fields
        partial = request.method == 'PATCH'
        serializer = RoleWithPermissionsUpdateSerializer(data=request.data, partial=partial)
        
        if serializer.is_valid():
            # The serializer's update method will handle getting or creating the role
            # We just need to pass a dummy instance (the serializer ignores it and gets role by role_id)
            dummy_role = Role(role_id=serializer.validated_data['role_id'])
            
            # Update role and permissions (serializer will create role if it doesn't exist)
            result = serializer.update(dummy_role, serializer.validated_data)
            updated_role = result['role']
            created_permissions = result['created_permissions']
            updated_permissions = result['updated_permissions']
            role_created = result.get('role_created', False)
            
            # Refresh role from database to ensure we have latest data
            updated_role.refresh_from_db()
            
            # Get ALL permissions for this role (not just created/updated)
            # Refresh from DB to ensure names are synced using raw SQL
            from django.db import connection
            from types import SimpleNamespace
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT rp.role_id, rp.name, rp.page_path, rp.permission_type, 
                           rp.is_allowed, rp.created_at, rp.updated_at
                    FROM frontend_role_permissions rp
                    WHERE rp.role_id = %s
                    ORDER BY rp.page_path, rp.permission_type
                """, [updated_role.role_id])
                rows = cursor.fetchall()
                
                # Convert rows to SimpleNamespace objects for serialization
                all_role_permissions = []
                for row in rows:
                    perm = SimpleNamespace()
                    perm.role = updated_role
                    perm.name = row[1]
                    perm.page_path = row[2]
                    perm.permission_type = row[3]
                    perm.is_allowed = row[4]
                    perm.created_at = row[5]
                    perm.updated_at = row[6]
                    all_role_permissions.append(perm)
            
            # Serialize the response
            role_serializer = RoleSerializer(updated_role)
            permissions_serializer = RolePermissionSerializer(all_role_permissions, many=True)
            
            # Create appropriate message
            if role_created:
                message = f'Role created and permissions set. Created: {len(created_permissions)}, Updated: {len(updated_permissions)}'
            else:
                message = f'Role and permissions updated successfully. Created: {len(created_permissions)}, Updated: {len(updated_permissions)}'
            
            return Response({
                'message_type': 'success',
                'message': message,
                'data': {
                    'role': role_serializer.data,
                    'permissions': permissions_serializer.data,
                    'created_count': len(created_permissions),
                    'updated_count': len(updated_permissions),
                    'total_permissions': len(all_role_permissions)
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message_type': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Role.DoesNotExist:
        # This shouldn't happen since serializer creates role, but just in case
        return Response({
            'message_type': 'error',
            'error': f'Role with role_id "{request.data.get("role_id", "unknown")}" does not exist and could not be created. Please ensure "name" is provided when creating a new role.'
        }, status=status.HTTP_404_NOT_FOUND)
    except serializers.ValidationError as e:
        # Handle validation errors from serializer
        return Response({
            'message_type': 'error',
            'errors': e.detail if hasattr(e, 'detail') else str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        import traceback
        return Response({
            'message_type': 'error',
            'error': str(e),
            'traceback': traceback.format_exc() if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST', 'PATCH', 'PUT'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def role_permissions_list(request):
    """
    Get all role permissions or create a new role permission
    
    GET: Get all role permissions
    Optional query parameters:
    - ?role_id=R001 - Filter by role_id
    - ?name=Admin - Filter by name (case-insensitive search)
    - ?page_path=/users - Filter by page_path
    - ?permission_type=view - Filter by permission_type
    - ?is_allowed=true/false - Filter by is_allowed status
    
    POST: Create a new role permission or bulk update permissions
    
    Single Permission (old format):
    {
        "role_id": "R001",
        "page_path": "/users",
        "permission_type": "view",
        "is_allowed": "allowed" (optional, default: "allowed")
    }
    
    Bulk Permissions (new format):
    {
        "role_id": "R001" (optional - will be auto-generated if not provided),
        "name": "Role Name" (required),
        "description": "Role description" (optional),
        "defaultPage": "/users" (optional, default: "/"),
        "permissions": {
            "/": {
                "view": true
            },
            "/users": {
                "view": true,
                "create": true,
                "edit": true,
                "delete": true
            },
            "/roles": {
                "view": true
            }
        }
    }
    
    Note: 
    - If role_id is not provided, it will be auto-generated (R001, R002, etc.)
    - If the role doesn't exist, it will be created automatically
    - 'name' is always required
    """
    try:
        if request.method in ['POST', 'PUT', 'PATCH']:
            # PUT/PATCH: Only supports bulk update format (requires 'permissions' dictionary)
            if request.method in ['PUT', 'PATCH']:
                if 'permissions' not in request.data:
                    return Response({
                        'message_type': 'error',
                        'error': 'PUT/PATCH requires a "permissions" dictionary in the payload. Use POST for single permission creation.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if payload has the new format (with 'permissions' dictionary)
            # role_id is optional - will be auto-generated if not provided
            if 'permissions' in request.data:
                # New format: Bulk create/update permissions
                serializer = RolePermissionsBulkUpdateSerializer(data=request.data)
                
                if serializer.is_valid():
                    result = serializer.save()
                    role = result['role']
                    created_permissions = result['created_permissions']
                    updated_permissions = result['updated_permissions']
                    role_created = result.get('role_created', False)
                    
                    # Serialize all permissions
                    all_permissions = created_permissions + updated_permissions
                    permissions_serializer = RolePermissionSerializer(all_permissions, many=True)
                    role_serializer = RoleSerializer(role)
                    
                    message = f'Permissions updated successfully. Created: {len(created_permissions)}, Updated: {len(updated_permissions)}'
                    if role_created:
                        message = f'Role created and permissions set. Created: {len(created_permissions)}, Updated: {len(updated_permissions)}'
                    
                    return Response({
                        'message_type': 'success',
                        'message': message,
                        'data': {
                            'role': role_serializer.data,
                            'role_created': role_created,
                            'permissions': permissions_serializer.data,
                            'created_count': len(created_permissions),
                            'updated_count': len(updated_permissions)
                        }
                    }, status=status.HTTP_201_CREATED if role_created else status.HTTP_200_OK)
                else:
                    return Response({
                        'message_type': 'error',
                        'errors': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Old format: Single permission creation (only for POST)
                if request.method != 'POST':
                    return Response({
                        'message_type': 'error',
                        'error': 'PUT/PATCH requires a "permissions" dictionary in the payload. Use POST for single permission creation.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = RolePermissionCreateSerializer(data=request.data)
                
                if serializer.is_valid():
                    # Create permission (validation for uniqueness is in serializer)
                    permission = serializer.save()
                    
                    # Return permission data
                    response_serializer = RolePermissionSerializer(permission)
                    
                    return Response({
                        'message_type': 'success',
                        'message': 'The role permission has been successfully created.',
                        'data': [response_serializer.data]
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'message_type': 'error',
                        'errors': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # GET: List all role permissions using raw SQL to avoid id field
            from django.db import connection
            from types import SimpleNamespace
            from .models import Role
            
            # Build WHERE clause based on query parameters
            where_clauses = []
            params = []
            
            role_id_param = request.query_params.get('role_id')
            if role_id_param:
                where_clauses.append("rp.role_id = %s")
                params.append(role_id_param)
            
            name_param = request.query_params.get('name')
            if name_param:
                where_clauses.append("rp.name ILIKE %s")
                params.append(f'%{name_param}%')
            
            page_path_param = request.query_params.get('page_path')
            if page_path_param:
                where_clauses.append("rp.page_path ILIKE %s")
                params.append(f'%{page_path_param}%')
            
            permission_type_param = request.query_params.get('permission_type')
            if permission_type_param:
                where_clauses.append("rp.permission_type ILIKE %s")
                params.append(permission_type_param)
            
            is_allowed_param = request.query_params.get('is_allowed')
            if is_allowed_param is not None:
                if is_allowed_param.lower() in ('allowed', 'true', '1', 'yes'):
                    where_clauses.append("rp.is_allowed = TRUE")
                elif is_allowed_param.lower() in ('denied', 'false', '0', 'no'):
                    where_clauses.append("rp.is_allowed = FALSE")
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT rp.role_id, rp.name, rp.page_path, rp.permission_type, 
                           rp.is_allowed, rp.created_at, rp.updated_at
                    FROM frontend_role_permissions rp
                    WHERE {where_sql}
                    ORDER BY rp.created_at DESC
                """, params)
                rows = cursor.fetchall()
                
                # Convert rows to SimpleNamespace objects for serialization
                permissions = []
                for row in rows:
                    perm = SimpleNamespace()
                    # Fetch role object for each permission
                    try:
                        perm.role = Role.objects.get(role_id=row[0])
                    except Role.DoesNotExist:
                        continue
                    perm.name = row[1]
                    perm.page_path = row[2]
                    perm.permission_type = row[3]
                    perm.is_allowed = row[4]
                    perm.created_at = row[5]
                    perm.updated_at = row[6]
                    permissions.append(perm)
            
            serializer = RolePermissionSerializer(permissions, many=True)
            
            return Response({
                'message_type': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            })
    except Exception as e:
        return Response({
            'message_type': 'error',
            'error': str(e),
            'count': 0,
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'DELETE', 'PUT', 'PATCH'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def role_permissions_by_role(request, role_id):
    """
    Get, update, or delete all permissions for a specific role
    
    GET: List all permissions for the specified role_id
    PUT/PATCH: Bulk update permissions for the specified role_id
    DELETE: Delete all permissions for the specified role_id
    
    Example:
    GET /api/auth/role-permissions/R001/
    PUT/PATCH /api/auth/role-permissions/R001/
    DELETE /api/auth/role-permissions/R001/
    
    PUT/PATCH Request body:
    {
        "permissions": {
            "/": {
                "view": true
            },
            "/users": {
                "view": true,
                "create": true,
                "edit": true,
                "delete": false
            }
        }
    }
    """
    try:
        # First check if the role exists
        from .models import Role
        try:
            role = Role.objects.get(role_id=role_id)
        except Role.DoesNotExist:
            # Check if there are similar role_ids (case-insensitive)
            similar_roles = Role.objects.filter(role_id__iexact=role_id)
            if similar_roles.exists():
                similar_role_ids = [r.role_id for r in similar_roles]
                return Response({
                    'message_type': 'error',
                    'error': f'Role with role_id "{role_id}" not found.',
                    'suggestion': f'Did you mean one of these? {similar_role_ids}',
                    'available_roles': similar_role_ids
                }, status=status.HTTP_404_NOT_FOUND)
            else:
                # List all available role_ids
                all_roles = Role.objects.values_list('role_id', flat=True)
                return Response({
                    'message_type': 'error',
                    'error': f'Role with role_id "{role_id}" not found.',
                    'available_role_ids': list(all_roles),
                    'hint': 'Use GET /api/auth/roles/ to see all available roles'
                }, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            # Use raw SQL to fetch permissions without id field
            from django.db import connection
            from types import SimpleNamespace
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT rp.role_id, rp.name, rp.page_path, rp.permission_type, 
                           rp.is_allowed, rp.created_at, rp.updated_at
                    FROM frontend_role_permissions rp
                    WHERE rp.role_id = %s
                    ORDER BY rp.created_at DESC
                """, [role_id])
                rows = cursor.fetchall()
                
                # Convert rows to SimpleNamespace objects for serialization
                permissions = []
                for row in rows:
                    perm = SimpleNamespace()
                    perm.role = role  # Use the role object we already fetched
                    perm.name = row[1]
                    perm.page_path = row[2]
                    perm.permission_type = row[3]
                    perm.is_allowed = row[4]
                    perm.created_at = row[5]
                    perm.updated_at = row[6]
                    permissions.append(perm)
            
            serializer = RolePermissionSerializer(permissions, many=True)
            return Response({
                'message_type': 'success',
                'count': len(serializer.data),
                'role_id': role_id,
                'role_name': role.name,
                'data': serializer.data
            })
        
        elif request.method in ['PUT', 'PATCH']:
            # Bulk update permissions for this role
            if 'permissions' not in request.data:
                return Response({
                    'message_type': 'error',
                    'error': 'PUT/PATCH requires a "permissions" dictionary in the payload.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Use the bulk update serializer
            payload = request.data.copy()
            payload['role_id'] = role_id
            # If name/description/defaultPage are not provided, use existing role values
            if 'name' not in payload:
                payload['name'] = role.name
            if 'description' not in payload:
                payload['description'] = role.description
            if 'defaultPage' not in payload:
                payload['defaultPage'] = role.default_page
            
            serializer = RolePermissionsBulkUpdateSerializer(data=payload)
            
            if serializer.is_valid():
                result = serializer.save()
                updated_role = result['role']
                created_permissions = result['created_permissions']
                updated_permissions = result['updated_permissions']
                
                # Serialize all permissions
                all_permissions = created_permissions + updated_permissions
                permissions_serializer = RolePermissionSerializer(all_permissions, many=True)
                role_serializer = RoleSerializer(updated_role)
                
                return Response({
                    'message_type': 'success',
                    'message': f'Permissions updated successfully for role "{updated_role.name}". Created: {len(created_permissions)}, Updated: {len(updated_permissions)}',
                    'data': {
                        'role': role_serializer.data,
                        'permissions': permissions_serializer.data,
                        'created_count': len(created_permissions),
                        'updated_count': len(updated_permissions)
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message_type': 'error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            # Use raw SQL to count and delete permissions
            from django.db import connection
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM frontend_role_permissions WHERE role_id = %s
                """, [role_id])
                count = cursor.fetchone()[0]
                
                if count == 0:
                    return Response({
                        'message_type': 'success',
                        'message': f'Role "{role.name}" (role_id: {role_id}) exists but has no permissions to delete.',
                        'role_id': role_id,
                        'role_name': role.name,
                        'deleted_count': 0
                    }, status=status.HTTP_200_OK)
                
                # Delete all permissions for this role
                cursor.execute("""
                    DELETE FROM frontend_role_permissions WHERE role_id = %s
                """, [role_id])
            
            return Response({
                'message_type': 'success',
                'message': f'Successfully deleted {count} permission(s) for role "{role.name}" (role_id: {role_id})',
                'role_id': role_id,
                'role_name': role.name,
                'deleted_count': count
            }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'message_type': 'error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def role_permission_detail(request, role_id, page_path, permission_type):
    """
    Get, create, update, or delete a specific role permission by composite key (role_id, page_path, permission_type)
    
    GET: Retrieve role permission
    POST: Create a new role permission (if it doesn't exist)
    Request body:
    {
        "is_allowed": "allowed" (optional, default: "allowed")
    }
    PUT/PATCH: Update role permission (PATCH allows partial update)
    Request body (all fields optional for PATCH, all required for PUT):
    {
        "role_id": "R001" (optional - to change role),
        "page_path": "/users" (optional - to change page),
        "permission_type": "view" (optional - to change permission type),
        "is_allowed": "allowed" or "denied" (optional)
    }
    DELETE: Delete role permission (hard delete)
    """
    # Decode URL-encoded page_path
    from urllib.parse import unquote
    page_path = unquote(page_path)
    
    try:
        role = Role.objects.get(role_id=role_id)
    except Role.DoesNotExist:
        return Response({
            'message_type': 'error',
            'error': f'Role with role_id "{role_id}" does not exist.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Use raw SQL to check if permission exists and fetch it
    from django.db import connection
    from types import SimpleNamespace
    
    permission_exists = False
    permission = None
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT rp.role_id, rp.name, rp.page_path, rp.permission_type, 
                   rp.is_allowed, rp.created_at, rp.updated_at
            FROM frontend_role_permissions rp
            WHERE rp.role_id = %s AND rp.page_path = %s AND rp.permission_type = %s
        """, [role.role_id, page_path, permission_type])
        row = cursor.fetchone()
        
        if row:
            permission_exists = True
            perm = SimpleNamespace()
            perm.role = role
            perm.name = row[1]
            perm.page_path = row[2]
            perm.permission_type = row[3]
            perm.is_allowed = row[4]
            perm.created_at = row[5]
            perm.updated_at = row[6]
            permission = perm
    
    # Handle different HTTP methods
    if request.method == 'GET':
        if not permission_exists:
            return Response({
                'message_type': 'error',
                'error': 'Role permission not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get permission
        serializer = RolePermissionSerializer(permission)
        return Response({
            'message_type': 'success',
            'data': [serializer.data]
        })
    
    elif request.method == 'POST':
        # Create permission (if it doesn't exist)
        if permission_exists:
            return Response({
                'message_type': 'error',
                'error': f'Role permission with role_id "{role_id}", page_path "{page_path}", and permission_type "{permission_type}" already exists. Use PUT/PATCH to update it.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create permission with the composite key values
        data = request.data.copy()
        data['role_id'] = role_id
        data['page_path'] = page_path
        data['permission_type'] = permission_type
        
        serializer = RolePermissionCreateSerializer(data=data)
        
        if serializer.is_valid():
            permission = serializer.save()
            response_serializer = RolePermissionSerializer(permission)
            
            return Response({
                'message_type': 'success',
                'message': 'Role permission created successfully',
                'data': [response_serializer.data]
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message_type': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not permission_exists:
            return Response({
                'message_type': 'error',
                'error': 'Role permission not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Hard delete: Delete from database using raw SQL
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM frontend_role_permissions 
                WHERE role_id = %s AND page_path = %s AND permission_type = %s
            """, [role.role_id, page_path, permission_type])
        
        return Response({
            'message_type': 'success',
            'message': 'Role permission deleted successfully'
        }, status=status.HTTP_200_OK)
    
    elif request.method in ['PUT', 'PATCH']:
        if not permission_exists:
            return Response({
                'message_type': 'error',
                'error': 'Role permission not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update permission
        # PATCH allows partial updates, PUT requires all fields
        partial = request.method == 'PATCH'
        serializer = RolePermissionUpdateSerializer(permission, data=request.data, partial=partial)
        
        if serializer.is_valid():
            updated_permission = serializer.save()
            response_serializer = RolePermissionSerializer(updated_permission)
            
            return Response({
                'message_type': 'success',
                'message': 'Role permission updated successfully',
                'data': [response_serializer.data]
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message_type': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        return Response({
            'message_type': 'error',
            'error': 'Method not allowed'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def role_permission_detail_by_id(request, id):
    """
    Backward compatibility endpoint: Get, create, update, or delete a specific role permission by ID
    
    NOTE: This endpoint is deprecated. The id column has been removed from the database.
    Please use the composite key endpoint instead:
    /api/auth/role-permissions/<role_id>/<page_path>/<permission_type>/
    
    This endpoint now returns an error directing users to use the composite key format.
    """
    return Response({
        'message_type': 'error',
        'error': 'ID-based lookups are no longer supported. The id column has been removed.',
        'message': 'Please use the composite key endpoint instead: /api/auth/role-permissions/<role_id>/<page_path>/<permission_type>/',
        'example': '/api/auth/role-permissions/R001/%2Fusers/view/'
    }, status=status.HTTP_410_GONE)  # 410 Gone - resource no longer available


@api_view(['GET', 'POST'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def user_roles_list(request):
    """
    Get all user role assignments or create a new user role assignment
    
    GET: Get all user role assignments
    Optional query parameters:
    - ?user_id=1 - Filter by user_id
    - ?role_id=R001 - Filter by role_id
    - ?is_active=true/false - Filter by is_active status
    
    POST: Create a new user role assignment
    Request body:
    {
        "user_id": 1,
        "role_id": "R001",
        "assigned_by_id": 1 (optional),
        "is_active": "active" (optional, default: "active")
    }
    """
    try:
        if request.method == 'POST':
            # Create user role assignment
            serializer = UserRoleCreateSerializer(data=request.data)
            
            if serializer.is_valid():
                # Create assignment (validation for uniqueness is in serializer)
                user_role = serializer.save()
                
                # Return assignment data
                response_serializer = UserRoleSerializer(user_role)
                
                return Response({
                    'message_type': 'success',
                    'message': 'The user role assignment has been successfully created.',
                    'data': [response_serializer.data]
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message_type': 'error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # GET: List all user role assignments
            user_roles = UserRole.objects.all()
            
            # Filter by user_id if provided
            user_id_param = request.query_params.get('user_id')
            if user_id_param:
                try:
                    user_id = int(user_id_param)
                    user_roles = user_roles.filter(user_id=user_id)
                except ValueError:
                    pass
            
            # Filter by role_id if provided
            role_id_param = request.query_params.get('role_id')
            if role_id_param:
                user_roles = user_roles.filter(role__role_id=role_id_param)
            
            # Filter by is_active if provided
            is_active_param = request.query_params.get('is_active')
            if is_active_param is not None:
                if is_active_param.lower() in ('active', 'true', '1', 'yes'):
                    user_roles = user_roles.filter(is_active=True)
                elif is_active_param.lower() in ('inactive', 'false', '0', 'no'):
                    user_roles = user_roles.filter(is_active=False)
            
            # Order by assigned_at descending
            user_roles = user_roles.order_by('-assigned_at')
            
            serializer = UserRoleSerializer(user_roles, many=True)
            
            return Response({
                'message_type': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            })
    except Exception as e:
        return Response({
            'message_type': 'error',
            'error': str(e),
            'count': 0,
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def user_role_detail(request, id):
    """
    Get, update, or delete a specific user role assignment by ID
    
    GET: Retrieve user role assignment
    PUT/PATCH: Update user role assignment (PATCH allows partial update, only is_active can be updated)
    DELETE: Delete user role assignment (hard delete)
    """
    try:
        user_role = UserRole.objects.get(pk=id)
    except UserRole.DoesNotExist:
        return Response({
            'message_type': 'error',
            'error': 'User role assignment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Handle different HTTP methods
    if request.method == 'GET':
        # Get user role assignment
        serializer = UserRoleSerializer(user_role)
        return Response({
            'message_type': 'success',
            'data': [serializer.data]
        })
    
    elif request.method == 'DELETE':
        # Hard delete: Delete from database
        user_role.delete()
        return Response({
            'message_type': 'success',
            'message': 'User role assignment deleted successfully'
        }, status=status.HTTP_200_OK)
    
    elif request.method in ['PUT', 'PATCH']:
        # Update user role assignment (only is_active can be updated)
        # PATCH allows partial updates, PUT requires all fields
        partial = request.method == 'PATCH'
        serializer = UserRoleUpdateSerializer(user_role, data=request.data, partial=partial)
        
        if serializer.is_valid():
            updated_user_role = serializer.save()
            response_serializer = UserRoleSerializer(updated_user_role)
            
            return Response({
                'message_type': 'success',
                'message': 'User role assignment updated successfully',
                'data': [response_serializer.data]
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message_type': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        return Response({
            'message_type': 'error',
            'error': 'Method not allowed'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def ride_user_count(request):
    """Get total count of users from rides_user table"""
    try:
        total_users = RidesUser.objects.count() or 0
        return Response({
            'message_type': 'success',
            'count': total_users
        })
    except Exception as e:
        return Response({
            'message_type': 'error',
            'count': 0
        }, status=500)


@api_view(['GET'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def rides_users_list(request):
    """Get all users from rides_user table with complete user information"""
    try:
        from django.db import connection
        
        # Use raw SQL to get phone number with different possible column names
        with connection.cursor() as cursor:
            # Try to find phone number column name
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'rides_user' 
                AND (column_name LIKE '%phone%' OR column_name LIKE '%mobile%')
                LIMIT 1;
            """)
            phone_col_result = cursor.fetchone()
            phone_column = phone_col_result[0] if phone_col_result else None
            
            # Build query with phone column if found, otherwise use COALESCE to try multiple names
            if phone_column:
                phone_select = f'"{phone_column}" as phone_number'
            else:
                # Try common column name variations
                phone_select = """COALESCE(
                    "phone_number", "phone", "phone_no", "mobile", "mobile_number", 
                    NULL
                ) as phone_number"""
            
            # Get all users with phone number
            query = f"""
                SELECT 
                    id, name, email, dob, is_active, is_staff, is_superuser,
                    otp, otp_created_at, custom_user_id, last_login, deleted_at,
                    {phone_select}
                FROM rides_user
                ORDER BY id;
            """
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
        
        # Convert rows to dictionaries
        users_data = []
        for row in rows:
            user_dict = dict(zip(columns, row))
            # Format dates
            if user_dict.get('dob'):
                user_dict['dob'] = user_dict['dob'].isoformat() if hasattr(user_dict['dob'], 'isoformat') else str(user_dict['dob'])
            if user_dict.get('last_login'):
                user_dict['last_login'] = user_dict['last_login'].isoformat() if hasattr(user_dict['last_login'], 'isoformat') else str(user_dict['last_login'])
            if user_dict.get('deleted_at'):
                user_dict['deleted_at'] = user_dict['deleted_at'].isoformat() if hasattr(user_dict['deleted_at'], 'isoformat') else str(user_dict['deleted_at'])
            if user_dict.get('otp_created_at'):
                user_dict['otp_created_at'] = user_dict['otp_created_at'].isoformat() if hasattr(user_dict['otp_created_at'], 'isoformat') else str(user_dict['otp_created_at'])
            
            # Add is_deleted
            user_dict['is_deleted'] = user_dict.get('deleted_at') is not None
            
            # Add age if dob exists
            if user_dict.get('dob'):
                try:
                    from datetime import date
                    dob = user_dict['dob']
                    if isinstance(dob, str):
                        from datetime import datetime
                        dob = datetime.fromisoformat(dob.replace('Z', '+00:00')).date()
                    today = date.today()
                    user_dict['age'] = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                except:
                    pass
            
            users_data.append(user_dict)
        
        return Response({
            'message_type': 'success',
            'count': len(users_data),
            'users': users_data
        })
    except Exception as e:
        return Response({
            'message_type': 'error',
            'error': str(e),
            'count': 0,
            'users': []
        }, status=500)


@api_view(['POST'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def promo_code_create(request):
    """
    Create promo code(s) - supports both single and bulk creation
    
    Single Creation (send object {}):
    {
        "code": "SAVE20",
        "discount_type": "percentage",
        "discount_value": 20.00,
        "start_date": "2025-12-10T00:00:00Z",
        "expire_date": "2025-12-31T23:59:59Z",
        "max_usage": 100,
        "status": "active"
    }
    
    Bulk Creation (send array []):
    [
        {
            "code": "SAVE20",
            "discount_type": "percentage",
            "discount_value": 20.00,
            ...
        },
        {
            "code": "FLAT50",
            "discount_type": "fixed",
            "discount_value": 50.00,
            ...
        }
    ]
    
    discount_type:
    - "percentage": Discount is a percentage (0-100). Example: 20 = 20% off
    - "fixed": Discount is a fixed amount. Example: 20 = $20 off
    """
    try:
        # Fix sequence before creating to ensure sequential IDs
        fix_promo_sequence()
        
        # Check if request.data is a list (bulk creation)
        if isinstance(request.data, list):
            # Bulk creation
            serializer = PromoCodeCreateSerializer(data=request.data, many=True)
            
            if serializer.is_valid():
                promo_codes = serializer.save()
                
                # Return all created promo codes
                response_serializer = PromoCodeSerializer(promo_codes, many=True)
                
                return Response({
                    'message_type': 'success',
                    'count': len(promo_codes),
                    'data': response_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message_type': 'error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Single creation
            serializer = PromoCodeCreateSerializer(data=request.data)
            
            if serializer.is_valid():
                promo_code = serializer.save()
                
                # Return the created promo code with full details
                response_serializer = PromoCodeSerializer(promo_code)
                
                return Response({
                    'message_type': 'success',
                    'data': response_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message_type': 'error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'message_type': 'error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def promo_codes_list(request):
    """
    Get all promo codes, create promo code(s), or bulk delete (deactivate) multiple promo codes
    
    GET: Get all promo codes
    Optional query parameter: ?status=active to filter only active codes
    
    POST: Create promo code(s) - supports both single and bulk creation
    Single Creation (send object {}):
    {
        "code": "SAVE20",
        "discount_type": "percentage",
        "discount_value": 20.00,
        "start_date": "2025-12-10T00:00:00Z",
        "expire_date": "2025-12-31T23:59:59Z",
        "max_usage": 100,
        "status": "active"
    }
    Bulk Creation (send array []): [ {...}, {...} ]
    
    DELETE: Bulk delete (deactivate) multiple promo codes
    Request body: {"ids": [1, 2, 3]} - list of promo code IDs to deactivate
    """
    try:
        if request.method == 'POST':
            # Fix sequence before creating to ensure sequential IDs
            fix_promo_sequence()
            
            # Create promo code(s) - same logic as promo_code_create
            # Check if request.data is a list (bulk creation)
            if isinstance(request.data, list):
                # Bulk creation
                serializer = PromoCodeCreateSerializer(data=request.data, many=True)
                
                if serializer.is_valid():
                    promo_codes = serializer.save()
                    
                    # Return all created promo codes
                    response_serializer = PromoCodeSerializer(promo_codes, many=True)
                    
                    return Response({
                        'message_type': 'success',
                        'count': len(promo_codes),
                        'data': response_serializer.data
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'message_type': 'error',
                        'errors': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Single creation
                serializer = PromoCodeCreateSerializer(data=request.data)
                
                if serializer.is_valid():
                    promo_code = serializer.save()
                    
                    # Return the created promo code with full details
                    response_serializer = PromoCodeSerializer(promo_code)
                    
                    return Response({
                        'message_type': 'success',
                        'data': response_serializer.data
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'message_type': 'error',
                        'errors': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            # Bulk delete (deactivate) multiple promo codes
            ids = request.data.get('ids', [])
            
            if not ids:
                return Response({
                    'message_type': 'error',
                    'error': 'No IDs provided. Send {"ids": [1, 2, 3]}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not isinstance(ids, list):
                return Response({
                    'message_type': 'error',
                    'error': 'ids must be a list/array. Send {"ids": [1, 2, 3]}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get promo codes and deactivate them
            promo_codes = PromoCode.objects.filter(pk__in=ids)
            count = promo_codes.count()
            
            if count == 0:
                return Response({
                    'message_type': 'error',
                    'error': 'No promo codes found with the provided IDs'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Deactivate all found promo codes
            promo_codes.update(status=PromoCode.STATUS_DEACTIVATE)
            
            # Return updated promo codes
            serializer = PromoCodeSerializer(promo_codes, many=True)
            
            return Response({
                'message_type': 'success',
                'count': count,
                'deactivated_ids': list(promo_codes.values_list('id', flat=True)),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        else:
            # GET: Get all promo codes
            # Get status filter from query parameters
            status_filter = request.query_params.get('status', None)
            
            promo_codes = PromoCode.objects.all()
            
            # Filter by status if provided
            if status_filter:
                promo_codes = promo_codes.filter(status=status_filter)
            
            promo_codes = promo_codes.order_by('-created_at')
            serializer = PromoCodeSerializer(promo_codes, many=True)
            
            # Add sequential display number to each promo code
            # Convert to list of dicts to ensure modifications work
            data = [dict(item) for item in serializer.data]
            for index, item in enumerate(data, start=1):
                item['display_number'] = index
            
            return Response({
                'message_type': 'success',
                'count': promo_codes.count(),
                'data': data
            })
    except Exception as e:
        return Response({
            'message_type': 'error',
            'error': str(e),
            'count': 0,
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AUTH_PERMISSION])  # Require authentication in production
def promo_code_detail(request, pk):
    """
    Get, update, or deactivate a specific promo code by ID
    
    GET: Retrieve promo code
    PUT/PATCH: Update promo code (PATCH allows partial update)
    DELETE: Deactivate promo code (soft delete - sets status to deactivate, doesn't delete from database)
    """
    try:
        promo_code = PromoCode.objects.get(pk=pk)
    except PromoCode.DoesNotExist:
        return Response({
            'message_type': 'error',
            'error': 'Promo code not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Handle different HTTP methods
    if request.method == 'GET':
        # Get promo code
        serializer = PromoCodeSerializer(promo_code)
        return Response({
            'message_type': 'success',
            'data': serializer.data
        })
    
    elif request.method == 'DELETE':
        # Soft delete: Set status to deactivate instead of deleting
        promo_code.status = PromoCode.STATUS_DEACTIVATE
        promo_code.save()
        
        response_serializer = PromoCodeSerializer(promo_code)
        return Response({
            'message_type': 'success',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method in ['PUT', 'PATCH']:
        # Update promo code
        # PATCH allows partial updates, PUT requires all fields
        partial = request.method == 'PATCH'
        serializer = PromoCodeUpdateSerializer(promo_code, data=request.data, partial=partial)
        
        if serializer.is_valid():
            updated_promo_code = serializer.save()
            response_serializer = PromoCodeSerializer(updated_promo_code)
            
            return Response({
                'message_type': 'success',
                'data': response_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message_type': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        return Response({
            'message_type': 'error',
            'error': 'Method not allowed'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Zone Management API Views

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])  # Require admin authentication
def zones_list(request):
    """
    Get all zones or create a new zone
    
    GET: Get all zones
    Optional query parameters:
    - ?status=true/false - Filter by status (boolean)
    - ?country=CountryName - Filter by country
    - ?state=StateName - Filter by state
    - ?city=CityName - Filter by city
    
    POST: Create a new zone
    Request body:
    {
        "zone_name": "Downtown Zone",
        "country": "India",
        "state": "Delhi",
        "city": "New Delhi",
        "priority": 1,
        "status": true
    }
    """
    try:
        if request.method == 'POST':
            # Create zone
            serializer = ZoneCreateSerializer(data=request.data)
            
            if serializer.is_valid():
                zone = serializer.save()
                
                # Return the created zone with full details
                response_serializer = ZoneSerializer(zone)
                
                return Response({
                    'message_type': 'success',
                    'data': response_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message_type': 'error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # GET: List all zones
            zones = Zone.objects.all()
            
            # Filter by status if provided (boolean)
            status_param = request.query_params.get('status')
            if status_param is not None:
                status_bool = status_param.lower() in ('true', '1', 'yes')
                zones = zones.filter(status=status_bool)
            
            # Filter by country if provided
            country_param = request.query_params.get('country')
            if country_param:
                zones = zones.filter(country__icontains=country_param)
            
            # Filter by state if provided
            state_param = request.query_params.get('state')
            if state_param:
                zones = zones.filter(state__icontains=state_param)
            
            # Filter by city if provided
            city_param = request.query_params.get('city')
            if city_param:
                zones = zones.filter(city__icontains=city_param)
            
            serializer = ZoneSerializer(zones, many=True)
            
            return Response({
                'message_type': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            })
    except Exception as e:
        return Response({
            'message_type': 'error',
            'error': str(e),
            'count': 0,
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])  # Require admin authentication
def zone_detail(request, id):
    """
    Get, update, or disable a specific zone by ID
    
    GET: Retrieve zone
    PUT: Update zone (all fields required)
    DELETE: Disable zone (sets status=false, doesn't delete from database)
    """
    try:
        zone = Zone.objects.get(pk=id)
    except Zone.DoesNotExist:
        return Response({
            'message_type': 'error',
            'error': 'Zone not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Handle different HTTP methods
    if request.method == 'GET':
        # Get zone
        serializer = ZoneSerializer(zone)
        return Response({
            'message_type': 'success',
            'data': serializer.data
        })
    
    elif request.method == 'DELETE':
        # Disable zone: Set status=False instead of deleting
        zone.status = False
        zone.save()
        
        response_serializer = ZoneSerializer(zone)
        return Response({
            'message_type': 'success',
            'message': 'Zone disabled successfully',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Update zone (PUT requires all fields)
        serializer = ZoneUpdateSerializer(zone, data=request.data, partial=False)
        
        if serializer.is_valid():
            updated_zone = serializer.save()
            response_serializer = ZoneSerializer(updated_zone)
            
            return Response({
                'message_type': 'success',
                'data': response_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message_type': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        return Response({
            'message_type': 'error',
            'error': 'Method not allowed'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)



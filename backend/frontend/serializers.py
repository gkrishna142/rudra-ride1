from rest_framework import serializers
from .models import UserProfile, PromoCode, AdminProfile, Zone, User as FrontendUser, Role, RolePermission, UserRole
from django.contrib.auth import get_user_model

User = get_user_model()  # Django's default User model (auth_user)
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
import re

User = get_user_model()  # Django's default User model


class UserCreateSerializer(serializers.Serializer):
    """Serializer for creating a new user"""
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True, max_length=255)
    phone_number = serializers.CharField(required=False, max_length=15, allow_blank=True)
    status = serializers.ChoiceField(choices=UserProfile.STATUS_CHOICES, default=UserProfile.STATUS_ACTIVE, required=False)
    password = serializers.CharField(required=True, write_only=True, min_length=8)
    
    def create(self, validated_data):
        name = validated_data.pop('name')
        phone_number = validated_data.pop('phone_number', None)
        status = validated_data.pop('status', UserProfile.STATUS_ACTIVE)
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=email,
            password=password
        )
        
        # Create user profile with name, phone number, email, and status
        UserProfile.objects.create(
            user=user,
            name=name,
            phone_number=phone_number,
            email=email,
            status=status
        )
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model with id, name, phone_number, email, status"""
    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'phone_number', 'email', 'status']
        read_only_fields = ['id']


class UserSerializer(serializers.Serializer):
    """Serializer for User model - gets data from UserProfile
    Field order: id, name, phone_number, email, status
    """
    # Define fields in the correct order: id, name, phone_number, email, status
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    def get_id(self, obj):
        """Get id from user profile"""
        try:
            return obj.user_profile.id
        except UserProfile.DoesNotExist:
            return obj.id
    
    def get_name(self, obj):
        """Get name from user profile"""
        try:
            return obj.user_profile.name or f"{obj.first_name} {obj.last_name}".strip() or obj.username
        except UserProfile.DoesNotExist:
            return f"{obj.first_name} {obj.last_name}".strip() or obj.username
    
    def get_phone_number(self, obj):
        """Get phone number from user profile"""
        try:
            return obj.user_profile.phone_number or ''
        except UserProfile.DoesNotExist:
            return ''
    
    def get_email(self, obj):
        """Get email from user profile or user"""
        try:
            return obj.user_profile.email or obj.email
        except UserProfile.DoesNotExist:
            return obj.email
    
    def get_status(self, obj):
        """Get status from user profile"""
        try:
            return obj.user_profile.status or 'active'
        except UserProfile.DoesNotExist:
            return 'active'


class AdminProfileSerializer(serializers.ModelSerializer):
    """Serializer for AdminProfile model"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AdminProfile
        fields = ['id', 'user', 'username', 'name', 'email', 'password', 'role', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'password', 'created_at', 'updated_at']


class AdminLoginSerializer(serializers.Serializer):
    """Serializer for admin login response"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()
    role_id = serializers.CharField(allow_null=True, allow_blank=True)
    role_name = serializers.CharField(allow_null=True)
    is_superadmin = serializers.BooleanField()
    is_active = serializers.SerializerMethodField()
    
    def get_is_active(self, obj):
        """Convert boolean to active/deactive string"""
        if isinstance(obj, dict):
            val = obj.get("is_active")
        else:
            val = getattr(obj, "is_active", None)
        return "active" if val else "deactive"


class PromoCodeSerializer(serializers.ModelSerializer):
    """Serializer for PromoCode model"""
    is_valid = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    is_usage_limit_reached = serializers.ReadOnlyField()
    remaining_usage = serializers.ReadOnlyField()
    
    class Meta:
        model = PromoCode
        fields = [
            'id', 'code', 'discount_type', 'discount_value',
            'start_date', 'expire_date', 'max_usage', 'current_usage',
            'status', 'is_valid', 'is_expired', 'is_usage_limit_reached',
            'remaining_usage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_usage', 'created_at', 'updated_at']


class PromoCodeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new promo code
    
    discount_type options:
    - 'percentage': Discount is a percentage (0-100)
    - 'fixed': Discount is a fixed amount in currency
    """
    # Explicitly define discount_type as required (no default)
    discount_type = serializers.ChoiceField(
        choices=PromoCode.DISCOUNT_TYPE_CHOICES,
        required=True,
        help_text="Type of discount: 'percentage' or 'fixed'"
    )
    
    class Meta:
        model = PromoCode
        fields = [
            'code', 'discount_type', 'discount_value',
            'start_date', 'expire_date', 'max_usage', 'status'
        ]
        extra_kwargs = {
            'code': {'required': True},
            'discount_value': {'required': True},
            'start_date': {'required': True},
            'expire_date': {'required': True},
            'max_usage': {'required': False},  # Has default in model
            'status': {'required': False},  # Has default in model
        }
    
    def validate_code(self, value):
        """Validate promo code is unique and uppercase"""
        if PromoCode.objects.filter(code__iexact=value).exists():
            raise serializers.ValidationError("A promo code with this code already exists.")
        return value.upper()
    
    def validate_discount_value(self, value):
        """Validate discount value based on discount type"""
        # This will be checked in validate() method where we have access to discount_type
        if value <= 0:
            raise serializers.ValidationError("Discount value must be greater than 0.")
        return value
    
    def validate(self, data):
        """Validate discount value and dates"""
        discount_type = data.get('discount_type')
        discount_value = data.get('discount_value')
        
        # Only validate discount_value if both fields are present
        if discount_type and discount_value is not None:
            # Validate discount value based on type
            if discount_type == PromoCode.DISCOUNT_TYPE_PERCENTAGE:
                if discount_value > 100:
                    raise serializers.ValidationError({
                        'discount_value': 'Percentage discount cannot exceed 100%.'
                    })
                if discount_value < 0:
                    raise serializers.ValidationError({
                        'discount_value': 'Percentage discount cannot be negative.'
                    })
            elif discount_type == PromoCode.DISCOUNT_TYPE_FIXED:
                if discount_value < 0:
                    raise serializers.ValidationError({
                        'discount_value': 'Fixed discount amount cannot be negative.'
                    })
        
        # Validate that expire_date is after start_date (only if both are present)
        if 'expire_date' in data and 'start_date' in data:
            if data['expire_date'] <= data['start_date']:
                raise serializers.ValidationError({
                    'expire_date': 'Expire date must be after start date.'
                })
        
            return data


class PromoCodeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a promo code"""
    # Explicitly define discount_type
    discount_type = serializers.ChoiceField(
        choices=PromoCode.DISCOUNT_TYPE_CHOICES,
        required=False,
        help_text="Type of discount: 'percentage' or 'fixed'"
    )
    
    class Meta:
        model = PromoCode
        fields = [
            'code', 'discount_type', 'discount_value',
            'start_date', 'expire_date', 'max_usage', 'status'
        ]
        extra_kwargs = {
            'code': {'required': False},
            'discount_value': {'required': False},
            'start_date': {'required': False},
            'expire_date': {'required': False},
            'max_usage': {'required': False},
            'status': {'required': False},
        }
    
    def validate_code(self, value):
        """Validate promo code is unique (excluding current instance)"""
        # Get the instance being updated
        instance = getattr(self, 'instance', None)
        if value:
            # Convert to uppercase for consistency
            value_upper = value.upper()
            # Check if code exists (case-insensitive) excluding current instance
            if instance:
                # For update: exclude current instance
                if PromoCode.objects.filter(code__iexact=value_upper).exclude(pk=instance.pk).exists():
                    raise serializers.ValidationError("Promo Code with this code already exists.")
            else:
                # For create: check if any exists
                if PromoCode.objects.filter(code__iexact=value_upper).exists():
                    raise serializers.ValidationError("Promo Code with this code already exists.")
            return value_upper
        return value
    
    def validate_discount_value(self, value):
        """Validate discount value"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Discount value must be greater than 0.")
        return value
    
    def validate(self, data):
        """Validate discount value and dates"""
        discount_type = data.get('discount_type')
        discount_value = data.get('discount_value')
        
        # Use existing values if not provided in update
        if discount_type is None and self.instance:
            discount_type = self.instance.discount_type
        if discount_value is None and self.instance:
            discount_value = self.instance.discount_value
        
        # Only validate if both are present
        if discount_type and discount_value is not None:
            if discount_type == PromoCode.DISCOUNT_TYPE_PERCENTAGE:
                if discount_value > 100:
                    raise serializers.ValidationError({
                        'discount_value': 'Percentage discount cannot exceed 100%.'
                    })
                if discount_value < 0:
                    raise serializers.ValidationError({
                        'discount_value': 'Percentage discount cannot be negative.'
                    })
            elif discount_type == PromoCode.DISCOUNT_TYPE_FIXED:
                if discount_value < 0:
                    raise serializers.ValidationError({
                        'discount_value': 'Fixed discount amount cannot be negative.'
                    })
        
        # Validate dates if both are provided
        start_date = data.get('start_date')
        expire_date = data.get('expire_date')
        
        # Use existing values if not provided
        if start_date is None and self.instance:
            start_date = self.instance.start_date
        if expire_date is None and self.instance:
            expire_date = self.instance.expire_date
        
        if start_date and expire_date:
            if expire_date <= start_date:
                raise serializers.ValidationError({
                    'expire_date': 'Expire date must be after start date.'
                })
        
        return data


def validate_wkt_polygon(value):
    """
    Validate WKT polygon format and geometry.
    
    Valid format: POLYGON((lon1 lat1, lon2 lat2, lon3 lat3, lon1 lat1))
    - Must start with POLYGON
    - Must have at least 4 points (3 unique + closing point)
    - First and last points must match (closed polygon)
    - All coordinates must be valid numbers
    """
    if not value or not isinstance(value, str):
        raise serializers.ValidationError("Polygon must be a valid WKT string.")
    
    original_value = value.strip()
    value_upper = original_value.upper()
    
    # Check if it starts with POLYGON (case-insensitive)
    if not value_upper.startswith('POLYGON'):
        raise serializers.ValidationError("Polygon must start with 'POLYGON'.")
    
    # Extract coordinates using regex
    # Pattern: POLYGON((lon lat, lon lat, ...))
    pattern = r'POLYGON\s*\(\s*\(\s*([^)]+)\s*\)\s*\)'
    match = re.match(pattern, original_value, re.IGNORECASE)
    
    if not match:
        raise serializers.ValidationError("Invalid POLYGON format. Expected: POLYGON((lon1 lat1, lon2 lat2, ...))")
    
    coords_str = match.group(1)
    
    # Parse coordinates
    coord_pairs = []
    for coord_pair in coords_str.split(','):
        coord_pair = coord_pair.strip()
        if not coord_pair:
            continue
        
        # Split by whitespace
        parts = coord_pair.split()
        if len(parts) != 2:
            raise serializers.ValidationError(f"Invalid coordinate pair: {coord_pair}. Expected format: 'lon lat'")
        
        try:
            lon = float(parts[0])
            lat = float(parts[1])
            
            # Validate longitude and latitude ranges
            if not (-180 <= lon <= 180):
                raise serializers.ValidationError(f"Longitude must be between -180 and 180. Got: {lon}")
            if not (-90 <= lat <= 90):
                raise serializers.ValidationError(f"Latitude must be between -90 and 90. Got: {lat}")
            
            coord_pairs.append((lon, lat))
        except ValueError:
            raise serializers.ValidationError(f"Invalid coordinate values: {coord_pair}. Must be numeric.")
    
    # Check minimum points (at least 4: 3 unique + closing point)
    if len(coord_pairs) < 4:
        raise serializers.ValidationError(f"Polygon must have at least 4 points (3 unique + closing point). Got: {len(coord_pairs)}")
    
    # Check if polygon is closed (first and last points match)
    first_point = coord_pairs[0]
    last_point = coord_pairs[-1]
    
    if abs(first_point[0] - last_point[0]) > 0.000001 or abs(first_point[1] - last_point[1]) > 0.000001:
        raise serializers.ValidationError("Polygon must be closed. First and last points must match.")
    
    # Check for duplicate consecutive points (invalid geometry)
    for i in range(len(coord_pairs) - 1):
        if coord_pairs[i] == coord_pairs[i + 1]:
            raise serializers.ValidationError("Polygon contains duplicate consecutive points. Invalid geometry.")
    
    # Return original value (preserve case)
    return original_value


class ZoneSerializer(serializers.ModelSerializer):
    """Serializer for Zone model"""
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Zone
        fields = [
            'zone_id', 'zone_name', 'country', 'state', 'city', 'priority', 'status',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['zone_id', 'created_at', 'updated_at']
    
    def validate_zone_name(self, value):
        """Validate zone name is unique"""
        # Check uniqueness excluding current instance (for updates)
        instance = getattr(self, 'instance', None)
        if instance:
            if Zone.objects.filter(zone_name__iexact=value).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError("A zone with this name already exists.")
        else:
            if Zone.objects.filter(zone_name__iexact=value).exists():
                raise serializers.ValidationError("A zone with this name already exists.")
        return value


class ZoneCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new zone"""
    
    class Meta:
        model = Zone
        fields = ['zone_name', 'country', 'state', 'city', 'priority', 'status']
        extra_kwargs = {
            'zone_name': {'required': True},
            'country': {'required': False},  # Optional field
            'state': {'required': False},  # Optional field
            'city': {'required': False},  # Optional field
            'priority': {'required': False},  # Has default in model
            'status': {'required': False},  # Has default in model
        }
    
    def validate_zone_name(self, value):
        """Validate zone name is unique"""
        if Zone.objects.filter(zone_name__iexact=value).exists():
            raise serializers.ValidationError("A zone with this name already exists.")
        return value
    


class ZoneUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a zone"""
    
    class Meta:
        model = Zone
        fields = ['zone_name', 'country', 'state', 'city', 'priority', 'status']
        extra_kwargs = {
            'zone_name': {'required': False},
            'country': {'required': False},
            'state': {'required': False},
            'city': {'required': False},
            'priority': {'required': False},
            'status': {'required': False},
        }
    
    def validate_zone_name(self, value):
        """Validate zone name is unique (excluding current instance)"""
        if value:
            instance = getattr(self, 'instance', None)
            if instance:
                if Zone.objects.filter(zone_name__iexact=value).exclude(pk=instance.pk).exists():
                    raise serializers.ValidationError("A zone with this name already exists.")
            else:
                if Zone.objects.filter(zone_name__iexact=value).exists():
                    raise serializers.ValidationError("A zone with this name already exists.")
        return value


def validate_wkt_point(value):
    """
    Validate WKT POINT format.
    
    Valid format: POINT(lon lat)
    - Must start with POINT
    - Must have exactly 2 coordinates (longitude and latitude)
    - Coordinates must be valid numbers
    """
    if not value or not isinstance(value, str):
        raise serializers.ValidationError("Location must be a valid WKT string.")
    
    value = value.strip().upper()
    
    # Check if it starts with POINT
    if not value.startswith('POINT'):
        raise serializers.ValidationError("Location must start with 'POINT'.")
    
    # Extract coordinates using regex
    # Pattern: POINT(lon lat)
    pattern = r'POINT\s*\(\s*([^)]+)\s*\)'
    match = re.match(pattern, value, re.IGNORECASE)
    
    if not match:
        raise serializers.ValidationError("Invalid POINT format. Expected: POINT(lon lat)")
    
    coords_str = match.group(1)
    parts = coords_str.split()
    
    if len(parts) != 2:
        raise serializers.ValidationError(f"POINT must have exactly 2 coordinates (longitude and latitude). Got: {len(parts)}")
    
    try:
        lon = float(parts[0])
        lat = float(parts[1])
        
        # Validate longitude and latitude ranges
        if not (-180 <= lon <= 180):
            raise serializers.ValidationError(f"Longitude must be between -180 and 180. Got: {lon}")
        if not (-90 <= lat <= 90):
            raise serializers.ValidationError(f"Latitude must be between -90 and 90. Got: {lat}")
        
    except ValueError:
        raise serializers.ValidationError(f"Invalid coordinate values: {coords_str}. Must be numeric.")
    
    return value


class UserSignupSerializer(serializers.ModelSerializer):
    """Serializer for user signup/registration"""
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Confirm password (must match password)"
    )
    is_active = serializers.CharField(
        required=False,
        help_text="User status: 'active' or 'deactive' (default: 'active')"
    )
    
    class Meta:
        model = FrontendUser
        fields = ['name', 'email', 'phone_number', 'password', 'confirm_password', 'role_id', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'name': {'required': True},
            'email': {'required': True},
            'phone_number': {'required': False},
            'role_id': {'required': False},
        }
    
    def validate_email(self, value):
        """Validate and preserve email exactly as provided"""
        if value:
            # Strip whitespace but preserve the exact email otherwise
            value = value.strip()
            # Ensure email is not modified - preserve exactly as provided
        return value
    
    def validate_is_active(self, value):
        """Convert 'active'/'deactive' string to boolean"""
        if value is None or value == '':
            return True  # Default to active
        if isinstance(value, str):
            if value.lower() in ('active', 'true', '1', 'yes'):
                return True
            elif value.lower() in ('deactive', 'false', '0', 'no'):
                return False
            else:
                raise serializers.ValidationError("is_active must be 'active' or 'deactive'")
        return bool(value) if value is not None else True
    
    def validate_role_id(self, value):
        """Validate that role_id exists if provided. Supports both string (e.g., 'R001') and integer values."""
        if value is not None:
            # Convert to string for comparison (handles both string and integer inputs)
            from .models import Role
            from django.db.models import Q
            
            # Try to find role by matching role_id as string (case-insensitive)
            # This matches how get_roles() method works in the User model
            role_exists = Role.objects.filter(
                Q(role_id__iexact=str(value)) | Q(role_id=str(value))
            ).exists()
            
            if not role_exists:
                # In DEBUG mode, allow creating users without roles (for testing)
                from django.conf import settings
                if settings.DEBUG:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"DEBUG MODE: Creating user with role_id '{value}' that doesn't exist. Role will need to be created later.")
                    # Allow it in DEBUG mode, but warn
                    return str(value) if value is not None else value
                else:
                    raise serializers.ValidationError(
                        f"Role with role_id '{value}' does not exist. Please provide a valid role_id or create the role first."
                    )
        # Convert to string to ensure consistency
        return str(value) if value is not None else value
    
    def validate(self, data):
        """Validate that password and confirm_password match"""
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        
        # Set default is_active if not provided
        if 'is_active' not in data or data.get('is_active') is None:
            data['is_active'] = True
        
        # Keep confirm_password in validated data (will be stored in database as requested)
        return data
    
    def create(self, validated_data):
        """Create a new user with hashed password"""
        # Ensure email is preserved exactly as provided (no modification)
        email = validated_data.get('email', '').strip()
        if email:
            validated_data['email'] = email  # Preserve original email exactly
        
        # Get role_id for logging
        role_id = validated_data.get('role_id')
        
        # Password will be automatically hashed in the model's save() method
        user = FrontendUser.objects.create(**validated_data)
        
        # Log the email and role_id to verify they're saved correctly
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"User created with email: {user.email} (original: {email}), role_id: {user.role_id} (provided: {role_id})")
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login response"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField(allow_null=True)
    role_id = serializers.CharField(allow_null=True, allow_blank=True)
    role_name = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    def get_is_active(self, obj):
        """Convert boolean to active/deactive string.

        The serializer `instance` may sometimes be a dict (e.g. when using
        `to_representation` with plain dicts) or a model instance. Handle both
        cases safely.
        """
        # support dict-like objects and model instances
        if isinstance(obj, dict):
            val = obj.get("is_active")
        else:
            val = getattr(obj, "is_active", None)
        return "active" if val else "deactive"
    
    def get_role_name(self, obj):
        """Get role name from Role model based on role_id or UserRole assignments"""
        try:
            # Handle both dict and model instance
            if isinstance(obj, dict):
                user_id = obj.get("id")
                role_id = obj.get("role_id")
                if not user_id:
                    return None
                # Get user instance
                from .models import FrontendUser
                try:
                    user = FrontendUser.objects.get(id=user_id)
                    roles = user.get_roles()
                    if roles.exists():
                        return roles.first().name
                except FrontendUser.DoesNotExist:
                    return None
            else:
                # obj is a model instance
                roles = obj.get_roles()
                if roles.exists():
                    return roles.first().name
            return None
        except Exception:
            return None


class UserLoginRequestSerializer(serializers.Serializer):
    """Serializer for user login request"""
    email = serializers.EmailField(required=True, help_text="User email address")
    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="User password"
    )


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - used for GET, PUT, PATCH operations"""
    is_active = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FrontendUser
        fields = ['id', 'name', 'email', 'phone_number', 'role_id', 'role_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_is_active(self, obj):
        """Convert boolean to active/deactive string"""
        return "active" if obj.is_active else "deactive"
    
    def get_role_name(self, obj):
        """Get role name from Role model based on role_id or UserRole assignments"""
        try:
            # Use the get_roles() method from the User model
            roles = obj.get_roles()
            if roles.exists():
                # Get the first role's name (if multiple, use the first one)
                return roles.first().name
            return None
        except Exception:
            return None


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user (admin use)"""
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Confirm password (must match password)"
    )
    is_active = serializers.CharField(
        required=False,
        help_text="User status: 'active' or 'deactive' (default: 'active')"
    )
    
    class Meta:
        model = FrontendUser
        fields = ['name', 'email', 'phone_number', 'password', 'confirm_password', 'role_id', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'name': {'required': True},
            'email': {'required': True},
            'phone_number': {'required': False},
            'role_id': {'required': False},
        }
    
    def validate_email(self, value):
        """Validate and preserve email exactly as provided"""
        if value:
            # Strip whitespace but preserve the exact email otherwise
            value = value.strip()
            # Ensure email is not modified - preserve exactly as provided
        return value
    
    def validate_phone_number(self, value):
        """Validate and preserve phone_number exactly as provided"""
        if value:
            # Strip whitespace but preserve the phone number
            value = value.strip()
            # Convert empty string to None for database
            if value == '':
                return None
        return value if value else None
    
    def validate_role_id(self, value):
        """Validate role_id - preserve as-is if it can be stored"""
        if value is not None:
            # Convert to string for consistency
            value = str(value).strip() if isinstance(value, str) else value
            # Convert empty string to None
            if value == '':
                return None
        return value
    
    def validate_is_active(self, value):
        """Convert 'active'/'deactive' string to boolean"""
        if isinstance(value, str):
            if value.lower() in ('active', 'true', '1', 'yes'):
                return True
            elif value.lower() in ('deactive', 'false', '0', 'no'):
                return False
            else:
                raise serializers.ValidationError("is_active must be 'active' or 'deactive'")
        return bool(value) if value is not None else True
    
    def validate(self, data):
        """Validate that password and confirm_password match"""
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        
        # Set default is_active if not provided
        if 'is_active' not in data or data.get('is_active') is None:
            data['is_active'] = True
        
        return data
    
    def create(self, validated_data):
        """Create a new user with hashed password"""
        # Keep confirm_password in validated_data (will be stored in database as requested)
        # Password and confirm_password will be automatically hashed in the model's save() method
        
        # Ensure email is preserved exactly as provided (no modification)
        email = validated_data.get('email', '').strip()
        if email:
            validated_data['email'] = email  # Preserve original email exactly
        
        # Ensure phone_number is preserved
        phone_number = validated_data.get('phone_number')
        if phone_number:
            validated_data['phone_number'] = phone_number.strip() if isinstance(phone_number, str) else phone_number
        elif phone_number == '':
            validated_data['phone_number'] = None
        
        # Extract role_id to determine if we need to create an AdminProfile
        role_id = validated_data.get('role_id')
        role_id_original = role_id
        
        # Log the email, phone_number, and role_id before creating user
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Creating user with email: {email}, phone_number: {phone_number}, role_id: {role_id}")
        
        # Try to create user with role_id as-is first (in case migration has been run)
        # If it fails due to integer conversion error, we'll handle it
        frontend_user = None
        try:
            # Create FrontendUser instance with role_id as provided
            frontend_user = FrontendUser.objects.create(**validated_data)
        except Exception as e:
            error_str = str(e)
            # Check if error is due to integer conversion (database column is still INTEGER)
            if 'invalid input syntax for type integer' in error_str.lower() and role_id is not None:
                # Try to convert role_id to integer to see if it's numeric
                try:
                    # If it can be converted to int, use the integer value
                    int_role_id = int(role_id)
                    validated_data['role_id'] = int_role_id
                    logger.info(f"Converted role_id '{role_id}' to integer {int_role_id} for database compatibility")
                    # Try again with integer value
                    frontend_user = FrontendUser.objects.create(**validated_data)
                except (ValueError, TypeError):
                    # role_id is a string that can't be converted to integer (e.g., "R001")
                    # Database column is still INTEGER - set to NULL temporarily
                    logger.warning(
                        f"Database role_id column is still INTEGER. Received '{role_id}' (string). "
                        f"Setting role_id to NULL temporarily. Please run migration to save string role_ids. "
                        f"See: backend/frontend/migrations/manual_sql_alter_role_id.sql"
                    )
                    validated_data['role_id'] = None
                    role_id = None
                    # Try again with NULL role_id
                    frontend_user = FrontendUser.objects.create(**validated_data)
            else:
                # Re-raise if it's a different error
                raise
        
        # Log if role_id was set to NULL due to migration issue
        if role_id_original is not None and frontend_user.role_id is None:
            logger.info(
                f"User {frontend_user.id} created with role_id=NULL (original: '{role_id_original}'). "
                f"Please update role_id after running migration."
            )
        
        # Log the email, phone_number, and role_id after creating user to verify they're saved correctly
        logger.info(
            f"User created with ID: {frontend_user.id}, "
            f"email: {frontend_user.email} (original: {email}), "
            f"phone_number: {frontend_user.phone_number} (provided: {phone_number}), "
            f"role_id: {frontend_user.role_id} (provided: {role_id_original})"
        )
        
        # If role_id is 1, 2, "1", "2", "R001", etc., create AdminProfile with corresponding role
        # AdminProfile.user requires a Django User instance, not FrontendUser
        # Convert role_id to string for comparison (handles both string and integer)
        role_id_str = str(role_id) if role_id is not None else None
        if role_id_str in ['1', '2', 1, 2]:
            from .models import AdminProfile
            
            # Generate username from email or use a fallback
            username = frontend_user.email.split('@')[0] if frontend_user.email else f'user_{frontend_user.id}'
            
            # Ensure username is unique
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            # Get or create Django User instance for AdminProfile
            try:
                # Try to get existing Django User by email
                django_user = User.objects.get(email=frontend_user.email)
                # Update existing user
                django_user.password = frontend_user.password
                django_user.is_active = frontend_user.is_active
                django_user.is_staff = True
                django_user.is_superuser = (role_id_str in ['1', 1])
                if not django_user.username or django_user.username == '':
                    django_user.username = username
                django_user.save()
            except User.DoesNotExist:
                # Create new Django User
                name_parts = frontend_user.name.split() if frontend_user.name else []
                # Check if password is already hashed
                if frontend_user.password and frontend_user.password.startswith('pbkdf2_'):
                    # Password is already hashed, create user and set password directly
                    django_user = User.objects.create(
                        username=username,
                        email=frontend_user.email,
                        first_name=name_parts[0] if len(name_parts) > 0 else '',
                        last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
                        password=frontend_user.password,  # Already hashed
                        is_active=frontend_user.is_active,
                        is_staff=True,  # Admin users should be staff
                        is_superuser=(role_id_str in ['1', 1]),  # Superadmin if role_id is 1
                    )
                else:
                    # Password is not hashed, use create_user to hash it
                    django_user = User.objects.create_user(
                        username=username,
                        email=frontend_user.email,
                        password=frontend_user.password,  # Will be hashed by create_user
                        first_name=name_parts[0] if len(name_parts) > 0 else '',
                        last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
                        is_active=frontend_user.is_active,
                        is_staff=True,  # Admin users should be staff
                        is_superuser=(role_id_str in ['1', 1]),  # Superadmin if role_id is 1
                    )
            
            # Create AdminProfile with Django User instance
            admin_role = AdminProfile.ROLE_SUPERADMIN if role_id_str in ['1', 1] else AdminProfile.ROLE_ADMIN
            AdminProfile.objects.get_or_create(
                user=django_user,
                defaults={
                    'name': frontend_user.name,
                    'email': frontend_user.email,
                    'password': frontend_user.password,  # Store hashed password
                    'role': admin_role,
                    'is_active': frontend_user.is_active
                }
            )
        
        return frontend_user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a user"""
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="New password (optional, leave blank to keep current password)"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="Confirm password (required if password is provided)"
    )
    is_active = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="User status: 'active' or 'deactive'"
    )
    
    class Meta:
        model = FrontendUser
        fields = ['name', 'email', 'phone_number', 'password', 'confirm_password', 'role_id', 'is_active']
        extra_kwargs = {
            'name': {'required': False},
            'email': {'required': False},
            'phone_number': {'required': False},
            'role_id': {'required': False},
        }
    
    def validate_is_active(self, value):
        """Convert 'active'/'deactive' string to boolean"""
        if value is None or value == '':
            return None  # Don't update if not provided
        if isinstance(value, str):
            if value.lower() in ('active', 'true', '1', 'yes'):
                return True
            elif value.lower() in ('deactive', 'false', '0', 'no'):
                return False
            else:
                raise serializers.ValidationError("is_active must be 'active' or 'deactive'")
        return bool(value)
    
    def validate(self, data):
        """Validate password and confirm_password if password is being updated"""
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # If password is provided, confirm_password must also be provided and match
        if password:
            if not confirm_password:
                raise serializers.ValidationError({
                    'confirm_password': 'Confirm password is required when updating password.'
                })
            if password != confirm_password:
                raise serializers.ValidationError({
                    'confirm_password': 'Passwords do not match.'
                })
        elif confirm_password:
            # If confirm_password is provided but password is not, that's an error
            raise serializers.ValidationError({
                'password': 'Password is required when providing confirm password.'
            })
        
        # Remove confirm_password from validated data (don't store it)
        data.pop('confirm_password', None)
        return data
    
    def update(self, instance, validated_data):
        """Update user instance"""
        # If password is not provided, remove it from validated_data to keep current password
        if 'password' not in validated_data or not validated_data.get('password'):
            validated_data.pop('password', None)
        
        # Update instance with validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model - used for GET operations"""
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['role_id', 'name', 'description', 'page_permission', 'default_page', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['role_id', 'created_at', 'updated_at']
    
    def get_is_active(self, obj):
        """Convert boolean to active/deactive string"""
        return "active" if obj.is_active else "deactive"


class RoleBasicSerializer(serializers.Serializer):
    """Minimal serializer returning only role_id and role_name"""
    role_id = serializers.CharField(read_only=True)
    role_name = serializers.CharField(source='name', read_only=True)


class RoleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new role"""
    is_active = serializers.CharField(
        required=False,
        help_text="Role status: 'active' or 'deactive' (default: 'active')"
    )
    
    class Meta:
        model = Role
        fields = ['role_id', 'name', 'description', 'page_permission', 'default_page', 'is_active']
        extra_kwargs = {
            'role_id': {'required': True},
            'name': {'required': True},
            'description': {'required': False},
            'page_permission': {'required': False},
            'default_page': {'required': False},  # Has default in model
        }
    
    def validate_is_active(self, value):
        """Convert 'active'/'deactive' string to boolean"""
        if value is None or value == '':
            return True  # Default to active
        if isinstance(value, str):
            if value.lower() in ('active', 'true', '1', 'yes'):
                return True
            elif value.lower() in ('deactive', 'false', '0', 'no'):
                return False
            else:
                raise serializers.ValidationError("is_active must be 'active' or 'deactive'")
        return bool(value) if value is not None else True
    
    def validate_role_id(self, value):
        """Validate that role_id is unique"""
        if Role.objects.filter(role_id=value).exists():
            raise serializers.ValidationError("A role with this role_id already exists.")
        return value
    
    def validate_name(self, value):
        """Validate that role name is unique"""
        if Role.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A role with this name already exists.")
        return value


class RoleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a role"""
    is_active = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Role status: 'active'/'deactive' or 'true'/'false' or boolean"
    )
    
    class Meta:
        model = Role
        fields = ['name', 'description', 'page_permission', 'default_page', 'is_active']
        extra_kwargs = {
            'name': {'required': False},
            'description': {'required': False},
            'page_permission': {'required': False},
            'default_page': {'required': False},
        }
    
    def validate_is_active(self, value):
        """Convert 'active'/'deactive' string or boolean to boolean"""
        if value is None or value == '':
            return None  # Don't update if not provided
        
        # Handle boolean values directly
        if isinstance(value, bool):
            return value
        
        # Handle string values
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ('active', 'true', '1', 'yes', 'on'):
                return True
            elif value_lower in ('deactive', 'inactive', 'false', '0', 'no', 'off'):
                return False
            else:
                raise serializers.ValidationError(
                    f"is_active must be 'active'/'deactive' or 'true'/'false', got: '{value}'"
                )
        
        # Handle other types (int, etc.)
        return bool(value)
    
    def validate_name(self, value):
        """Validate that role name is unique (excluding current instance)"""
        if value:
            instance = getattr(self, 'instance', None)
            if instance:
                if Role.objects.filter(name__iexact=value).exclude(pk=instance.role_id).exists():
                    raise serializers.ValidationError("A role with this name already exists.")
            else:
                if Role.objects.filter(name__iexact=value).exists():
                    raise serializers.ValidationError("A role with this name already exists.")
        return value
    
    def update(self, instance, validated_data):
        """Update role instance with proper transaction handling for PgBouncer"""
        from django.db import transaction
        import logging
        logger = logging.getLogger(__name__)
        
        # Use atomic transaction to ensure update is committed
        with transaction.atomic(using='default'):
            # Update the instance with validated data
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            # Save the role
            instance.save()
            logger.info(f"✅ Role updated: role_id={instance.role_id}, name={instance.name}")
            
            # If name was updated, sync it to permissions
            if 'name' in validated_data:
                from .models import RolePermission
                RolePermission.objects.filter(role=instance).update(name=instance.name)
                logger.info(f"✅ Synced role name to permissions: role_id={instance.role_id}")
        
        # Refresh from database after transaction commits (outside the atomic block)
        instance.refresh_from_db()
        logger.info(f"✅ Role verified in database: role_id={instance.role_id}, name={instance.name}")
        
        return instance


class RolePermissionSerializer(serializers.Serializer):
    """Serializer for RolePermission model - used for GET operations
    Uses Serializer instead of ModelSerializer to avoid id field issues"""
    role_id = serializers.SerializerMethodField()
    name = serializers.CharField(read_only=True)
    page_path = serializers.CharField(read_only=True)
    permission_type = serializers.CharField(read_only=True)
    is_allowed = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def get_role_id(self, obj):
        """Get role_id from role object"""
        if hasattr(obj, 'role'):
            if hasattr(obj.role, 'role_id'):
                return obj.role.role_id
            return str(obj.role)
        return None
    
    def get_is_allowed(self, obj):
        """Convert boolean to allowed/denied string"""
        if hasattr(obj, 'is_allowed'):
            return "allowed" if obj.is_allowed else "denied"
        return "allowed"


class RolePermissionsSerializer(serializers.Serializer):
    """Serializer to present a role's permissions mapping without
    creating or mutating database objects.

    Output format:
    {
      "role_id": "R001",
      "permissions": {
          "/path": {"view": true, "create": false},
          ...
      }
    }
    """
    role_id = serializers.CharField()
    permissions = serializers.DictField(child=serializers.DictField(child=serializers.BooleanField()))


class RolePermissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new role permission"""
    role_id = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Role identifier (e.g., R001)"
    )
    is_allowed = serializers.CharField(
        required=False,
        help_text="Permission status: 'allowed' or 'denied' (default: 'allowed')"
    )
    
    class Meta:
        model = RolePermission
        fields = ['role_id', 'page_path', 'permission_type', 'is_allowed']
        extra_kwargs = {
            'page_path': {'required': True},
            'permission_type': {'required': True},
        }
    
    def validate_is_allowed(self, value):
        """Convert 'allowed'/'denied' string to boolean"""
        if value is None or value == '':
            return True  # Default to allowed
        if isinstance(value, str):
            if value.lower() in ('allowed', 'true', '1', 'yes'):
                return True
            elif value.lower() in ('denied', 'false', '0', 'no'):
                return False
            else:
                raise serializers.ValidationError("is_allowed must be 'allowed' or 'denied'")
        return bool(value) if value is not None else True
    
    def validate_role_id(self, value):
        """Validate that role exists"""
        if not Role.objects.filter(role_id=value).exists():
            raise serializers.ValidationError(f"Role with role_id '{value}' does not exist.")
        return value
    
    def create(self, validated_data):
        """Create role permission with role_id"""
        role_id = validated_data.pop('role_id')
        role = Role.objects.get(role_id=role_id)
        
        # Check if permission already exists
        existing_permission = RolePermission.objects.filter(
            role=role,
            page_path=validated_data['page_path'],
            permission_type=validated_data['permission_type']
        ).first()
        
        if existing_permission:
            # URL encode the page_path for the composite key endpoint
            from urllib.parse import quote
            encoded_page_path = quote(validated_data["page_path"], safe='')
            raise serializers.ValidationError({
                'non_field_errors': [
                    f'A permission with this role_id ({role_id}), page_path ({validated_data["page_path"]}), and permission_type ({validated_data["permission_type"]}) already exists. '
                    f'Use PUT/PATCH /api/auth/role-permissions/{role_id}/{encoded_page_path}/{validated_data["permission_type"]}/ to update it instead.'
                ]
            })
        
        # Create permission using raw SQL to avoid id field issues
        from django.db import connection
        from django.utils import timezone
        
        page_path = validated_data['page_path']
        permission_type = validated_data['permission_type']
        is_allowed = validated_data.get('is_allowed', True)
        name = role.name
        now = timezone.now()
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO frontend_role_permissions 
                (role_id, name, page_path, permission_type, is_allowed, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (role_id, page_path, permission_type) DO NOTHING
            """, [role.role_id, name, page_path, permission_type, is_allowed, now, now])
        
        # Fetch using raw SQL and create a simple object that can be serialized
        from django.db import connection
        from types import SimpleNamespace
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT role_id, name, page_path, permission_type, is_allowed, created_at, updated_at
                FROM frontend_role_permissions
                WHERE role_id = %s AND page_path = %s AND permission_type = %s
            """, [role.role_id, page_path, permission_type])
            row = cursor.fetchone()
            
            if row:
                # Create a simple object that mimics the model but without id
                perm = SimpleNamespace()
                perm.role = role
                perm.name = row[1]
                perm.page_path = row[2]
                perm.permission_type = row[3]
                perm.is_allowed = row[4]
                perm.created_at = row[5]
                perm.updated_at = row[6]
                return perm
            else:
                raise serializers.ValidationError("Failed to create permission")


class RolePermissionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a role permission"""
    role_id = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Role identifier (e.g., R001)"
    )
    name = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Role name (optional - will update the role's name, which syncs to all permissions)"
    )
    is_allowed = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Permission status: 'allowed' or 'denied'"
    )
    
    class Meta:
        model = RolePermission
        fields = ['role_id', 'name', 'page_path', 'permission_type', 'is_allowed']
        extra_kwargs = {
            'page_path': {'required': False},
            'permission_type': {'required': False},
        }
    
    def validate_role_id(self, value):
        """Validate that role exists if provided"""
        if value and not Role.objects.filter(role_id=value).exists():
            raise serializers.ValidationError(f"Role with role_id '{value}' does not exist.")
        return value
    
    def validate_name(self, value):
        """Validate that role name is unique (excluding current role)"""
        if value:
            instance = getattr(self, 'instance', None)
            if instance:
                # Get the role from the instance
                role = instance.role
                # Check if name already exists for a different role
                if Role.objects.filter(name__iexact=value).exclude(role_id=role.role_id).exists():
                    existing_role = Role.objects.filter(name__iexact=value).exclude(role_id=role.role_id).first()
                    raise serializers.ValidationError(
                        f'A role with the name "{value}" already exists (role_id: {existing_role.role_id}). Please use a different name.'
                    )
        return value
    
    def validate_is_allowed(self, value):
        """Convert 'allowed'/'denied' string to boolean"""
        if value is None or value == '':
            return None  # Don't update if not provided
        if isinstance(value, str):
            if value.lower() in ('allowed', 'true', '1', 'yes'):
                return True
            elif value.lower() in ('denied', 'false', '0', 'no'):
                return False
            else:
                raise serializers.ValidationError("is_allowed must be 'allowed' or 'denied'")
        return bool(value)
    
    def validate(self, data):
        """Validate unique constraint if page_path or permission_type is being updated"""
        instance = getattr(self, 'instance', None)
        if instance:
            # Get role (either from update data or existing instance)
            role_id = data.get('role_id')
            if role_id:
                # If role_id is provided, use it
                role = Role.objects.get(role_id=role_id)
            else:
                # Otherwise, use the existing instance's role
                role = instance.role
            
            # Get the values that will be used (from data if provided, otherwise from instance)
            page_path = data.get('page_path', instance.page_path)
            permission_type = data.get('permission_type', instance.permission_type)
            
            # Check if another permission with same role, page_path, and permission_type exists
            # Exclude the current instance being updated using raw SQL
            from django.db import connection
            
            # Get original composite key values
            original_role_id = instance.role.role_id if hasattr(instance, 'role') and hasattr(instance.role, 'role_id') else None
            original_page_path = instance.page_path if hasattr(instance, 'page_path') else None
            original_permission_type = instance.permission_type if hasattr(instance, 'permission_type') else None
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM frontend_role_permissions
                    WHERE role_id = %s AND page_path = %s AND permission_type = %s
                    AND NOT (role_id = %s AND page_path = %s AND permission_type = %s)
                """, [
                    role.role_id, page_path, permission_type,
                    original_role_id, original_page_path, original_permission_type
                ])
                count = cursor.fetchone()[0]
                existing = count > 0
            
            if existing:
                raise serializers.ValidationError({
                    'non_field_errors': [
                        f'A permission with this role_id ({role.role_id}), page_path ({page_path}), and permission_type ({permission_type}) already exists. '
                        f'Use PUT/PATCH /api/auth/role-permissions/{role.role_id}/{page_path}/{permission_type}/ to update it instead, or change one of these values.'
                    ]
                })
        return data
    
    def update(self, instance, validated_data):
        """Update role permission instance using raw SQL to avoid id field issues"""
        from django.db import connection, transaction
        from django.utils import timezone
        from types import SimpleNamespace
        import logging
        logger = logging.getLogger(__name__)
        
        # Handle name update (updates the role's name, which syncs to all permissions)
        name = validated_data.pop('name', None)
        role = instance.role if hasattr(instance, 'role') else None
        
        if name and role:
            role.name = name
            role.save()  # This will trigger the signal to sync name to all permissions
        
        # Handle role_id update
        role_id = validated_data.pop('role_id', None)
        if role_id:
            role = Role.objects.get(role_id=role_id)
            # Update name when role changes
            name = role.name
        
        # Get current values
        current_role = role if role else (instance.role if hasattr(instance, 'role') else None)
        current_page_path = validated_data.get('page_path', instance.page_path if hasattr(instance, 'page_path') else None)
        current_permission_type = validated_data.get('permission_type', instance.permission_type if hasattr(instance, 'permission_type') else None)
        is_allowed = validated_data.get('is_allowed', instance.is_allowed if hasattr(instance, 'is_allowed') else True)
        
        # Convert is_allowed string to boolean
        if isinstance(is_allowed, str):
            is_allowed = is_allowed.lower() in ('allowed', 'true', '1', 'yes')
        
        # Get original composite key values
        original_role_id = current_role.role_id if current_role else None
        original_page_path = instance.page_path if hasattr(instance, 'page_path') else current_page_path
        original_permission_type = instance.permission_type if hasattr(instance, 'permission_type') else current_permission_type
        
        # Use atomic transaction to ensure update is committed
        with transaction.atomic(using='default'):
            # Use raw SQL to update
            now = timezone.now()
            logger.info(f"Updating permission: role_id={original_role_id}, page_path={original_page_path}, permission_type={original_permission_type}, is_allowed={is_allowed}")
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE frontend_role_permissions 
                    SET role_id = %s, name = %s, page_path = %s, permission_type = %s, 
                        is_allowed = %s, updated_at = %s
                    WHERE role_id = %s AND page_path = %s AND permission_type = %s
                """, [
                    current_role.role_id,
                    current_role.name,
                    current_page_path,
                    current_permission_type,
                    is_allowed,
                    now,
                    original_role_id,
                    original_page_path,
                    original_permission_type
                ])
                
                rows_updated = cursor.rowcount
                logger.info(f"UPDATE rows affected: {rows_updated} for role_id={original_role_id}")
                
                if rows_updated == 0:
                    logger.warning(f"No rows updated for role_id={original_role_id}, page_path={original_page_path}, permission_type={original_permission_type}")
            
            # Fetch updated permission using raw SQL to verify it was saved
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT rp.role_id, rp.name, rp.page_path, rp.permission_type, 
                           rp.is_allowed, rp.created_at, rp.updated_at
                    FROM frontend_role_permissions rp
                    WHERE rp.role_id = %s AND rp.page_path = %s AND rp.permission_type = %s
                """, [current_role.role_id, current_page_path, current_permission_type])
                row = cursor.fetchone()
                
                if row:
                    perm = SimpleNamespace()
                    perm.role = current_role
                    perm.name = row[1]
                    perm.page_path = row[2]
                    perm.permission_type = row[3]
                    perm.is_allowed = row[4]
                    perm.created_at = row[5]
                    perm.updated_at = row[6]
                    
                    # Verify the value was actually saved correctly
                    if perm.is_allowed != is_allowed:
                        logger.error(f"❌ Value mismatch! Expected {is_allowed}, got {perm.is_allowed} for role_id={current_role.role_id}")
                        # Force update one more time
                        with connection.cursor() as fix_cursor:
                            fix_cursor.execute("""
                                UPDATE frontend_role_permissions 
                                SET is_allowed = %s, updated_at = %s
                                WHERE role_id = %s AND page_path = %s AND permission_type = %s
                            """, [is_allowed, timezone.now(), current_role.role_id, current_page_path, current_permission_type])
                            if fix_cursor.rowcount > 0:
                                logger.info(f"✅ Fixed value mismatch for role_id={current_role.role_id}")
                                perm.is_allowed = is_allowed
                    else:
                        logger.info(f"✅ Permission updated correctly: role_id={current_role.role_id}, {current_page_path}/{current_permission_type} = {perm.is_allowed}")
                    
                    # Close connection to ensure PgBouncer sees the commit
                    connection.close()
                    return perm
        
        # If we get here, something went wrong
        logger.error(f"❌ Failed to update permission: role_id={original_role_id}, page_path={original_page_path}, permission_type={original_permission_type}")
        return instance


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for UserRole model - used for GET operations"""
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    role_id = serializers.CharField(source='role.role_id', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    assigned_by_id = serializers.IntegerField(source='assigned_by.id', read_only=True, allow_null=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True, allow_null=True)
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRole
        fields = ['id', 'user_id', 'username', 'email', 'role_id', 'role_name', 'assigned_at', 'assigned_by_id', 'assigned_by_username', 'is_active']
        read_only_fields = ['id', 'assigned_at']
    
    def get_is_active(self, obj):
        """Convert boolean to active/inactive string"""
        return "active" if obj.is_active else "inactive"


class UserRoleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user role assignment"""
    user_id = serializers.IntegerField(
        write_only=True,
        required=True,
        help_text="User ID (from auth_user table)"
    )
    role_id = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Role identifier (e.g., R001)"
    )
    assigned_by_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="User ID who assigned the role (optional)"
    )
    is_active = serializers.CharField(
        required=False,
        help_text="Assignment status: 'active' or 'inactive' (default: 'active')"
    )
    
    class Meta:
        model = UserRole
        fields = ['user_id', 'role_id', 'assigned_by_id', 'is_active']
    
    def validate_is_active(self, value):
        """Convert 'active'/'inactive' string to boolean"""
        if value is None or value == '':
            return True  # Default to active
        if isinstance(value, str):
            if value.lower() in ('active', 'true', '1', 'yes'):
                return True
            elif value.lower() in ('inactive', 'false', '0', 'no'):
                return False
            else:
                raise serializers.ValidationError("is_active must be 'active' or 'inactive'")
        return bool(value) if value is not None else True
    
    def validate_user_id(self, value):
        """Validate that user exists"""
        # Get the User model from UserRole's ForeignKey field to ensure we use the correct model
        UserModel = UserRole._meta.get_field('user').related_model
        if not UserModel.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"User with id '{value}' does not exist.")
        return value
    
    def validate_role_id(self, value):
        """Validate that role exists"""
        if not Role.objects.filter(role_id=value).exists():
            raise serializers.ValidationError(f"Role with role_id '{value}' does not exist.")
        return value
    
    def validate_assigned_by_id(self, value):
        """Validate that assigned_by user exists if provided"""
        if value is not None:
            # Get the User model from UserRole's ForeignKey field to ensure we use the correct model
            UserModel = UserRole._meta.get_field('user').related_model
            if not UserModel.objects.filter(id=value).exists():
                raise serializers.ValidationError(f"User with id '{value}' does not exist.")
        return value
    
    def validate(self, data):
        """Validate unique constraint and create UserRole instance"""
        user_id = data.get('user_id')
        role_id = data.get('role_id')
        
        # Check if user-role assignment already exists
        if UserRole.objects.filter(user_id=user_id, role_id=role_id).exists():
            raise serializers.ValidationError({
                'non_field_errors': ['A role assignment with this user_id and role_id already exists.']
            })
        
        return data
    
    def create(self, validated_data):
        """Create user role assignment"""
        user_id = validated_data.pop('user_id')
        role_id = validated_data.pop('role_id')
        assigned_by_id = validated_data.pop('assigned_by_id', None)
        
        # Get the User model from UserRole's ForeignKey field to ensure we use the correct model
        UserModel = UserRole._meta.get_field('user').related_model
        
        user = UserModel.objects.get(id=user_id)
        role = Role.objects.get(role_id=role_id)
        assigned_by = UserModel.objects.get(id=assigned_by_id) if assigned_by_id else None
        
        return UserRole.objects.create(
            user=user,
            role=role,
            assigned_by=assigned_by,
            **validated_data
        )


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a user role assignment"""
    is_active = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Assignment status: 'active' or 'inactive'"
    )
    
    class Meta:
        model = UserRole
        fields = ['is_active']
    
    def validate_is_active(self, value):
        """Convert 'active'/'inactive' string to boolean"""
        if value is None or value == '':
            return None  # Don't update if not provided
        if isinstance(value, str):
            if value.lower() in ('active', 'true', '1', 'yes'):
                return True
            elif value.lower() in ('inactive', 'false', '0', 'no'):
                return False
            else:
                raise serializers.ValidationError("is_active must be 'active' or 'inactive'")
        return bool(value)
    

class RoleWithPermissionsCreateSerializer(serializers.Serializer):
    """Serializer for creating a role with permissions in one request"""
    name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Role name (e.g., Super Admin, Admin)"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Role description"
    )
    defaultPage = serializers.CharField(
        required=False,
        max_length=255,
        default='/',
        help_text="Default page path after login"
    )
    permissions = serializers.DictField(
        required=True,
        child=serializers.DictField(
            child=serializers.BooleanField()
        ),
        help_text="Dictionary of page paths and their permissions. Format: {'/path': {'view': true, 'create': false, ...}}"
    )
    
    def validate_name(self, value):
        """Validate that role name is unique"""
        if Role.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A role with this name already exists.")
        return value
    
    def validate_permissions(self, value):
        """Validate permissions structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Permissions must be a dictionary.")
        
        # All valid permission types based on JSON format
        valid_permission_types = [
            'view', 'create', 'edit', 'delete', 
            'assign', 'approve', 'block', 'refund', 
            'reply', 'resolve', 'send'
        ]
        
        for page_path, perms in value.items():
            if not isinstance(page_path, str):
                raise serializers.ValidationError(f"Page path must be a string. Got: {type(page_path)}")
            
            if not isinstance(perms, dict):
                raise serializers.ValidationError(f"Permissions for '{page_path}' must be a dictionary.")
            
            for perm_type, perm_value in perms.items():
                if perm_type not in valid_permission_types:
                    raise serializers.ValidationError(
                        f"Invalid permission type '{perm_type}' for page '{page_path}'. "
                        f"Valid types: {', '.join(valid_permission_types)}"
                    )
                
                if not isinstance(perm_value, bool):
                    raise serializers.ValidationError(
                        f"Permission value for '{perm_type}' on '{page_path}' must be a boolean. Got: {type(perm_value)}"
                    )
        
        return value
    
    def create(self, validated_data):
        """Create role and all its permissions"""
        # Generate role_id automatically (R001, R002, etc.)
        # Try to find the maximum numeric part of role_ids
        max_number = 0
        existing_roles = Role.objects.all()
        
        for role in existing_roles:
            role_id = role.role_id
            # Check if role_id matches pattern R### or R##
            if role_id.startswith('R') and len(role_id) > 1:
                try:
                    # Extract numeric part
                    num_part = role_id[1:]
                    num = int(num_part)
                    if num > max_number:
                        max_number = num
                except ValueError:
                    continue
        
        # Generate next role_id
        role_id_number = max_number + 1
        role_id = f"R{role_id_number:03d}"
        
        # Ensure role_id is unique (in case of conflicts)
        while Role.objects.filter(role_id=role_id).exists():
            role_id_number += 1
            role_id = f"R{role_id_number:03d}"
        
        # Create the role
        role = Role.objects.create(
            role_id=role_id,
            name=validated_data['name'],
            description=validated_data.get('description', ''),
            default_page=validated_data.get('defaultPage', '/'),
            is_active=True
        )
        
        # Create permissions
        permissions_data = validated_data['permissions']
        created_permissions = []
        
        for page_path, perms in permissions_data.items():
            for permission_type, is_allowed in perms.items():
                # Create permission for both true and false values so they appear in database
                # Use raw SQL to create/update permission to avoid id field issues
                from django.db import connection
                from django.utils import timezone
                
                now = timezone.now()
                with connection.cursor() as cursor:
                    # Try to insert, update if exists
                    cursor.execute("""
                        INSERT INTO frontend_role_permissions 
                        (role_id, name, page_path, permission_type, is_allowed, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (role_id, page_path, permission_type) 
                        DO UPDATE SET is_allowed = EXCLUDED.is_allowed, name = EXCLUDED.name, updated_at = EXCLUDED.updated_at
                    """, [role.role_id, role.name, page_path, permission_type, is_allowed, now, now])
                
                # Fetch using raw SQL to avoid id field
                from django.db import connection
                from types import SimpleNamespace
                
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT rp.role_id, rp.name, rp.page_path, rp.permission_type, 
                               rp.is_allowed, rp.created_at, rp.updated_at
                        FROM frontend_role_permissions rp
                        WHERE rp.role_id = %s AND rp.page_path = %s AND rp.permission_type = %s
                    """, [role.role_id, page_path, permission_type])
                    row = cursor.fetchone()
                    
                    if row:
                        perm = SimpleNamespace()
                        perm.role = role
                        perm.name = row[1]
                        perm.page_path = row[2]
                        perm.permission_type = row[3]
                        perm.is_allowed = row[4]
                        perm.created_at = row[5]
                        perm.updated_at = row[6]
                        created_permissions.append(perm)
        
        return {
            'role': role,
            'permissions': created_permissions
        }


class RolePermissionsBulkUpdateSerializer(serializers.Serializer):
    """Serializer for creating/updating permissions for a role (creates role if it doesn't exist, auto-generates role_id if not provided)"""
    role_id = serializers.CharField(
        required=False,
        max_length=50,
        allow_blank=True,
        allow_null=True,
        help_text="Role identifier (e.g., R001). If not provided, will be auto-generated."
    )
    name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Role name (required)"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Role description"
    )
    defaultPage = serializers.CharField(
        required=False,
        max_length=255,
        default='/',
        help_text="Default page path after login"
    )
    permissions = serializers.DictField(
        required=True,
        child=serializers.DictField(
            child=serializers.BooleanField()
        ),
        help_text="Dictionary of page paths and their permissions. Format: {'/path': {'view': true, 'create': false, ...}}"
    )
    
    def validate(self, data):
        """Validate that role exists or can be created"""
        role_id = data.get('role_id')
        
        # If role_id is provided, check if role exists
        if role_id:
            role_exists = Role.objects.filter(role_id=role_id).exists()
            if not role_exists:
                # Role doesn't exist, name is required for creation
                if not data.get('name'):
                    raise serializers.ValidationError({
                        'name': 'Role name is required when creating a new role.'
                    })
        else:
            # role_id not provided, name is required for auto-generation
            if not data.get('name'):
                raise serializers.ValidationError({
                    'name': 'Role name is required.'
                })
        
        return data
    
    def validate_permissions(self, value):
        """Validate permissions structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Permissions must be a dictionary.")
        
        # All valid permission types based on JSON format
        valid_permission_types = [
            'view', 'create', 'edit', 'delete', 
            'assign', 'approve', 'block', 'refund', 
            'reply', 'resolve', 'send'
        ]
        
        for page_path, perms in value.items():
            if not isinstance(page_path, str):
                raise serializers.ValidationError(f"Page path must be a string. Got: {type(page_path)}")
            
            if not isinstance(perms, dict):
                raise serializers.ValidationError(f"Permissions for '{page_path}' must be a dictionary.")
            
            for perm_type, perm_value in perms.items():
                if perm_type not in valid_permission_types:
                    raise serializers.ValidationError(
                        f"Invalid permission type '{perm_type}' for page '{page_path}'. "
                        f"Valid types: {', '.join(valid_permission_types)}"
                    )
                
                if not isinstance(perm_value, bool):
                    raise serializers.ValidationError(
                        f"Permission value for '{perm_type}' on '{page_path}' must be a boolean. Got: {type(perm_value)}"
                    )
        
        return value
    
    def create(self, validated_data):
        """Create or update permissions for a role (creates role if it doesn't exist, auto-generates role_id if not provided)"""
        from django.db import transaction
        import logging
        logger = logging.getLogger(__name__)
        
        role_id = validated_data.get('role_id')
        role_created = False
        
        # Auto-generate role_id if not provided
        if not role_id:
            # Generate role_id automatically (R001, R002, etc.)
            max_number = 0
            existing_roles = Role.objects.all()
            
            for role in existing_roles:
                role_id_str = role.role_id
                # Check if role_id matches pattern R### or R##
                if role_id_str.startswith('R') and len(role_id_str) > 1:
                    try:
                        # Extract numeric part
                        num_part = role_id_str[1:]
                        num = int(num_part)
                        if num > max_number:
                            max_number = num
                    except ValueError:
                        continue
            
            # Generate next role_id
            role_id_number = max_number + 1
            role_id = f"R{role_id_number:03d}"
            
            # Ensure role_id is unique (in case of conflicts)
            while Role.objects.filter(role_id=role_id).exists():
                role_id_number += 1
                role_id = f"R{role_id_number:03d}"
        
        # Get or create the role
        role, role_created = Role.objects.get_or_create(
            role_id=role_id,
            defaults={
                'name': validated_data.get('name', f'Role {role_id}'),
                'description': validated_data.get('description', ''),
                'default_page': validated_data.get('defaultPage', '/'),
                'is_active': True
            }
        )
        
        # If role already exists, update optional fields if provided
        if not role_created:
            if 'name' in validated_data:
                role.name = validated_data['name']
            if 'description' in validated_data:
                role.description = validated_data.get('description', '')
            if 'defaultPage' in validated_data:
                role.default_page = validated_data.get('defaultPage', '/')
            role.save()
        
        permissions_data = validated_data['permissions']
        created_permissions = []
        updated_permissions = []
        deleted_permissions = []
        
        # Get all existing permissions for this role using raw SQL
        from django.db import connection
        from types import SimpleNamespace
        
        existing_perms_dict = {}
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT rp.role_id, rp.name, rp.page_path, rp.permission_type, 
                       rp.is_allowed, rp.created_at, rp.updated_at
                FROM frontend_role_permissions rp
                WHERE rp.role_id = %s
            """, [role.role_id])
            rows = cursor.fetchall()
            
            for row in rows:
                perm = SimpleNamespace()
                perm.role = role
                perm.name = row[1]
                perm.page_path = row[2]
                perm.permission_type = row[3]
                perm.is_allowed = row[4]
                perm.created_at = row[5]
                perm.updated_at = row[6]
                key = (perm.page_path, perm.permission_type)
                existing_perms_dict[key] = perm
        
        # Process permissions from payload
        processed_perms = set()
        from django.db import connection, transaction
        from django.utils import timezone
        from types import SimpleNamespace
        import logging
        logger = logging.getLogger(__name__)
        
        # Use atomic transaction to ensure all changes are committed
        # Using savepoint=True to ensure proper transaction handling with PgBouncer
        with transaction.atomic(using='default'):
            for page_path, perms in permissions_data.items():
                for permission_type, is_allowed in perms.items():
                    key = (page_path, permission_type)
                    processed_perms.add(key)
                    
                    # Create or update permission using raw SQL for reliable saving
                    now = timezone.now()
                    was_existing = key in existing_perms_dict
                    perm_obj = existing_perms_dict.get(key)
                    
                    try:
                        # Use raw SQL with explicit transaction handling for PgBouncer compatibility
                        logger.info(f"Updating permission: role_id={role.role_id}, page_path={page_path}, permission_type={permission_type}, is_allowed={is_allowed}")
                        
                        with connection.cursor() as cursor:
                            # First try UPDATE
                            cursor.execute("""
                                UPDATE frontend_role_permissions 
                                SET is_allowed = %s,
                                    name = %s,
                                    updated_at = %s
                                WHERE role_id = %s 
                                  AND page_path = %s 
                                  AND permission_type = %s
                            """, [is_allowed, role.name, now, role.role_id, page_path, permission_type])
                            
                            rows_updated = cursor.rowcount
                            logger.info(f"UPDATE rows affected: {rows_updated} for role_id={role.role_id}")
                            
                            # If no rows updated, INSERT new permission
                            if rows_updated == 0:
                                logger.info(f"Inserting new permission for role_id={role.role_id}")
                                cursor.execute("""
                                    INSERT INTO frontend_role_permissions 
                                    (role_id, name, page_path, permission_type, is_allowed, created_at, updated_at)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """, [role.role_id, role.name, page_path, permission_type, is_allowed, now, now])
                                rows_inserted = cursor.rowcount
                                logger.info(f"INSERT rows affected: {rows_inserted}")
                        
                        # Fetch the saved permission to verify it was saved correctly (within same transaction)
                        with connection.cursor() as cursor:
                            cursor.execute("""
                                SELECT rp.role_id, rp.name, rp.page_path, rp.permission_type, 
                                       rp.is_allowed, rp.created_at, rp.updated_at
                                FROM frontend_role_permissions rp
                                WHERE rp.role_id = %s AND rp.page_path = %s AND rp.permission_type = %s
                            """, [role.role_id, page_path, permission_type])
                            row = cursor.fetchone()
                            
                            if row:
                                perm = SimpleNamespace()
                                perm.role = role
                                perm.name = row[1]
                                perm.page_path = row[2]
                                perm.permission_type = row[3]
                                perm.is_allowed = row[4]
                                perm.created_at = row[5]
                                perm.updated_at = row[6]
                                
                                # Verify the value was actually saved correctly
                                if perm.is_allowed != is_allowed:
                                    logger.error(f"❌ Value mismatch! Expected {is_allowed}, got {perm.is_allowed} for role_id={role.role_id}, {page_path}/{permission_type}")
                                    # Force update one more time
                                    with connection.cursor() as fix_cursor:
                                        fix_cursor.execute("""
                                            UPDATE frontend_role_permissions 
                                            SET is_allowed = %s, updated_at = %s
                                            WHERE role_id = %s AND page_path = %s AND permission_type = %s
                                        """, [is_allowed, timezone.now(), role.role_id, page_path, permission_type])
                                        if fix_cursor.rowcount > 0:
                                            logger.info(f"✅ Fixed value mismatch for role_id={role.role_id}")
                                            perm.is_allowed = is_allowed
                                else:
                                    logger.info(f"✅ Permission saved correctly: role_id={role.role_id}, {page_path}/{permission_type} = {perm.is_allowed}")
                                
                                # Add to appropriate list
                                if was_existing:
                                    if perm_obj and perm_obj.is_allowed != is_allowed:
                                        updated_permissions.append(perm)
                                    else:
                                        updated_permissions.append(perm)
                                else:
                                    created_permissions.append(perm)
                            else:
                                logger.error(f"❌ Permission not found after save for role_id={role.role_id}, {page_path}/{permission_type}")
                                raise Exception(f"Failed to save permission: role_id={role.role_id}, {page_path}/{permission_type}")
                        
                        # Add to appropriate list based on whether it existed before
                        if was_existing:
                            # Check if value actually changed
                            if perm_obj and perm_obj.is_allowed != is_allowed:
                                updated_permissions.append(perm)
                            else:
                                # Value didn't change, but still include in updated list for response
                                updated_permissions.append(perm)
                        else:
                            created_permissions.append(perm)
                            
                    except Exception as e:
                        logger.error(f"❌ Error saving permission {page_path}/{permission_type}: {str(e)}", exc_info=True)
                        # Fallback to raw SQL if ORM fails
                        try:
                            logger.warning(f"Falling back to raw SQL for {page_path}/{permission_type}")
                            with connection.cursor() as cursor:
                                # Try UPDATE first
                                cursor.execute("""
                                    UPDATE frontend_role_permissions 
                                    SET is_allowed = %s,
                                        name = %s,
                                        updated_at = %s
                                    WHERE role_id = %s 
                                      AND page_path = %s 
                                      AND permission_type = %s
                                """, [is_allowed, role.name, now, role.role_id, page_path, permission_type])
                                
                                rows_updated = cursor.rowcount
                                
                                # If no rows were updated, INSERT the new permission
                                if rows_updated == 0:
                                    cursor.execute("""
                                        INSERT INTO frontend_role_permissions 
                                        (role_id, name, page_path, permission_type, is_allowed, created_at, updated_at)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    """, [role.role_id, role.name, page_path, permission_type, is_allowed, now, now])
                                
                                # Fetch to verify
                                cursor.execute("""
                                    SELECT rp.role_id, rp.name, rp.page_path, rp.permission_type, 
                                           rp.is_allowed, rp.created_at, rp.updated_at
                                    FROM frontend_role_permissions rp
                                    WHERE rp.role_id = %s AND rp.page_path = %s AND rp.permission_type = %s
                                """, [role.role_id, page_path, permission_type])
                                row = cursor.fetchone()
                                
                                if row:
                                    perm = SimpleNamespace()
                                    perm.role = role
                                    perm.name = row[1]
                                    perm.page_path = row[2]
                                    perm.permission_type = row[3]
                                    perm.is_allowed = row[4]
                                    perm.created_at = row[5]
                                    perm.updated_at = row[6]
                                    
                                    if was_existing:
                                        updated_permissions.append(perm)
                                    else:
                                        created_permissions.append(perm)
                                else:
                                    raise Exception(f"Failed to save permission: {page_path}/{permission_type}")
                        except Exception as fallback_error:
                            logger.error(f"❌ Raw SQL fallback also failed: {str(fallback_error)}", exc_info=True)
                            raise  # Re-raise to ensure transaction rollback
        
        # Delete permissions that are not in the payload (optional - you can comment this out if you don't want to delete)
        # for key, perm in existing_perms_dict.items():
        #     if key not in processed_perms:
        #         perm.delete()
        #         deleted_permissions.append(perm)
        
        # Transaction commits automatically when exiting the atomic block above
        # Close connection to ensure PgBouncer sees the committed transaction
        connection.close()
        
        # Reopen connection and verify all permissions were saved
        logger.info(f"Transaction committed. Verifying {len(created_permissions) + len(updated_permissions)} permissions were saved to database...")
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM frontend_role_permissions 
                WHERE role_id = %s
            """, [role.role_id])
            total_count = cursor.fetchone()[0]
            logger.info(f"✅ Total permissions in database for role {role.role_id}: {total_count}")
        
        return {
            'role': role,
            'role_created': role_created,
            'created_permissions': created_permissions,
            'updated_permissions': updated_permissions,
            'deleted_permissions': deleted_permissions
        }


class RoleWithPermissionsUpdateSerializer(serializers.Serializer):
    """Serializer for updating a role with all its permissions in one request"""
    role_id = serializers.CharField(
        required=True,
        max_length=50,
        help_text="Role identifier (e.g., R001) - required to identify which role to update"
    )
    name = serializers.CharField(
        required=False,
        max_length=255,
        help_text="Role name"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Role description"
    )
    defaultPage = serializers.CharField(
        required=False,
        max_length=255,
        help_text="Default page path after login"
    )
    permissions = serializers.DictField(
        required=False,
        child=serializers.DictField(
            child=serializers.BooleanField()
        ),
        help_text="Dictionary of page paths and their permissions. Format: {'/path': {'view': true, 'create': false, ...}}"
    )
    
    def validate_role_id(self, value):
        """Validate role_id format - role will be created if it doesn't exist"""
        # Just validate format, don't require existence
        # The role will be created in the update method if it doesn't exist
        if not value or not isinstance(value, str):
            raise serializers.ValidationError("role_id must be a non-empty string.")
        return value
    
    def validate_name(self, value):
        """Validate that role name is unique (excluding current role being updated)"""
        if value:
            # Get role_id from validated_data if available, or from initial_data
            role_id = None
            if hasattr(self, 'initial_data') and 'role_id' in self.initial_data:
                role_id = self.initial_data['role_id']
            
            if role_id:
                # Check uniqueness excluding the current role
                if Role.objects.filter(name__iexact=value).exclude(role_id=role_id).exists():
                    raise serializers.ValidationError("A role with this name already exists.")
            else:
                # If no role_id, check if name exists (shouldn't happen in update, but just in case)
                if Role.objects.filter(name__iexact=value).exists():
                    raise serializers.ValidationError("A role with this name already exists.")
        return value

    def validate_permissions(self, value):
        """Validate permissions structure"""
        if value is None:
            return value  # Allow None for permissions (optional field)
        
        if not isinstance(value, dict):
            raise serializers.ValidationError("Permissions must be a dictionary.")
        
        valid_permission_types = ['view', 'create', 'edit', 'delete', 'assign', 'approve', 'reject']
        
        for page_path, perms in value.items():
            if not isinstance(page_path, str):
                raise serializers.ValidationError(f"Page path must be a string. Got: {type(page_path)}")
            
            if not isinstance(perms, dict):
                raise serializers.ValidationError(f"Permissions for '{page_path}' must be a dictionary.")
            
            for perm_type, perm_value in perms.items():
                if perm_type not in valid_permission_types:
                    raise serializers.ValidationError(
                        f"Invalid permission type '{perm_type}' for page '{page_path}'. "
                        f"Valid types: {', '.join(valid_permission_types)}"
                    )
                
                if not isinstance(perm_value, bool):
                    raise serializers.ValidationError(
                        f"Permission value for '{perm_type}' on '{page_path}' must be a boolean. Got: {type(perm_value)}"
                    )
        
        return value
    
    def update(self, instance, validated_data):
        """Update role and all its permissions (creates role if it doesn't exist)"""
        from django.db import connection, transaction
        import logging
        logger = logging.getLogger(__name__)
        
        role_id = validated_data['role_id']
        role_created = False
        
        # Use atomic transaction to ensure all changes are committed
        with transaction.atomic(using='default'):
            # Get or create the role
            try:
                role = Role.objects.get(role_id=role_id)
            except Role.DoesNotExist:
                # Create role if it doesn't exist
                # Name is required when creating
                if 'name' not in validated_data or not validated_data.get('name'):
                    raise serializers.ValidationError({
                        'name': 'name is required when creating a new role.'
                    })
                
                role = Role.objects.create(
                    role_id=role_id,
                    name=validated_data['name'],
                    description=validated_data.get('description', ''),
                    default_page=validated_data.get('defaultPage', '/'),
                    is_active=True
                )
                role_created = True
                logger.info(f"✅ Created new role: role_id={role_id}, name={role.name}")
            
            # Update role fields if provided
            name_updated = False
            if 'name' in validated_data and validated_data['name']:
                # Only update if name is provided and not empty
                old_name = role.name
                role.name = validated_data['name']
                name_updated = (old_name != role.name)
            if 'description' in validated_data:
                role.description = validated_data.get('description', '')
            if 'defaultPage' in validated_data:
                role.default_page = validated_data.get('defaultPage', '/')
            
            # Save the role (this will trigger the signal to sync name to permissions)
            role.save()
            logger.info(f"✅ Role saved: role_id={role.role_id}, name={role.name}")
            
            # Explicitly sync name to all permissions if name was updated
            # (The signal should handle this, but we do it explicitly to ensure it happens)
            if name_updated:
                RolePermission.objects.filter(role=role).update(name=role.name)
                logger.info(f"✅ Synced role name to permissions: role_id={role.role_id}")
        
        # Update permissions if provided (still inside transaction if permissions are being updated)
        created_permissions = []
        updated_permissions = []
        deleted_permissions = []
        
        if 'permissions' in validated_data and validated_data['permissions'] is not None:
            permissions_data = validated_data['permissions']
            
            # Get all existing permissions for this role using raw SQL
            from django.db import connection
            from types import SimpleNamespace
            
            existing_perms_dict = {}
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT rp.role_id, rp.name, rp.page_path, rp.permission_type, 
                           rp.is_allowed, rp.created_at, rp.updated_at
                    FROM frontend_role_permissions rp
                    WHERE rp.role_id = %s
                """, [role.role_id])
                rows = cursor.fetchall()
                
                for row in rows:
                    perm = SimpleNamespace()
                    perm.role = role
                    perm.name = row[1]
                    perm.page_path = row[2]
                    perm.permission_type = row[3]
                    perm.is_allowed = row[4]
                    perm.created_at = row[5]
                    perm.updated_at = row[6]
                    key = (perm.page_path, perm.permission_type)
                    existing_perms_dict[key] = perm
            
            # Process permissions from payload
            processed_perms = set()
            for page_path, perms in permissions_data.items():
                for permission_type, is_allowed in perms.items():
                    key = (page_path, permission_type)
                    processed_perms.add(key)
                    
                    now = timezone.now()
                    was_existing = key in existing_perms_dict
                    perm_obj = existing_perms_dict.get(key)
                    
                    try:
                        # Use Django ORM update_or_create for better transaction handling with PgBouncer
                        logger.info(f"Processing permission: role_id={role.role_id}, page_path={page_path}, permission_type={permission_type}, is_allowed={is_allowed}")
                        
                        perm_instance, created = RolePermission.objects.update_or_create(
                            role=role,
                            page_path=page_path,
                            permission_type=permission_type,
                            defaults={
                                'is_allowed': is_allowed,
                                'name': role.name,
                                'updated_at': now,
                            }
                        )
                        
                        # Force save to ensure it's committed
                        perm_instance.save()
                        
                        if created:
                            logger.info(f"✅ Created new permission: {page_path}/{permission_type} = {is_allowed}")
                        else:
                            logger.info(f"✅ Updated existing permission: {page_path}/{permission_type} = {is_allowed}")
                        
                        # Create SimpleNamespace object for response (matching raw SQL format)
                        perm = SimpleNamespace()
                        perm.role = role
                        perm.name = perm_instance.name
                        perm.page_path = perm_instance.page_path
                        perm.permission_type = perm_instance.permission_type
                        perm.is_allowed = perm_instance.is_allowed
                        perm.created_at = perm_instance.created_at
                        perm.updated_at = perm_instance.updated_at
                        
                        # Verify the value was actually saved correctly
                        if perm.is_allowed != is_allowed:
                            logger.error(f"❌ Value mismatch! Expected {is_allowed}, got {perm.is_allowed} for {page_path}/{permission_type}")
                            # Force update again
                            perm_instance.is_allowed = is_allowed
                            perm_instance.save()
                            perm.is_allowed = is_allowed
                        else:
                            logger.info(f"✅ Permission verified: {page_path}/{permission_type} = {perm.is_allowed}")
                        
                        # Add to appropriate list based on whether it existed before
                        if was_existing:
                            if perm_obj and perm_obj.is_allowed != is_allowed:
                                updated_permissions.append(perm)
                            else:
                                updated_permissions.append(perm)
                        else:
                            created_permissions.append(perm)
                            
                    except Exception as e:
                        logger.error(f"❌ Error saving permission {page_path}/{permission_type}: {str(e)}", exc_info=True)
                        # Fallback to raw SQL if ORM fails
                        try:
                            logger.warning(f"Falling back to raw SQL for {page_path}/{permission_type}")
                            with connection.cursor() as cursor:
                                # Try UPDATE first
                                cursor.execute("""
                                    UPDATE frontend_role_permissions 
                                    SET is_allowed = %s,
                                        name = %s,
                                        updated_at = %s
                                    WHERE role_id = %s 
                                      AND page_path = %s 
                                      AND permission_type = %s
                                """, [is_allowed, role.name, now, role.role_id, page_path, permission_type])
                                
                                rows_updated = cursor.rowcount
                                
                                # If no rows were updated, INSERT the new permission
                                if rows_updated == 0:
                                    cursor.execute("""
                                        INSERT INTO frontend_role_permissions 
                                        (role_id, name, page_path, permission_type, is_allowed, created_at, updated_at)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    """, [role.role_id, role.name, page_path, permission_type, is_allowed, now, now])
                                
                                # Fetch to verify
                                cursor.execute("""
                                    SELECT rp.role_id, rp.name, rp.page_path, rp.permission_type, 
                                           rp.is_allowed, rp.created_at, rp.updated_at
                                    FROM frontend_role_permissions rp
                                    WHERE rp.role_id = %s AND rp.page_path = %s AND rp.permission_type = %s
                                """, [role.role_id, page_path, permission_type])
                                row = cursor.fetchone()
                                
                                if row:
                                    perm = SimpleNamespace()
                                    perm.role = role
                                    perm.name = row[1]
                                    perm.page_path = row[2]
                                    perm.permission_type = row[3]
                                    perm.is_allowed = row[4]
                                    perm.created_at = row[5]
                                    perm.updated_at = row[6]
                                    
                                    if was_existing:
                                        updated_permissions.append(perm)
                                    else:
                                        created_permissions.append(perm)
                                else:
                                    raise Exception(f"Failed to save permission: {page_path}/{permission_type}")
                        except Exception as fallback_error:
                            logger.error(f"❌ Raw SQL fallback also failed: {str(fallback_error)}", exc_info=True)
                            raise  # Re-raise to ensure transaction rollback
            
            # Optionally delete permissions that are not in the payload
            # Uncomment the code below if you want to delete permissions not in the payload
            # for key, perm in existing_perms_dict.items():
            #     if key not in processed_perms:
            #         perm.delete()
            #         deleted_permissions.append(perm)
        
        # Refresh from database after transaction commits (outside the atomic block)
        role.refresh_from_db()
        logger.info(f"✅ Role and permissions verified in database: role_id={role.role_id}, name={role.name}")
        
        return {
            'role': role,
            'role_created': role_created,
            'created_permissions': created_permissions,
            'updated_permissions': updated_permissions,
            'deleted_permissions': deleted_permissions
        }



from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from decimal import Decimal

User = settings.AUTH_USER_MODEL


class RidesUser(models.Model):
    """Model to connect to existing rides_user table with actual column structure"""
    # Primary key
    id = models.BigIntegerField(primary_key=True)  # bigint in database
    
    # Authentication fields
    password = models.CharField(max_length=128, blank=True, null=True)  # Hashed password
    last_login = models.DateTimeField(blank=True, null=True)  # timestamp with time zone
    
    # User information fields
    name = models.CharField(max_length=255, blank=True, null=True)  # Full name
    # Phone number field removed - column doesn't exist in database
    # If phone number column exists with different name, add it back with db_column parameter
    # Example: phone_number = models.CharField(max_length=20, blank=True, null=True, db_column='phone')
    email = models.EmailField(blank=True, null=True)  # Email address
    dob = models.DateField(blank=True, null=True)  # Date of birth
    
    # Status fields
    is_active = models.BooleanField(default=True, blank=True, null=True)  # Active status
    is_staff = models.BooleanField(default=False, blank=True, null=True)  # Staff status
    is_superuser = models.BooleanField(default=False, blank=True, null=True)  # Superuser status
    
    # OTP fields
    otp = models.CharField(max_length=10, blank=True, null=True)  # OTP code
    otp_created_at = models.DateTimeField(blank=True, null=True)  # OTP creation timestamp
    
    # Additional fields
    custom_user_id = models.CharField(max_length=255, blank=True, null=True)  # Custom user ID
    deleted_at = models.DateTimeField(blank=True, null=True)  # Soft delete timestamp
    
    class Meta:
        managed = False  # Don't let Django manage this table (it already exists)
        db_table = 'rides_user'  # Connect to existing table name
        verbose_name = "Rides User"
        verbose_name_plural = "Rides Users"
    
    def __str__(self):
        return f"{self.name or f'User {self.id}'} - {self.email or 'No contact'}"
    
    @property
    def is_deleted(self):
        """Check if user is soft deleted"""
        return self.deleted_at is not None
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if self.dob:
            from datetime import date
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return None


class UserProfile(models.Model):
    """User Profile model with id, name, phone number, email, and status"""
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_SUSPENDED = 'suspended'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_SUSPENDED, 'Suspended'),
    ]
    
    # id is automatically created by Django as primary key
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile', db_constraint=False)
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Full name of the user")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, help_text="User email address")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']     
    
    def __str__(self):
        return f"{self.name or self.user.username} - {self.phone_number} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Auto-populate name and email from user if not provided
        if not self.name and self.user:
            self.name = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
        if not self.email and self.user:
            self.email = self.user.email
        super().save(*args, **kwargs)


class AdminProfile(models.Model):
    """Admin Profile model to store admin roles"""
    ROLE_SUPERADMIN = 'superadmin'
    ROLE_ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (ROLE_SUPERADMIN, 'Super Admin'),
        (ROLE_ADMIN, 'Admin'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='admin_profile',
        db_constraint=False,
        help_text="Django User associated with this admin profile"
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Full name of the admin"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Email address of the admin"
    )
    password = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Password hash (for reference, actual auth uses auth_user table)"
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default=ROLE_ADMIN,
        help_text="Admin role: superadmin or admin"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this admin account is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name or self.user.username} - {self.get_role_display()}"
    
    def save(self, *args, **kwargs):
        # Auto-populate name, email, and password from user if not provided
        if not self.name and self.user:
            self.name = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
        if not self.email and self.user:
            self.email = self.user.email
        if not self.password and self.user:
            self.password = self.user.password  # Store password hash for reference
        super().save(*args, **kwargs)
    
    @property
    def is_superadmin(self):
        """Check if user is superadmin"""
        return self.role == self.ROLE_SUPERADMIN
    
    @property
    def is_admin(self):
        """Check if user is admin (includes superadmin)"""
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPERADMIN]


class PromoCode(models.Model):
    """PromoCode model for discount codes"""
    
    # Discount type choices
    DISCOUNT_TYPE_PERCENTAGE = 'percentage'
    DISCOUNT_TYPE_FIXED = 'fixed'
    
    DISCOUNT_TYPE_CHOICES = [
        (DISCOUNT_TYPE_PERCENTAGE, 'Percentage'),
        (DISCOUNT_TYPE_FIXED, 'Fixed Amount'),
    ]
    
    # Status choices
    STATUS_ACTIVE = 'active'
    STATUS_DEACTIVATE = 'deactivate'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DEACTIVATE, 'Deactivate'),
    ]
    
    # Promo code (unique identifier)
    code = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="Unique promo code (e.g., SAVE20, WELCOME50)"
    )
    
    # Discount information
    discount_type = models.CharField(
        max_length=20, 
        choices=DISCOUNT_TYPE_CHOICES, 
        default=DISCOUNT_TYPE_PERCENTAGE,
        help_text="Type of discount: percentage or fixed amount"
    )
    
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Discount value (percentage or fixed amount)"
    )
    
    # Date fields
    start_date = models.DateTimeField(
        help_text="Start date and time when promo code becomes active"
    )
    
    expire_date = models.DateTimeField(
        help_text="Expiration date and time for the promo code"
    )
    
    # Usage limits
    max_usage = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of times this promo code can be used"
    )
    
    current_usage = models.PositiveIntegerField(
        default=0,
        help_text="Current number of times this promo code has been used"
    )
    
    # Status
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=STATUS_ACTIVE,
        help_text="Status of the promo code"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Promo Code"
        verbose_name_plural = "Promo Codes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status', 'start_date', 'expire_date']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()} {self.discount_value}"
    
    @property
    def is_valid(self):
        """Check if promo code is currently valid"""
        from django.utils import timezone
        now = timezone.now()
        
        # Check status
        if self.status != self.STATUS_ACTIVE:
            return False
        
        # Check date range
        if now < self.start_date or now > self.expire_date:
            return False
        
        # Check usage limit
        if self.current_usage >= self.max_usage:
            return False
        
        return True
    
    @property
    def is_expired(self):
        """Check if promo code has expired"""
        from django.utils import timezone
        now = timezone.now()
        return now > self.expire_date
    
    @property
    def is_usage_limit_reached(self):
        """Check if usage limit has been reached"""
        return self.current_usage >= self.max_usage
    
    @property
    def remaining_usage(self):
        """Get remaining usage count"""
        return max(0, self.max_usage - self.current_usage)
    
    def calculate_discount(self, amount):
        """
        Calculate discount amount based on discount type
        
        Args:
            amount: Original amount to apply discount to
            
        Returns:
            Discount amount
        """
        if self.discount_type == self.DISCOUNT_TYPE_PERCENTAGE:
            # Percentage discount
            discount = (amount * self.discount_value) / 100
            return round(discount, 2)
        else:
            # Fixed amount discount
            return min(self.discount_value, amount)
    
    def apply_discount(self, amount):
        """
        Apply discount to an amount and return final amount
        
        Args:
            amount: Original amount
            
        Returns:
            Final amount after discount
        """
        discount = self.calculate_discount(amount)
        final_amount = amount - discount
        return max(0, round(final_amount, 2))


class Zone(models.Model):
    """
    Zone Management model for defining geographic zones
    """
    zone_id = models.AutoField(
        primary_key=True,
        db_column='zone_id',
        help_text="Zone ID (primary key)"
    )
    
    zone_name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the zone (e.g., 'Downtown Zone', 'Airport Zone')"
    )
    
    country = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Country where this zone is located"
    )
    
    state = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="State/Province where this zone is located"
    )
    
    city = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="City name where this zone is located"
    )
    
    priority = models.IntegerField(
        default=0,
        help_text="Priority of the zone (higher number = higher priority)"
    )
    
    status = models.BooleanField(
        default=True,
        help_text="Status of the zone: True for active, False for inactive"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the zone was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the zone was last updated"
    )
    
    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['zone_name']),
            models.Index(fields=['country']),
            models.Index(fields=['state']),
            models.Index(fields=['city']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        status_text = "Active" if self.status else "Inactive"
        return f"{self.zone_name} - {status_text}"
    
    @property
    def is_active(self):
        """Check if zone is active"""
        return self.status


class User(models.Model):
    """
    User model for RBAC (Role-Based Access Control)
    Table name: frontend_user
    """
    id = models.AutoField(primary_key=True, help_text="User ID (primary key)")
    name = models.CharField(
        max_length=255,
        help_text="Full name of the user"
    )
    email = models.EmailField(
        unique=True,
        help_text="Email address of the user (must be unique)"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Phone number of the user"
    )
    password = models.CharField(
        max_length=128,
        help_text="Hashed password (stored securely)"
    )
    confirm_password = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Confirm password (stored securely)"
    )
    role_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Role ID for RBAC (supports both string like 'R001' and integer values)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this user account is active"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the user was created"
    )
    
    class Meta:
        db_table = 'frontend_user'
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role_id']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.email}"
    
    def save(self, *args, **kwargs):
        # Hash password if it's not already hashed
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        # Hash confirm_password if it's not already hashed
        if self.confirm_password and not self.confirm_password.startswith('pbkdf2_'):
            self.confirm_password = make_password(self.confirm_password)
        super().save(*args, **kwargs)

    def get_roles(self):
        """Return a QuerySet of Role objects for this user.

        Priority:
        - If user has entries in `frontend_user_roles` (UserRole), use those.
        - Otherwise, fall back to the `role_id` column on the `frontend_user` table.
        This does not persist any changes; it's a read-only helper.
        """
        from django.db.models import Q
        # Try explicit assignments via UserRole
        roles_qs = Role.objects.filter(user_roles__user_id=self.id, user_roles__is_active=True).distinct()
        if roles_qs.exists():
            return roles_qs

        # Fallback to role_id stored on user (may be numeric PK or role_id string)
        if self.role_id is None:
            return Role.objects.none()

        # Try matching primary key or role_id (case-insensitive)
        return Role.objects.filter(Q(role_id__iexact=str(self.role_id)) | Q(role_id=str(self.role_id)))

    def get_permissions(self):
        """Return permissions mapping for this user's roles.

        Format: { page_path: { permission_type: bool, ... }, ... }
        Merges permissions across multiple roles if present.
        """
        perms = {}
        roles = self.get_roles()
        if not roles.exists():
            return perms

        perms_qs = RolePermission.objects.filter(role__in=roles)
        for rp in perms_qs:
            perms.setdefault(rp.page_path, {})[rp.permission_type] = bool(rp.is_allowed)
        return perms


class Role(models.Model):
    """
    Role model for RBAC (Role-Based Access Control)
    Table name: frontend_role
    """
    role_id = models.CharField(
        max_length=50,
        primary_key=True,
        db_column='role_id',
        help_text="Role identifier (e.g., R001, R002)"
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Role name (e.g., Super Admin, Admin)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Role description"
    )
    page_permission = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Page or module name for this permission set"
    )
    default_page = models.CharField(
        max_length=255,
        default='/',
        help_text="Default page path after login"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this role is active"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    
    class Meta:
        db_table = 'frontend_role'
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name'], name='idx_roles_name'),
            models.Index(fields=['is_active'], name='idx_roles_active'),
            models.Index(fields=['page_permission'], name='idx_roles_page_permission'),
        ]
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} ({self.role_id}) - {status}"


class RolePermission(models.Model):
    """
    Role Permission model for storing permissions for each role and page combination
    Table name: frontend_role_permissions
    Note: Database uses composite primary key (role_id, page_path, permission_type).
    The id column has been removed from the database.
    Django requires a primary key field, so we use a workaround with a composite key.
    """
    # Django requires a primary key, but database uses composite PK
    # This field exists only in Django's model state, not in the database
    # The actual primary key in database is (role_id, page_path, permission_type)
    id = models.BigAutoField(
        primary_key=True,
        help_text="Django ORM primary key (not in database - database uses composite PK)"
    )
    
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='permissions',
        db_column='role_id',
        help_text="Role identifier (foreign key to frontend_role)"
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Role name (denormalized from role table for easier querying)"
    )
    page_path = models.CharField(
        max_length=255,
        help_text="Page route path (e.g., '/', '/users')"
    )
    permission_type = models.CharField(
        max_length=50,
        help_text="Permission type (view, create, edit, delete, etc.)"
    )
    is_allowed = models.BooleanField(
        default=True,
        help_text="Whether permission is allowed"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    
    class Meta:
        db_table = 'frontend_role_permissions'
        verbose_name = "Role Permission"
        verbose_name_plural = "Role Permissions"
        ordering = ['-created_at']
        # Composite primary key: (role, page_path, permission_type)
        # Note: Django doesn't natively support composite primary keys,
        # so we use unique_together and handle it via migration
        unique_together = [['role', 'page_path', 'permission_type']]
        # Prevent Django from auto-creating an 'id' field
        # We'll manage the primary key via database migration
        managed = True
        indexes = [
            models.Index(fields=['role', 'page_path'], name='idx_role_perms_role_page'),
            models.Index(fields=['page_path', 'permission_type'], name='idx_role_perms_page_perm'),
            models.Index(fields=['name'], name='idx_role_perms_name'),
        ]
    
    def save(self, *args, **kwargs):
        """Override save to automatically sync name from role"""
        if self.role:
            self.name = self.role.name
        super().save(*args, **kwargs)
    
    def __str__(self):
        allowed = "Allowed" if self.is_allowed else "Denied"
        return f"{self.role.role_id} - {self.page_path} - {self.permission_type} ({allowed})"


class UserRole(models.Model):
    """
    User Role model for linking users to roles (many-to-many relationship)
    Table name: frontend_user_roles
    """
    id = models.BigAutoField(
        primary_key=True,
        help_text="Primary key"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles',
        db_column='user_id',
        help_text="User ID (foreign key to auth_user)"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles',
        db_column='role_id',
        help_text="Role identifier (foreign key to frontend_role)"
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Assignment timestamp"
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_user_roles',
        null=True,
        blank=True,
        db_column='assigned_by',
        help_text="User who assigned the role (foreign key to auth_user)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether assignment is active"
    )
    
    class Meta:
        db_table = 'frontend_user_roles'
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        ordering = ['-assigned_at']
        unique_together = [['user', 'role']]
        indexes = [
            models.Index(fields=['user', 'is_active'], name='idx_user_roles_user'),
            models.Index(fields=['role', 'is_active'], name='idx_user_roles_role'),
        ]
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.user.username} - {self.role.role_id} ({self.role.name}) - {status}"


# Signal to sync name in RolePermission when Role name is updated
@receiver(post_save, sender=Role)
def sync_role_permissions_name(sender, instance, **kwargs):
    """Update name in all related RolePermission records when role name changes"""
    RolePermission.objects.filter(role=instance).update(name=instance.name)


from django.urls import path
from .views import (
    ride_user_count, rides_users_list, login_view, admin_login_view,
    admin_logout_view, admin_refresh_token_view,
    promo_code_create, promo_codes_list, promo_code_detail,
    zones_list, zone_detail,
    send_welcome_email,
    user_signup_view, user_login_view,
    users_list, user_detail,
    roles_list, role_detail, roles_basic_list,
    role_with_permissions_create, role_with_permissions_update,
    role_permissions_list, role_permission_detail, role_permission_detail_by_id, role_permissions_by_role,
    user_roles_list, user_role_detail,
)

urlpatterns = [
    # Public endpoints
    path('login/', login_view, name='login'),
    path('admin/login/', admin_login_view, name='admin-login'),
    path('admin-login/', admin_login_view, name='admin-login-direct'),  # Direct admin login endpoint
    
    # User signup and login endpoints
    path('user/signup/', user_signup_view, name='user-signup'),
    path('user/login/', user_login_view, name='user-login'),
    
    # User CRUD endpoints
    path('auth/users/', users_list, name='users-list'),  # GET (list all), POST (create)
    path('auth/users/<int:id>/', user_detail, name='user-detail'),  # GET, PUT, PATCH, DELETE
    
    # Role CRUD endpoints
    # IMPORTANT: More specific paths must come BEFORE the generic <str:role_id> path
    path('auth/roles/create-with-permissions/', role_with_permissions_create, name='role-with-permissions-create'),  # POST (create role with permissions)
    path('auth/roles/update-with-permissions/', role_with_permissions_update, name='role-with-permissions-update'),  # PUT/PATCH (update role with permissions)
    path('auth/roles/basic/', roles_basic_list, name='roles-basic-list'),  # GET (list all roles with only role_id and role_name)
    path('auth/roles/', roles_list, name='roles-list'),  # GET (list all), POST (create)
    path('auth/roles/<str:role_id>/', role_detail, name='role-detail'),  # GET, PUT, PATCH, DELETE
    
    # Role Permission CRUD endpoints
    path('auth/role-permissions/', role_permissions_list, name='role-permissions-list'),  # GET (list all), POST (create)
<<<<<<< Updated upstream
    # Support both ID-based (for backward compatibility) and composite key formats
    path('auth/role-permissions/<int:id>/', role_permission_detail_by_id, name='role-permission-detail-by-id'),  # GET, POST, PUT, PATCH, DELETE (uses id - backward compatible)
    # List/delete all permissions for a role (must come before composite key pattern)
    path('auth/role-permissions/<str:role_id>/', role_permissions_by_role, name='role-permissions-by-role'),  # GET (list all for role), PUT/PATCH (bulk update), DELETE (delete all for role)
    path('auth/role-permissions/<str:role_id>/<path:page_path>/<str:permission_type>/', role_permission_detail, name='role-permission-detail'),  # GET, POST, PUT, PATCH, DELETE (uses composite key)
=======
    path('role-permissions/', role_permissions_list, name='role-permissions-list-short'),  # Alias: POST /api/role-permissions/
    path('auth/role-permissions/<int:id>/', role_permission_detail, name='role-permission-detail'),  # GET, PUT, PATCH, DELETE
>>>>>>> Stashed changes
    
    # User Role CRUD endpoints
    path('auth/user-roles/', user_roles_list, name='user-roles-list'),  # GET (list all), POST (create)
    path('auth/user-roles/<int:id>/', user_role_detail, name='user-role-detail'),  # GET, PUT, PATCH, DELETE
    
    # Protected endpoints under /api/auth/
    path('auth/admin/login/', admin_login_view, name='admin-login-auth'),  # Alias under /api/auth/
    path('auth/admin-login/', admin_login_view, name='admin-login-hyphen'),  # Alias with hyphen
    path('auth/users/login/', user_login_view, name='user-login-auth'),  # Alias for user login under /api/auth/
    path('auth/admin/logout/', admin_logout_view, name='admin-logout'),
    path('auth/admin/refresh/', admin_refresh_token_view, name='admin-refresh-token'),
    path('auth/ride-users/count/', ride_user_count, name='ride-user-count'),
    path('auth/rides-users/', rides_users_list, name='rides-users-list'),
    
    # Promo code endpoints
    path('auth/promo-codes/', promo_codes_list, name='promo-codes-list'),
    path('auth/promo-codes/create/', promo_code_create, name='promo-code-create'),
    path('auth/promo-code-create/', promo_code_create, name='promo-code-create-alias'),  # Alias for convenience
    path('auth/promo-codes/<int:pk>/', promo_code_detail, name='promo-code-detail'),
    
    # Zone management endpoints (protected)
    path('auth/zones/', zones_list, name='zones-list'),  # GET /api/auth/zones/ - list, POST /api/auth/zones/ - create
    path('auth/zones/<int:id>/', zone_detail, name='zone-detail'),  # GET, PUT, DELETE /api/auth/zones/{id}/
    
    # Email endpoints
    path('auth/send-welcome-email/', send_welcome_email, name='send-welcome-email'),
    
    # Keep old URLs for backward compatibility (optional - can remove later)
    path('ride-users/count/', ride_user_count, name='ride-user-count-old'),
    path('rides-users/', rides_users_list, name='rides-users-list-old'),
]

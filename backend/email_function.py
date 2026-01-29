# Email API Views

@api_view(['POST'])
@permission_classes([IsAdminUser])  # Require admin authentication
def send_welcome_email(request):
    '''
    Send welcome email to a new user
    
    Request Body:
    {
        "email": "user@example.com",
        "name": "User Name"
    }
    
    Response (Success):
    {
        "message_type": "success",
        "message": "Welcome email sent successfully"
    }
    '''
    try:
        email = request.data.get('email')
        name = request.data.get('name')
        
        if not email or not name:
            return Response({
                'message_type': 'error',
                'error': 'Email and name are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send welcome email
        from django.core.mail import send_mail
        
        subject = 'Welcome to Rudra Ride!'
        message = f'''
        Dear {name},
        
        Welcome to Rudra Ride! Your account has been successfully created.
        
        You can now log in to your account and start using our services.
        
        Best regards,
        Rudra Ride Team
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        return Response({
            'message_type': 'success',
            'message': 'Welcome email sent successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message_type': 'error',
            'error': f'Failed to send email: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

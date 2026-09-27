Security
===========

In-depth security guide for Flask-Exts applications with best practices and advanced patterns.

Authentication Advanced Topics
-------------------------------

Custom Authentication Backends
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implement custom authentication sources::

    from flask_exts.security import UserDatastore, hash_password

    class LDAPUserDatastore(UserDatastore):
        """Authenticate against LDAP directory"""

        def __init__(self, app, ldap_server):
            super().__init__(app)
            self.ldap = ldap_server

        def authenticate(self, username, password):
            """Authenticate via LDAP"""
            try:
                user = self.ldap.authenticate(username, password)
                if user:
                    # Create or update local user
                    local_user = self.find_user(email=user['email'])
                    if not local_user:
                        local_user = self.create_user(
                            email=user['email'],
                            username=username,
                            password=password,
                            active=True
                        )
                    return local_user
            except ldap.INVALID_CREDENTIALS:
                return None

OAuth2 Integration
~~~~~~~~~~~~~~~~~~

Integrate with OAuth2 providers::

    from authlib.integrations.flask_client import OAuth

    oauth = OAuth()

    def init_oauth(app):
        oauth.init_app(app)

        google = oauth.register(
            name='google',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET'],
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            token_url='https://accounts.google.com/o/oauth2/token',
            userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo',
        )

        @app.route('/oauth/google/callback')
        def google_callback():
            token = google.authorize_access_token()
            user_info = token.get('userinfo')

            user = User.query.filter_by(email=user_info['email']).first()
            if not user:
                user = User(
                    email=user_info['email'],
                    username=user_info.get('name'),
                    oauth_provider='google',
                    oauth_id=user_info['id'],
                    active=True
                )
                db.session.add(user)
                db.session.commit()

            login_user(user)
            return redirect('/')

Social Login
~~~~~~~~~~~~

Implement social login::

    class SocialAuthMixin:
        """Mixin for social authentication"""
        oauth_provider: Mapped[str] = mapped_column(nullable=True)
        oauth_id: Mapped[str] = mapped_column(nullable=True)
        oauth_token: Mapped[str] = mapped_column(nullable=True)

    class User(SocialAuthMixin, UserMixin, db.Model):
        id: Mapped[int] = mapped_column(primary_key=True)
        email: Mapped[str] = mapped_column(String(255), unique=True)
        username: Mapped[str] = mapped_column(String(100))

Multi-Factor Authentication Advanced
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Advanced MFA patterns::

    class MFAMethod(db.Model):
        """Different MFA methods for user"""
        id: Mapped[int] = mapped_column(primary_key=True)
        user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
        method_type: Mapped[str] = mapped_column(
            String(20)  # 'totp', 'sms', 'backup_code', 'webauthn'
        )
        data: Mapped[dict] = mapped_column(JSON)
        verified: Mapped[bool] = mapped_column(default=False)
        primary: Mapped[bool] = mapped_column(default=False)

    def verify_mfa(user, method_type, code):
        """Verify MFA code"""
        mfa_method = MFAMethod.query.filter_by(
            user_id=user.id,
            method_type=method_type,
            verified=True
        ).first()

        if not mfa_method:
            return False

        if method_type == 'totp':
            import pyotp
            totp = pyotp.TOTP(mfa_method.data['secret'])
            return totp.verify(code)
        elif method_type == 'sms':
            # Verify SMS code
            return verify_sms_code(mfa_method.data['phone'], code)
        elif method_type == 'backup_code':
            # Verify backup code
            if code in mfa_method.data['codes']:
                mfa_method.data['codes'].remove(code)
                db.session.commit()
                return True

Authorization Advanced Topics
------------------------------

Fine-Grained Access Control
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implement RBAC with granular permissions::

    class Permission(db.Model):
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(100), unique=True)
        description: Mapped[str] = mapped_column(String(255))
        resource: Mapped[str] = mapped_column(String(50))  # 'post', 'user', 'admin'
        action: Mapped[str] = mapped_column(String(50))    # 'create', 'read', 'update', 'delete'

    class Role(db.Model):
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(100), unique=True)
        permissions: Mapped[List[Permission]] = relationship(
            'Permission',
            secondary='role_permission',
            backref='roles'
        )

    def check_permission(user, resource, action):
        """Check if user has permission"""
        for role in user.roles:
            for perm in role.permissions:
                if perm.resource == resource and perm.action == action:
                    return True
        return False

Attribute-Based Access Control (ABAC)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

More flexible access control::

    def check_access(user, resource, action, context=None):
        """
        Evaluate access based on:
        - User attributes (role, department, etc.)
        - Resource attributes (owner, status, etc.)
        - Context (time, location, ip, etc.)
        - Environment (dev, staging, prod)
        """
        context = context or {}

        # Check user role
        if action == 'delete' and 'admin' not in [r.name for r in user.roles]:
            return False

        # Check resource ownership
        if action == 'update' and resource.owner_id != user.id:
            return False

        # Check time-based access (business hours only)
        if action == 'sensitive_action':
            now = datetime.now()
            if not (9 <= now.hour <= 17 and now.weekday() < 5):
                return False

        # Check IP whitelist
        if action == 'admin_action':
            allowed_ips = app.config.get('ADMIN_IP_WHITELIST', [])
            if context.get('ip') not in allowed_ips:
                return False

        return True

Data Security
--------------

Encryption at Rest
~~~~~~~~~~~~~~~~~~

Encrypt sensitive data::

    from cryptography.fernet import Fernet

    class User(db.Model):
        id: Mapped[int] = mapped_column(primary_key=True)
        email: Mapped[str] = mapped_column(String(255))
        _phone: Mapped[str] = mapped_column('phone', String(500), nullable=True)

        def __init__(self, **kwargs):
            self.cipher = Fernet(app.config['ENCRYPTION_KEY'])

        @property
        def phone(self):
            if self._phone:
                return self.cipher.decrypt(self._phone).decode()
            return None

        @phone.setter
        def phone(self, value):
            if value:
                self._phone = self.cipher.encrypt(value.encode())
            else:
                self._phone = None

Sensitive Data Masking
~~~~~~~~~~~~~~~~~~~~~~

Mask sensitive data in logs and responses::

    import re

    def mask_sensitive_data(data):
        """Mask email, phone, SSN in data"""
        # Mask email
        data = re.sub(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            '***@***.***',
            data
        )

        # Mask phone
        data = re.sub(
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            '***-***-****',
            data
        )

        # Mask SSN
        data = re.sub(
            r'\b\d{3}-\d{2}-\d{4}\b',
            '***-**-****',
            data
        )

        return data

Data Deletion and GDPR Compliance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implement right to be forgotten::

    @app.route('/user/<user_id>/delete-account', methods=['POST'])
    @login_required
    def delete_account(user_id):
        """Delete user account and all associated data"""
        if current_user.id != user_id and not current_user.is_admin:
            abort(403)

        user = User.query.get(user_id)
        if not user:
            abort(404)

        # Collect all data to delete
        deletion_records = []

        # Delete user data
        for order in user.orders:
            deletion_records.append(f'Order {order.id}')
            db.session.delete(order)

        for post in user.posts:
            deletion_records.append(f'Post {post.id}')
            db.session.delete(post)

        # Anonymize user account
        user.email = f'deleted_user_{user.id}@example.com'
        user.username = f'deleted_user_{user.id}'
        user.password = None
        user.active = False

        db.session.commit()

        # Log deletion
        audit_log(
            action='DELETE_ACCOUNT',
            user_id=user_id,
            records=deletion_records
        )

        return jsonify({'status': 'account_deleted'})

API Security
------------

Token-Based Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~

Implement JWT tokens::

    from flask_jwt_extended import JWTManager, create_access_token, jwt_required

    jwt = JWTManager(app)

    @app.route('/api/login', methods=['POST'])
    def api_login():
        data = request.json
        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.verify_password(data['password']):
            return {'msg': 'Invalid credentials'}, 401

        access_token = create_access_token(identity=user.id)
        return {
            'access_token': access_token,
            'user': user.to_dict()
        }, 200

    @app.route('/api/protected')
    @jwt_required()
    def protected():
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        return {'user': user.to_dict()}, 200

Rate Limiting
~~~~~~~~~~~~~

Prevent brute force and abuse::

    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )

    @app.route('/api/login', methods=['POST'])
    @limiter.limit("5 per minute")  # 5 login attempts per minute
    def login():
        # Login logic
        pass

    @app.route('/api/forgot-password', methods=['POST'])
    @limiter.limit("3 per hour")  # 3 password reset attempts per hour
    def forgot_password():
        # Password reset logic
        pass

CORS and CSRF Protection
~~~~~~~~~~~~~~~~~~~~~~~~

::

    from flask_cors import CORS
    from flask_wtf.csrf import CSRFProtect

    csrf = CSRFProtect(app)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["https://example.com"],
            "allow_headers": ["Content-Type", "Authorization"],
            "max_age": 3600
        }
    })

    # Exclude CSRF for API endpoints that use JWT
    @app.route('/api/data')
    @csrf.exempt
    def api_data():
        return jsonify({'data': []})

Content Security Policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Prevent XSS attacks::

    @app.after_request
    def set_security_headers(response):
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://fonts.googleapis.com; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "upgrade-insecure-requests"
        )
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

Audit Logging
-------------

Track security-relevant events::

    class AuditLog(db.Model):
        id: Mapped[int] = mapped_column(primary_key=True)
        timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
        user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=True)
        action: Mapped[str] = mapped_column(String(100))
        resource: Mapped[str] = mapped_column(String(100), nullable=True)
        resource_id: Mapped[int] = mapped_column(nullable=True)
        ip_address: Mapped[str] = mapped_column(String(45))
        user_agent: Mapped[str] = mapped_column(String(255))
        status: Mapped[str] = mapped_column(String(20))  # 'success', 'failure'
        details: Mapped[dict] = mapped_column(JSON, nullable=True)

    def audit_log(action, resource=None, resource_id=None, status='success', details=None):
        """Log security-relevant action"""
        log = AuditLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            resource=resource,
            resource_id=resource_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            status=status,
            details=details
        )
        db.session.add(log)
        db.session.commit()

Security Checklist
------------------

Authentication
  ☐ Use strong password hashing (bcrypt, argon2)
  ☐ Implement rate limiting on login
  ☐ Add CAPTCHA for repeated failed attempts
  ☐ Log all authentication attempts
  ☐ Use MFA for sensitive operations

Authorization
  ☐ Implement principle of least privilege
  ☐ Use role-based access control (RBAC)
  ☐ Validate permissions on every request
  ☐ Audit all access denials
  ☐ Regularly review permissions

Data Security
  ☐ Encrypt sensitive data at rest
  ☐ Use HTTPS for all communications
  ☐ Implement GDPR compliance
  ☐ Regular backups with encryption
  ☐ Data retention policies

API Security
  ☐ Use JWT or OAuth2 tokens
  ☐ Implement rate limiting
  ☐ Use CORS properly
  ☐ Input validation on all endpoints
  ☐ Output encoding to prevent XSS

Application Security
  ☐ Input validation and sanitization
  ☐ SQL injection prevention
  ☐ CSRF protection enabled
  ☐ Security headers configured
  ☐ Dependency scanning

See Also
--------

- `OWASP Top 10 <https://owasp.org/Top10/>`_
- `Flask Security <https://flask-security-too.readthedocs.io/>`_
- `Flask-JWT-Extended <https://flask-jwt-extended.readthedocs.io/>`_
- `Cryptography <https://cryptography.io/>`_

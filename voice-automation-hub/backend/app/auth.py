"""Authentication and authorization system."""

import jwt
import bcrypt
import secrets
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class User:
    """User model."""
    id: str
    email: str
    username: str
    role: str
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True


class AuthManager:
    """Authentication and authorization manager."""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        Initialize auth manager.

        Args:
            secret_key: Secret key for JWT
            algorithm: JWT algorithm
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.users: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify password against hash.

        Args:
            password: Plain text password
            hashed: Hashed password

        Returns:
            Whether password is correct
        """
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def create_user(
        self,
        email: str,
        username: str,
        password: str,
        role: str = "user",
    ) -> User:
        """
        Create new user.

        Args:
            email: User email
            username: Username
            password: Password
            role: User role

        Returns:
            Created user

        Raises:
            ValueError: If user already exists
        """
        if email in self.users:
            raise ValueError(f"User with email {email} already exists")

        user_id = f"user_{secrets.token_hex(8)}"
        hashed_password = self.hash_password(password)

        user_data = {
            "id": user_id,
            "email": email,
            "username": username,
            "password": hashed_password,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "is_active": True,
        }

        self.users[email] = user_data
        logger.info(f"User created: {email} (role: {role})")

        return User(
            id=user_id,
            email=email,
            username=username,
            role=role,
            created_at=user_data["created_at"],
        )

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user.

        Args:
            email: User email
            password: Password

        Returns:
            User if authenticated, None otherwise
        """
        user_data = self.users.get(email)
        if not user_data:
            logger.warning(f"Authentication failed: user not found ({email})")
            return None

        if not user_data.get("is_active", True):
            logger.warning(f"Authentication failed: user inactive ({email})")
            return None

        if not self.verify_password(password, user_data["password"]):
            logger.warning(f"Authentication failed: invalid password ({email})")
            return None

        # Update last login
        user_data["last_login"] = datetime.now().isoformat()

        logger.info(f"User authenticated: {email}")
        return User(
            id=user_data["id"],
            email=user_data["email"],
            username=user_data["username"],
            role=user_data["role"],
            created_at=user_data["created_at"],
            last_login=user_data["last_login"],
        )

    def create_access_token(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create JWT access token.

        Args:
            user: User to create token for
            expires_delta: Token expiration time

        Returns:
            JWT token
        """
        if expires_delta is None:
            expires_delta = timedelta(hours=24)

        expire = datetime.utcnow() + expires_delta

        payload = {
            "sub": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Access token created for user: {user.email}")
        return token

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token

        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token verification failed: expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token verification failed: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        for user_data in self.users.values():
            if user_data["id"] == user_id:
                return User(
                    id=user_data["id"],
                    email=user_data["email"],
                    username=user_data["username"],
                    role=user_data["role"],
                    created_at=user_data["created_at"],
                    last_login=user_data.get("last_login"),
                )
        return None

    def update_user(
        self, user_id: str, updates: Dict[str, Any]
    ) -> Optional[User]:
        """
        Update user information.

        Args:
            user_id: User ID
            updates: Fields to update

        Returns:
            Updated user if found, None otherwise
        """
        for email, user_data in self.users.items():
            if user_data["id"] == user_id:
                # Update allowed fields
                for key, value in updates.items():
                    if key in ["username", "role", "is_active"]:
                        user_data[key] = value

                logger.info(f"User updated: {email}")
                return self.get_user_by_id(user_id)

        return None

    def delete_user(self, user_id: str) -> bool:
        """
        Delete user.

        Args:
            user_id: User ID

        Returns:
            Whether user was deleted
        """
        for email, user_data in list(self.users.items()):
            if user_data["id"] == user_id:
                del self.users[email]
                logger.info(f"User deleted: {email}")
                return True

        return False

    def list_users(self) -> list[User]:
        """List all users."""
        return [
            User(
                id=data["id"],
                email=data["email"],
                username=data["username"],
                role=data["role"],
                created_at=data["created_at"],
                last_login=data.get("last_login"),
                is_active=data.get("is_active", True),
            )
            for data in self.users.values()
        ]


class PermissionChecker:
    """Check user permissions."""

    ROLES = {
        "admin": ["read", "write", "delete", "admin"],
        "user": ["read", "write"],
        "viewer": ["read"],
    }

    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        """
        Check if user has permission.

        Args:
            user: User to check
            permission: Required permission

        Returns:
            Whether user has permission
        """
        user_permissions = PermissionChecker.ROLES.get(user.role, [])
        return permission in user_permissions

    @staticmethod
    def require_permission(user: Optional[User], permission: str) -> bool:
        """
        Require user to have permission.

        Args:
            user: User to check
            permission: Required permission

        Returns:
            Whether user has permission

        Raises:
            ValueError: If user doesn't have permission
        """
        if not user:
            raise ValueError("Authentication required")

        if not PermissionChecker.has_permission(user, permission):
            raise ValueError(
                f"Permission denied: {permission} required (user role: {user.role})"
            )

        return True


# Initialize with environment variable or generate random key
import os

SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
auth_manager = AuthManager(SECRET_KEY)

# Create default admin user if none exists
if not auth_manager.list_users():
    try:
        auth_manager.create_user(
            email="admin@voicehub.local",
            username="admin",
            password="admin123",  # Change in production!
            role="admin",
        )
        logger.info("Default admin user created")
    except Exception as e:
        logger.error(f"Failed to create default admin: {e}")


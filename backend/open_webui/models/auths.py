import logging
import uuid
import time
from typing import Optional

from open_webui.internal.db import Base, get_db
from open_webui.models.users import UserModel, Users
from open_webui.env import SRC_LOG_LEVELS
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, String, Text, BigInteger
from open_webui.utils.auth import verify_password

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# DB MODEL
####################


class Auth(Base):
    __tablename__ = "auth"

    id = Column(String, primary_key=True)
    email = Column(String)
    password = Column(Text)
    active = Column(Boolean)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_token"

    token = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    expires_at = Column(BigInteger, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(BigInteger, nullable=False)


class AuthModel(BaseModel):
    id: str
    email: str
    password: str
    active: bool = True


class PasswordResetTokenModel(BaseModel):
    token: str
    user_id: str
    email: str
    expires_at: int
    used: bool = False
    created_at: int


####################
# Forms
####################


class Token(BaseModel):
    token: str
    token_type: str


class ApiKey(BaseModel):
    api_key: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    profile_image_url: str
    user_type: Optional[str] = "individual"


class SigninResponse(Token, UserResponse):
    pass


class SigninForm(BaseModel):
    email: str
    password: str


class LdapForm(BaseModel):
    user: str
    password: str


class ProfileImageUrlForm(BaseModel):
    profile_image_url: str


class UpdatePasswordForm(BaseModel):
    password: str
    new_password: str


class SignupForm(BaseModel):
    name: str
    email: str
    password: str
    profile_image_url: Optional[str] = "/user.png"
    plan_id: Optional[str] = None  # Subscription plan ID
    payment_id: Optional[str] = None  # Payment gateway transaction ID
    dob: Optional[str] = None  # Date of birth (YYYY-MM-DD format)
    phone: Optional[str] = None  # Phone number
    user_type: Optional[str] = "individual"  # Registration type: org or individual


class GuestSigninForm(BaseModel):
    name: str
    email: str


class ForgotPasswordForm(BaseModel):
    email: str


class ResetPasswordForm(BaseModel):
    token: str
    new_password: str


class AddUserForm(SignupForm):
    role: Optional[str] = "pending"


class AuthsTable:
    def insert_new_auth(
        self,
        email: str,
        password: str,
        name: str,
        profile_image_url: str = "/user.png",
        role: str = "pending",
        oauth_sub: Optional[str] = None,
        dob: Optional[str] = None,
        phone: Optional[str] = None,
        user_type: Optional[str] = "individual",
        organization_id: Optional[str] = None,
    ) -> Optional[UserModel]:
        import time
        from datetime import datetime
        from open_webui.models.users import User, UserModel
        
        with get_db() as db:
            log.info("insert_new_auth")

            id = str(uuid.uuid4())

            # Create auth record
            auth = AuthModel(
                **{"id": id, "email": email, "password": password, "active": True}
            )
            auth_result = Auth(**auth.model_dump())
            db.add(auth_result)

            # Parse date of birth if provided
            date_of_birth = None
            if dob:
                try:
                    date_of_birth = datetime.strptime(dob, "%Y-%m-%d").date()
                except ValueError:
                    log.warning(f"Invalid date format for DOB: {dob}")

            # Create user record in the same transaction

            user_data = {
                "id": id,
                "name": name,
                "email": email,
                "role": role,
                "profile_image_url": profile_image_url,
                "last_active_at": int(time.time()),
                "created_at": int(time.time()),
                "updated_at": int(time.time()),
                "oauth_sub": oauth_sub,
                "user_type": user_type,
            }
            if date_of_birth:
                user_data["date_of_birth"] = date_of_birth
            if phone:
                user_data["phone"] = phone
            if organization_id:
                user_data["organization_id"] = organization_id

            user_model = UserModel(**user_data)
            user_result = User(**user_model.model_dump())
            db.add(user_result)

            # Commit both records in single transaction
            db.commit()
            db.refresh(auth_result)
            db.refresh(user_result)

            if auth_result and user_result:
                return user_model
            else:
                return None

    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        log.info(f"authenticate_user: {email}")

        user = Users.get_user_by_email(email)
        if not user:
            return None

        try:
            with get_db() as db:
                auth = db.query(Auth).filter_by(id=user.id, active=True).first()
                if auth:
                    if verify_password(password, auth.password):
                        return user
                    else:
                        return None
                else:
                    return None
        except Exception:
            return None

    def authenticate_user_by_api_key(self, api_key: str) -> Optional[UserModel]:
        log.info(f"authenticate_user_by_api_key: {api_key}")
        # if no api_key, return None
        if not api_key:
            return None

        try:
            user = Users.get_user_by_api_key(api_key)
            return user if user else None
        except Exception:
            return False

    def authenticate_user_by_email(self, email: str) -> Optional[UserModel]:
        log.info(f"authenticate_user_by_email: {email}")
        try:
            with get_db() as db:
                auth = db.query(Auth).filter_by(email=email, active=True).first()
                if auth:
                    user = Users.get_user_by_id(auth.id)
                    return user
        except Exception:
            return None

    def update_user_password_by_id(self, id: str, new_password: str) -> bool:
        try:
            with get_db() as db:
                result = (
                    db.query(Auth).filter_by(id=id).update({"password": new_password})
                )
                db.commit()
                return True if result == 1 else False
        except Exception:
            return False

    def update_email_by_id(self, id: str, email: str) -> bool:
        try:
            with get_db() as db:
                result = db.query(Auth).filter_by(id=id).update({"email": email})
                db.commit()
                return True if result == 1 else False
        except Exception:
            return False

    def delete_auth_by_id(self, id: str) -> bool:
        try:
            with get_db() as db:
                # Delete User
                result = Users.delete_user_by_id(id)

                if result:
                    db.query(Auth).filter_by(id=id).delete()
                    db.commit()

                    return True
                else:
                    return False
        except Exception:
            return False


Auths = AuthsTable()


####################
# Password Reset Tokens
####################


class PasswordResetTokensTable:
    def create_token(self, user_id: str, email: str) -> Optional[PasswordResetTokenModel]:
        """Create a new password reset token valid for 24 hours"""
        try:
            with get_db() as db:
                # Delete any existing unused tokens for this user
                db.query(PasswordResetToken).filter_by(user_id=user_id, used=False).delete()
                
                # Generate secure token
                token = secrets.token_urlsafe(32)
                current_time = int(time.time())
                expires_at = current_time + (24 * 60 * 60)  # 24 hours from now
                
                reset_token = PasswordResetTokenModel(
                    token=token,
                    user_id=user_id,
                    email=email.lower(),
                    expires_at=expires_at,
                    used=False,
                    created_at=current_time
                )
                
                result = PasswordResetToken(**reset_token.model_dump())
                db.add(result)
                db.commit()
                db.refresh(result)
                
                return reset_token
        except Exception as e:
            log.error(f"Error creating password reset token: {e}")
            return None
    
    def get_valid_token(self, token: str) -> Optional[PasswordResetTokenModel]:
        """Get a valid (not expired, not used) password reset token"""
        try:
            with get_db() as db:
                current_time = int(time.time())
                result = db.query(PasswordResetToken).filter_by(token=token).first()
                
                if result:
                    # Check if token is expired or already used
                    if result.used:
                        log.warning(f"Token already used: {token}")
                        return None
                    if result.expires_at < current_time:
                        log.warning(f"Token expired: {token}")
                        return None
                    
                    return PasswordResetTokenModel(**result.__dict__)
                return None
        except Exception as e:
            log.error(f"Error getting password reset token: {e}")
            return None
    
    def mark_token_as_used(self, token: str) -> bool:
        """Mark a password reset token as used"""
        try:
            with get_db() as db:
                result = db.query(PasswordResetToken).filter_by(token=token).update({"used": True})
                db.commit()
                return True if result == 1 else False
        except Exception as e:
            log.error(f"Error marking token as used: {e}")
            return False
    
    def delete_expired_tokens(self) -> int:
        """Delete all expired tokens (cleanup task)"""
        try:
            with get_db() as db:
                current_time = int(time.time())
                result = db.query(PasswordResetToken).filter(
                    PasswordResetToken.expires_at < current_time
                ).delete()
                db.commit()
                return result
        except Exception as e:
            log.error(f"Error deleting expired tokens: {e}")
            return 0


import secrets

PasswordResetTokens = PasswordResetTokensTable()

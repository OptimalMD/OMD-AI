import json
import logging
import time
from typing import Optional, List
import uuid

from open_webui.internal.db import Base, get_db, JSONField
from open_webui.env import SRC_LOG_LEVELS

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, JSON, Boolean


log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Organization DB Schema
####################


class Organization(Base):
    __tablename__ = "organization"

    id = Column(Text, unique=True, primary_key=True)
    org_name = Column(Text, nullable=False)
    org_code = Column(Text, unique=True, nullable=False)
    
    dark_logo = Column(Text, nullable=True)  # URL or base64 data for dark mode logo
    light_logo = Column(Text, nullable=True)  # URL or base64 data for light mode logo
    
    plans = Column(JSONField, nullable=True)  # Array of subscription plan IDs
    users = Column(JSONField, nullable=True)  # Array of user IDs
    
    status = Column(String, default="active")  # active, inactive, suspended
    signup_enabled = Column(Boolean, default=True)  # Enable/disable signup for this org
    
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class OrganizationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    org_name: str
    org_code: str
    
    dark_logo: Optional[str] = None
    light_logo: Optional[str] = None
    
    plans: Optional[List[str]] = []
    users: Optional[List[str]] = []
    
    status: str = "active"
    signup_enabled: bool = True
    
    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch


####################
# Forms
####################


class OrganizationResponse(BaseModel):
    id: str
    org_name: str
    org_code: str
    dark_logo: Optional[str] = None
    light_logo: Optional[str] = None
    plans: Optional[List[str]] = []
    users: Optional[List[str]] = []
    status: str = "active"
    signup_enabled: bool = True
    created_at: int
    updated_at: int


class OrganizationForm(BaseModel):
    org_name: str
    org_code: str
    dark_logo: Optional[str] = None
    light_logo: Optional[str] = None
    plans: Optional[List[str]] = []
    users: Optional[List[str]] = []
    status: Optional[str] = "active"
    signup_enabled: Optional[bool] = True


class OrganizationUpdateForm(BaseModel):
    org_name: Optional[str] = None
    org_code: Optional[str] = None
    dark_logo: Optional[str] = None
    light_logo: Optional[str] = None
    plans: Optional[List[str]] = None
    users: Optional[List[str]] = None
    status: Optional[str] = None
    signup_enabled: Optional[bool] = None


class OrganizationTable:
    def insert_new_organization(
        self, form_data: OrganizationForm
    ) -> Optional[OrganizationModel]:
        with get_db() as db:
            # Check if org_code already exists
            existing_org = db.query(Organization).filter_by(org_code=form_data.org_code).first()
            if existing_org:
                raise ValueError(f"Organization with code '{form_data.org_code}' already exists")
            
            organization = OrganizationModel(
                **{
                    **form_data.model_dump(exclude_none=True),
                    "id": str(uuid.uuid4()),
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )

            try:
                result = Organization(**organization.model_dump())
                db.add(result)
                db.commit()
                db.refresh(result)
                if result:
                    return OrganizationModel.model_validate(result)
                else:
                    return None

            except Exception as e:
                log.exception(e)
                return None

    def get_organizations(self) -> List[OrganizationModel]:
        with get_db() as db:
            return [
                OrganizationModel.model_validate(org)
                for org in db.query(Organization).order_by(Organization.updated_at.desc()).all()
            ]

    def get_organization_by_id(self, id: str) -> Optional[OrganizationModel]:
        try:
            with get_db() as db:
                organization = db.query(Organization).filter_by(id=id).first()
                return OrganizationModel.model_validate(organization) if organization else None
        except Exception as e:
            log.exception(e)
            return None

    def get_organization_by_code(self, org_code: str) -> Optional[OrganizationModel]:
        try:
            with get_db() as db:
                organization = db.query(Organization).filter_by(org_code=org_code).first()
                return OrganizationModel.model_validate(organization) if organization else None
        except Exception as e:
            log.exception(e)
            return None

    def update_organization_by_id(
        self, id: str, form_data: OrganizationUpdateForm
    ) -> Optional[OrganizationModel]:
        try:
            with get_db() as db:
                # If org_code is being updated, check if it already exists
                if form_data.org_code:
                    existing_org = db.query(Organization).filter(
                        Organization.org_code == form_data.org_code,
                        Organization.id != id
                    ).first()
                    if existing_org:
                        raise ValueError(f"Organization with code '{form_data.org_code}' already exists")
                
                update_data = form_data.model_dump(exclude_none=True)
                update_data["updated_at"] = int(time.time())
                
                db.query(Organization).filter_by(id=id).update(update_data)
                db.commit()
                return self.get_organization_by_id(id=id)
        except Exception as e:
            log.exception(e)
            raise

    def delete_organization_by_id(self, id: str) -> bool:
        try:
            with get_db() as db:
                db.query(Organization).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception as e:
            log.exception(e)
            return False

    def add_users_to_organization(
        self, id: str, user_ids: List[str]
    ) -> Optional[OrganizationModel]:
        try:
            with get_db() as db:
                organization = db.query(Organization).filter_by(id=id).first()
                if not organization:
                    return None

                org_user_ids = organization.users
                if not org_user_ids or not isinstance(org_user_ids, list):
                    org_user_ids = []

                org_user_ids = list(set(org_user_ids))  # Deduplicate

                for user_id in user_ids:
                    if user_id not in org_user_ids:
                        org_user_ids.append(user_id)

                organization.users = org_user_ids
                organization.updated_at = int(time.time())
                db.commit()
                db.refresh(organization)
                return OrganizationModel.model_validate(organization)
        except Exception as e:
            log.exception(e)
            return None

    def remove_users_from_organization(
        self, id: str, user_ids: List[str]
    ) -> Optional[OrganizationModel]:
        try:
            with get_db() as db:
                organization = db.query(Organization).filter_by(id=id).first()
                if not organization:
                    return None

                org_user_ids = organization.users

                if not org_user_ids or not isinstance(org_user_ids, list):
                    return OrganizationModel.model_validate(organization)

                org_user_ids = list(set(org_user_ids))  # Deduplicate

                for user_id in user_ids:
                    if user_id in org_user_ids:
                        org_user_ids.remove(user_id)

                organization.users = org_user_ids
                organization.updated_at = int(time.time())

                db.commit()
                db.refresh(organization)
                return OrganizationModel.model_validate(organization)
        except Exception as e:
            log.exception(e)
            return None

    def add_plans_to_organization(
        self, id: str, plan_ids: List[str]
    ) -> Optional[OrganizationModel]:
        try:
            with get_db() as db:
                organization = db.query(Organization).filter_by(id=id).first()
                if not organization:
                    return None

                org_plan_ids = organization.plans
                if not org_plan_ids or not isinstance(org_plan_ids, list):
                    org_plan_ids = []

                org_plan_ids = list(set(org_plan_ids))  # Deduplicate

                for plan_id in plan_ids:
                    if plan_id not in org_plan_ids:
                        org_plan_ids.append(plan_id)

                organization.plans = org_plan_ids
                organization.updated_at = int(time.time())
                db.commit()
                db.refresh(organization)
                return OrganizationModel.model_validate(organization)
        except Exception as e:
            log.exception(e)
            return None

    def remove_plans_from_organization(
        self, id: str, plan_ids: List[str]
    ) -> Optional[OrganizationModel]:
        try:
            with get_db() as db:
                organization = db.query(Organization).filter_by(id=id).first()
                if not organization:
                    return None

                org_plan_ids = organization.plans

                if not org_plan_ids or not isinstance(org_plan_ids, list):
                    return OrganizationModel.model_validate(organization)

                org_plan_ids = list(set(org_plan_ids))  # Deduplicate

                for plan_id in plan_ids:
                    if plan_id in org_plan_ids:
                        org_plan_ids.remove(plan_id)

                organization.plans = org_plan_ids
                organization.updated_at = int(time.time())

                db.commit()
                db.refresh(organization)
                return OrganizationModel.model_validate(organization)
        except Exception as e:
            log.exception(e)
            return None


Organizations = OrganizationTable()

"""
Guest user cleanup utility.
Removes guest users that are older than 24 hours.
"""

import logging
import time
from open_webui.models.users import Users
from open_webui.models.auths import Auths

log = logging.getLogger(__name__)


def cleanup_expired_guest_users():
    """
    Clean up guest users that are older than 24 hours.
    This should be run periodically (e.g., via a cron job or background task).
    """
    try:
        # Get all users with user_type='guest'
        all_users = Users.get_users(skip=0, limit=10000)  # Adjust limit as needed
        
        current_time = int(time.time())
        cleanup_threshold = 24 * 60 * 60  # 24 hours in seconds
        
        deleted_count = 0
        
        for user in all_users:
            # Check user_type instead of role to identify guest users
            if hasattr(user, 'user_type') and user.user_type == 'guest':
                # Check if user is older than 24 hours
                user_age = current_time - user.created_at
                
                if user_age > cleanup_threshold:
                    # Delete the guest user
                    success = Auths.delete_auth_by_id(user.id)
                    if success:
                        deleted_count += 1
                        log.info(f"Deleted expired guest user: {user.id} ({user.email})")
                    else:
                        log.error(f"Failed to delete guest user: {user.id}")
        
        log.info(f"Guest cleanup completed. Deleted {deleted_count} expired guest users.")
        return deleted_count
        
    except Exception as e:
        log.error(f"Error during guest user cleanup: {str(e)}")
        return 0

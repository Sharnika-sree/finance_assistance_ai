import json
import os
from typing import Optional
from models.user_profile import UserProfile

class ProfileService:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
   
    def save_profile(self, profile: UserProfile) -> bool:
        """Save user profile to JSON file"""
        try:
            file_path = os.path.join(self.data_dir, f"profile_{profile.user_id}.json")
            with open(file_path, 'w') as f:
                json.dump(profile.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False
   
    def load_profile(self, user_id: str) -> Optional[UserProfile]:
        """Load user profile from JSON file"""
        try:
            file_path = os.path.join(self.data_dir, f"profile_{user_id}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                return UserProfile.from_dict(data)
            return None
        except Exception as e:
            print(f"Error loading profile: {e}")
            return None
   
    def profile_exists(self, user_id: str) -> bool:
        """Check if profile exists"""
        file_path = os.path.join(self.data_dir, f"profile_{user_id}.json")
        return os.path.exists(file_path)
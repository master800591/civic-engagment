"""
CITIZEN VERIFICATION SYSTEM
Real-world government officials verify platform users as citizens
Hierarchical citizenship verification: Country → State → City/Town
"""

import json
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import uuid

# Import blockchain for transparency
try:
    from ..blockchain.blockchain import Blockchain
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    print("Warning: Blockchain not available for citizen verification logging")
    BLOCKCHAIN_AVAILABLE = False

# Import session management
try:
    from ..users.session import SessionManager
    SESSION_AVAILABLE = True
except ImportError:
    print("Warning: Session management not available")
    SESSION_AVAILABLE = False


class CitizenshipLevel(Enum):
    """Levels of citizenship verification"""
    COUNTRY = "country"
    STATE = "state" 
    CITY = "city"
    TOWN = "town"


class CitizenshipStatus(Enum):
    """Status of citizenship verification"""
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    REVOKED = "revoked"


class VerificationMethod(Enum):
    """Methods of citizenship verification"""
    GOVERNMENT_ID = "government_id"
    BIRTH_CERTIFICATE = "birth_certificate"
    PASSPORT = "passport"
    NATURALIZATION_CERTIFICATE = "naturalization_certificate"
    VOTER_REGISTRATION = "voter_registration"
    UTILITY_BILLS = "utility_bills"
    TAX_RECORDS = "tax_records"
    IN_PERSON_VERIFICATION = "in_person_verification"


class CitizenVerificationManager:
    """Manages citizen verification by real-world government officials"""
    
    def __init__(self, config_path: str = None):
        """Initialize the citizen verification system"""
        
        # Configuration
        self.config_path = config_path or "government/citizen_verification_db.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Load or initialize database
        self.verification_data = self._load_verification_database()
        
        # Initialize verification statistics
        self.stats_cache = None
        self.stats_cache_time = None
        
    def _load_verification_database(self) -> Dict[str, Any]:
        """Load citizen verification database"""
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Initialize with default structure
        return {
            "citizen_verifications": {},
            "verification_requests": {},
            "government_verifiers": {},
            "verification_statistics": {
                "total_requests": 0,
                "verified_citizens": 0,
                "pending_verifications": 0,
                "rejected_verifications": 0
            },
            "verification_history": [],
            "system_metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }
    
    def _save_verification_database(self) -> bool:
        """Save citizen verification database"""
        
        try:
            # Update metadata
            self.verification_data["system_metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.verification_data, f, indent=2, ensure_ascii=False)
            
            # Clear stats cache
            self.stats_cache = None
            self.stats_cache_time = None
            
            return True
            
        except Exception as e:
            print(f"Error saving citizen verification database: {e}")
            return False
    
    def request_citizenship_verification(
        self,
        user_email: str,
        citizenship_level: CitizenshipLevel,
        jurisdiction: str,
        country: str,
        verification_documents: List[Dict[str, str]],
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """Request citizenship verification from government officials"""
        
        try:
            # Generate verification request ID
            request_id = f"citizen_verify_{uuid.uuid4().hex[:12]}"
            
            # Create verification request
            verification_request = {
                "request_id": request_id,
                "user_email": user_email,
                "citizenship_level": citizenship_level.value,
                "jurisdiction": jurisdiction,
                "country": country,
                "status": CitizenshipStatus.PENDING.value,
                "verification_documents": verification_documents,
                "additional_info": additional_info or {},
                "requested_at": datetime.now().isoformat(),
                "assigned_verifier": None,
                "verifier_notes": "",
                "verification_method": [],
                "evidence_provided": [],
                "blockchain_reference": None
            }
            
            # Store verification request
            self.verification_data["verification_requests"][request_id] = verification_request
            
            # Update statistics
            self.verification_data["verification_statistics"]["total_requests"] += 1
            self.verification_data["verification_statistics"]["pending_verifications"] += 1
            
            # Add to history
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "verification_requested",
                "request_id": request_id,
                "user_email": user_email,
                "jurisdiction": f"{jurisdiction}, {country}",
                "level": citizenship_level.value
            }
            self.verification_data["verification_history"].append(history_entry)
            
            # Save database
            if not self._save_verification_database():
                return False, "Failed to save verification request"
            
            # Record on blockchain for transparency
            if BLOCKCHAIN_AVAILABLE:
                blockchain_data = {
                    "request_id": request_id,
                    "user_email": user_email,
                    "citizenship_level": citizenship_level.value,
                    "jurisdiction": jurisdiction,
                    "country": country,
                    "documents_count": len(verification_documents)
                }
                
                try:
                    Blockchain.add_page(
                        action_type="citizenship_verification_requested",
                        data=blockchain_data,
                        user_email=user_email
                    )
                    verification_request["blockchain_reference"] = "recorded"
                except Exception as e:
                    print(f"Blockchain recording failed: {e}")
            
            return True, f"Citizenship verification requested: {request_id}"
            
        except Exception as e:
            return False, f"Failed to request citizenship verification: {str(e)}"
    
    def assign_government_verifier(
        self,
        request_id: str,
        verifier_email: str,
        verifier_title: str,
        verifier_jurisdiction: str
    ) -> Tuple[bool, str]:
        """Assign government official as verifier for citizenship request"""
        
        try:
            # Check if request exists
            if request_id not in self.verification_data["verification_requests"]:
                return False, "Verification request not found"
            
            request = self.verification_data["verification_requests"][request_id]
            
            # Verify request is still pending
            if request["status"] != CitizenshipStatus.PENDING.value:
                return False, f"Request status is {request['status']}, cannot assign verifier"
            
            # Create verifier record
            verifier_info = {
                "verifier_email": verifier_email,
                "verifier_title": verifier_title,
                "verifier_jurisdiction": verifier_jurisdiction,
                "assigned_at": datetime.now().isoformat(),
                "verification_authority": self._determine_verification_authority(
                    request["citizenship_level"],
                    verifier_title,
                    verifier_jurisdiction
                )
            }
            
            # Update request with assigned verifier
            request["assigned_verifier"] = verifier_info
            request["status"] = "under_review"
            
            # Record verifier in government verifiers database
            if verifier_email not in self.verification_data["government_verifiers"]:
                self.verification_data["government_verifiers"][verifier_email] = {
                    "verifier_email": verifier_email,
                    "title": verifier_title,
                    "jurisdiction": verifier_jurisdiction,
                    "verifications_assigned": 0,
                    "verifications_completed": 0,
                    "first_assigned": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat()
                }
            
            # Update verifier statistics
            verifier_record = self.verification_data["government_verifiers"][verifier_email]
            verifier_record["verifications_assigned"] += 1
            verifier_record["last_activity"] = datetime.now().isoformat()
            
            # Add to history
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "verifier_assigned",
                "request_id": request_id,
                "verifier_email": verifier_email,
                "verifier_title": verifier_title,
                "jurisdiction": verifier_jurisdiction
            }
            self.verification_data["verification_history"].append(history_entry)
            
            # Save database
            if not self._save_verification_database():
                return False, "Failed to save verifier assignment"
            
            # Record on blockchain
            if BLOCKCHAIN_AVAILABLE:
                blockchain_data = {
                    "request_id": request_id,
                    "verifier_email": verifier_email,
                    "verifier_title": verifier_title,
                    "verifier_jurisdiction": verifier_jurisdiction,
                    "user_email": request["user_email"]
                }
                
                try:
                    Blockchain.add_page(
                        action_type="citizenship_verifier_assigned",
                        data=blockchain_data,
                        user_email=verifier_email
                    )
                except Exception as e:
                    print(f"Blockchain recording failed: {e}")
            
            return True, f"Government verifier assigned: {verifier_title}"
            
        except Exception as e:
            return False, f"Failed to assign verifier: {str(e)}"
    
    def complete_citizenship_verification(
        self,
        request_id: str,
        verifier_email: str,
        verification_decision: CitizenshipStatus,
        verification_methods: List[VerificationMethod],
        verifier_notes: str,
        evidence_reviewed: List[str]
    ) -> Tuple[bool, str]:
        """Complete citizenship verification by government official"""
        
        try:
            # Check if request exists
            if request_id not in self.verification_data["verification_requests"]:
                return False, "Verification request not found"
            
            request = self.verification_data["verification_requests"][request_id]
            
            # Verify the verifier is assigned to this request
            if not request.get("assigned_verifier") or request["assigned_verifier"]["verifier_email"] != verifier_email:
                return False, "Verifier not authorized for this request"
            
            # Update request with verification results
            request["status"] = verification_decision.value
            request["verifier_notes"] = verifier_notes
            request["verification_method"] = [method.value for method in verification_methods]
            request["evidence_provided"] = evidence_reviewed
            request["verified_at"] = datetime.now().isoformat()
            request["verification_completed"] = True
            
            # If verified, create citizen verification record
            if verification_decision == CitizenshipStatus.VERIFIED:
                citizen_verification = {
                    "user_email": request["user_email"],
                    "citizenship_level": request["citizenship_level"],
                    "jurisdiction": request["jurisdiction"],
                    "country": request["country"],
                    "verified_by": verifier_email,
                    "verified_at": datetime.now().isoformat(),
                    "verification_methods": [method.value for method in verification_methods],
                    "evidence_reviewed": evidence_reviewed,
                    "verifier_title": request["assigned_verifier"]["verifier_title"],
                    "verifier_jurisdiction": request["assigned_verifier"]["verifier_jurisdiction"],
                    "verification_id": f"citizen_{uuid.uuid4().hex[:8]}",
                    "blockchain_reference": None,
                    "status": "active"
                }
                
                # Store citizen verification
                verification_key = f"{request['user_email']}_{request['citizenship_level']}_{request['jurisdiction']}"
                self.verification_data["citizen_verifications"][verification_key] = citizen_verification
                
                # Update statistics
                self.verification_data["verification_statistics"]["verified_citizens"] += 1
            
            # Update statistics
            self.verification_data["verification_statistics"]["pending_verifications"] -= 1
            
            if verification_decision == CitizenshipStatus.REJECTED:
                self.verification_data["verification_statistics"]["rejected_verifications"] += 1
            
            # Update verifier statistics
            if verifier_email in self.verification_data["government_verifiers"]:
                verifier_record = self.verification_data["government_verifiers"][verifier_email]
                verifier_record["verifications_completed"] += 1
                verifier_record["last_activity"] = datetime.now().isoformat()
            
            # Add to history
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "verification_completed",
                "request_id": request_id,
                "user_email": request["user_email"],
                "verifier_email": verifier_email,
                "decision": verification_decision.value,
                "jurisdiction": f"{request['jurisdiction']}, {request['country']}"
            }
            self.verification_data["verification_history"].append(history_entry)
            
            # Save database
            if not self._save_verification_database():
                return False, "Failed to save verification results"
            
            # Record on blockchain for transparency
            if BLOCKCHAIN_AVAILABLE:
                blockchain_data = {
                    "request_id": request_id,
                    "user_email": request["user_email"],
                    "verifier_email": verifier_email,
                    "decision": verification_decision.value,
                    "citizenship_level": request["citizenship_level"],
                    "jurisdiction": request["jurisdiction"],
                    "country": request["country"],
                    "verification_methods": [method.value for method in verification_methods]
                }
                
                try:
                    Blockchain.add_page(
                        action_type="citizenship_verification_completed",
                        data=blockchain_data,
                        user_email=verifier_email
                    )
                    
                    if verification_decision == CitizenshipStatus.VERIFIED:
                        verification_key = f"{request['user_email']}_{request['citizenship_level']}_{request['jurisdiction']}"
                        self.verification_data["citizen_verifications"][verification_key]["blockchain_reference"] = "recorded"
                        
                except Exception as e:
                    print(f"Blockchain recording failed: {e}")
            
            decision_text = "VERIFIED" if verification_decision == CitizenshipStatus.VERIFIED else "REJECTED"
            return True, f"Citizenship verification {decision_text} for {request['user_email']}"
            
        except Exception as e:
            return False, f"Failed to complete verification: {str(e)}"
    
    def get_user_citizenship_status(self, user_email: str) -> Dict[str, Any]:
        """Get citizenship verification status for user"""
        
        try:
            user_citizenships = {}
            
            # Find all citizenship verifications for user
            for key, verification in self.verification_data["citizen_verifications"].items():
                if verification["user_email"] == user_email:
                    level = verification["citizenship_level"]
                    user_citizenships[level] = {
                        "jurisdiction": verification["jurisdiction"],
                        "country": verification["country"],
                        "verified_by": verification["verified_by"],
                        "verified_at": verification["verified_at"],
                        "verifier_title": verification["verifier_title"],
                        "verification_id": verification["verification_id"],
                        "status": verification["status"]
                    }
            
            # Find pending verification requests
            pending_requests = []
            for request_id, request in self.verification_data["verification_requests"].items():
                if (request["user_email"] == user_email and 
                    request["status"] in [CitizenshipStatus.PENDING.value, "under_review"]):
                    pending_requests.append({
                        "request_id": request_id,
                        "citizenship_level": request["citizenship_level"],
                        "jurisdiction": request["jurisdiction"],
                        "country": request["country"],
                        "status": request["status"],
                        "requested_at": request["requested_at"]
                    })
            
            return {
                "user_email": user_email,
                "verified_citizenships": user_citizenships,
                "pending_requests": pending_requests,
                "citizenship_count": len(user_citizenships),
                "has_country_citizenship": "country" in user_citizenships,
                "has_state_citizenship": "state" in user_citizenships,
                "has_city_citizenship": "city" in user_citizenships or "town" in user_citizenships
            }
            
        except Exception as e:
            print(f"Error getting user citizenship status: {e}")
            return {"user_email": user_email, "error": str(e)}
    
    def search_verification_requests(
        self,
        status: Optional[CitizenshipStatus] = None,
        citizenship_level: Optional[CitizenshipLevel] = None,
        jurisdiction: Optional[str] = None,
        country: Optional[str] = None,
        verifier_email: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search verification requests with filters"""
        
        try:
            results = []
            
            for request_id, request in self.verification_data["verification_requests"].items():
                # Apply filters
                if status and request["status"] != status.value:
                    continue
                
                if citizenship_level and request["citizenship_level"] != citizenship_level.value:
                    continue
                
                if jurisdiction and jurisdiction.lower() not in request["jurisdiction"].lower():
                    continue
                
                if country and country.lower() not in request["country"].lower():
                    continue
                
                if verifier_email:
                    assigned_verifier = request.get("assigned_verifier")
                    if not assigned_verifier or assigned_verifier["verifier_email"] != verifier_email:
                        continue
                
                # Add to results
                result = request.copy()
                result["request_id"] = request_id
                results.append(result)
            
            # Sort by requested date (newest first)
            results.sort(key=lambda x: x["requested_at"], reverse=True)
            
            return results
            
        except Exception as e:
            print(f"Error searching verification requests: {e}")
            return []
    
    def get_verification_statistics(self) -> Dict[str, Any]:
        """Get comprehensive verification statistics"""
        
        try:
            # Use cached stats if available and recent
            current_time = datetime.now()
            if (self.stats_cache and self.stats_cache_time and 
                (current_time - self.stats_cache_time).seconds < 300):  # 5-minute cache
                return self.stats_cache
            
            # Calculate fresh statistics
            base_stats = self.verification_data["verification_statistics"].copy()
            
            # Count by citizenship level
            verifications_by_level = {"country": 0, "state": 0, "city": 0, "town": 0}
            verifications_by_country = {}
            verifications_by_status = {}
            
            for verification in self.verification_data["citizen_verifications"].values():
                level = verification["citizenship_level"]
                country = verification["country"]
                status = verification["status"]
                
                verifications_by_level[level] += 1
                verifications_by_country[country] = verifications_by_country.get(country, 0) + 1
                verifications_by_status[status] = verifications_by_status.get(status, 0) + 1
            
            # Count requests by status
            requests_by_status = {}
            for request in self.verification_data["verification_requests"].values():
                status = request["status"]
                requests_by_status[status] = requests_by_status.get(status, 0) + 1
            
            # Government verifier statistics
            verifier_stats = {
                "total_verifiers": len(self.verification_data["government_verifiers"]),
                "active_verifiers": 0,
                "verifications_completed": 0
            }
            
            for verifier in self.verification_data["government_verifiers"].values():
                if verifier["verifications_completed"] > 0:
                    verifier_stats["active_verifiers"] += 1
                verifier_stats["verifications_completed"] += verifier["verifications_completed"]
            
            # Compile comprehensive stats
            stats = {
                **base_stats,
                "verifications_by_level": verifications_by_level,
                "verifications_by_country": verifications_by_country,
                "verifications_by_status": verifications_by_status,
                "requests_by_status": requests_by_status,
                "government_verifiers": verifier_stats,
                "system_health": {
                    "database_size": len(self.verification_data["citizen_verifications"]),
                    "pending_queue_size": requests_by_status.get("pending", 0),
                    "verification_success_rate": (
                        (base_stats["verified_citizens"] / base_stats["total_requests"] * 100)
                        if base_stats["total_requests"] > 0 else 0
                    )
                }
            }
            
            # Cache the results
            self.stats_cache = stats
            self.stats_cache_time = current_time
            
            return stats
            
        except Exception as e:
            print(f"Error calculating verification statistics: {e}")
            return {"error": str(e)}
    
    def _determine_verification_authority(
        self,
        citizenship_level: str,
        verifier_title: str,
        verifier_jurisdiction: str
    ) -> str:
        """Determine verification authority based on level and verifier"""
        
        title_lower = verifier_title.lower()
        
        if citizenship_level == "country":
            if any(word in title_lower for word in ["president", "prime minister", "chancellor", "secretary", "minister"]):
                return "federal_authority"
            elif any(word in title_lower for word in ["ambassador", "consul", "embassy"]):
                return "diplomatic_authority"
        
        elif citizenship_level == "state":
            if any(word in title_lower for word in ["governor", "premier", "secretary of state"]):
                return "state_authority"
            elif any(word in title_lower for word in ["legislature", "senator", "representative"]):
                return "legislative_authority"
        
        elif citizenship_level in ["city", "town"]:
            if any(word in title_lower for word in ["mayor", "city manager", "town", "municipal"]):
                return "municipal_authority"
            elif "clerk" in title_lower:
                return "administrative_authority"
        
        return "general_authority"


# Demo functions for testing
def demo_citizen_verification():
    """Demonstrate citizen verification system"""
    
    print("🏛️ CITIZEN VERIFICATION SYSTEM DEMO")
    print("=" * 50)
    print("Real-world government officials verify platform users as citizens")
    print("Hierarchical verification: Country → State → City/Town")
    print("=" * 50)
    
    # Initialize system
    manager = CitizenVerificationManager()
    
    # Demo verification request
    print("\n📝 REQUESTING CITIZENSHIP VERIFICATION")
    print("-" * 40)
    
    documents = [
        {"type": "passport", "document_id": "US123456789", "issued_date": "2020-01-15"},
        {"type": "birth_certificate", "state": "California", "county": "Los Angeles"},
        {"type": "voter_registration", "precinct": "LA-001", "registered_date": "2018-11-01"}
    ]
    
    success, message = manager.request_citizenship_verification(
        user_email="citizen@example.com",
        citizenship_level=CitizenshipLevel.COUNTRY,
        jurisdiction="United States",
        country="United States",
        verification_documents=documents,
        additional_info={"birth_city": "Los Angeles", "residence_years": 25}
    )
    
    print(f"Request result: {message}")
    
    # Get statistics
    print("\n📊 VERIFICATION STATISTICS")
    print("-" * 30)
    
    stats = manager.get_verification_statistics()
    print(f"Total requests: {stats.get('total_requests', 0)}")
    print(f"Verified citizens: {stats.get('verified_citizens', 0)}")
    print(f"Pending verifications: {stats.get('pending_verifications', 0)}")
    
    return manager


if __name__ == "__main__":
    demo_citizen_verification()
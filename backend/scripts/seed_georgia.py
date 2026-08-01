"""Seed Georgia Film Tax Credit program."""
import sys, os, uuid, json, logging
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.db.session import SessionLocal
from app.models.jurisdiction import Jurisdiction
from app.models.program import Program
logger = logging.getLogger(__name__)

GEORGIA_RULES = {
    "program_name": "Georgia Film Tax Credit",
    "jurisdiction": "Georgia",
    "version": "2025.01",
    "base_credit_rate": 0.20,
    "bonus_conditions": [
        {
            "id": "promotional_logo",
            "name": "Georgia Promotional Logo",
            "rate": 0.10,
            "condition": "logo_included == True",
            "description": "Additional 10% for including the Georgia state logo in credits"
        }
    ],
    "qualified_expenditure_categories": [
        "above_the_line", "below_the_line", "post_production",
        "visual_effects", "music_production", "transportation", "lodging"
    ],
    "minimum_requirements": [
        {
            "id": "min_spend",
            "rule": "qualified_spend >= 500000",
            "message": "Minimum qualified spend of $500,000 required",
            "severity": "blocking"
        },
        {
            "id": "georgia_filming",
            "rule": "filming_location contains 'Georgia'",
            "message": "At least 50% of principal photography must occur in Georgia",
            "severity": "blocking"
        }
    ],
    "exclusions": [
        {
            "category": "music_licensing",
            "condition": "licensor_resident_georgia == False",
            "message": "Music licensing payments to non-Georgia residents are excluded"
        }
    ],
    "local_hire_bonus": {
        "rate": 0.05,
        "threshold": 0.15,
        "description": "Additional 5% when Georgia resident crew exceeds 15% of total crew",
        "condition": "local_hire_percentage >= 0.15"
    },
    "diversity_bonus": {
        "rate": 0.02,
        "threshold": 0.20,
        "description": "Additional 2% for diversity in key creative roles",
        "condition": "diversity_score >= 0.20"
    },
    "application_deadlines": {
        "initial_application": {
            "timing": "within 90 days of principal photography commencement",
            "message": "Initial application must be filed within 90 days"
        },
        "final_claim": {
            "timing": "within 3 years of completion",
            "message": "Final claim must be submitted within 3 years"
        }
    },
    "checklist": [
        {"item": "Register with Georgia Film Office", "required": True},
        {"item": "Submit GEIPA form", "required": True},
        {"item": "Provide affidavit of Georgia spend", "required": True},
        {"item": "Confirm promotional logo inclusion", "required": False, "condition": "logo_included == True"}
    ],
    "transferability": {
        "allowed": True,
        "fee_market_range": "0.88 - 0.94 per dollar",
        "notes": "Credits are transferable; typically sold at 88-94% of face value"
    },
    "sunset_date": "2028-12-31"
}

def seed_georgia():
    db = SessionLocal()
    try:
        georgia = db.query(Jurisdiction).filter(Jurisdiction.name == "Georgia").first()
        if not georgia:
            logger.error("Georgia jurisdiction not found. Run add_georgia first.")
            return None
        
        existing = db.query(Program).filter(
            Program.name == "Georgia Film Tax Credit",
            Program.jurisdiction_id == georgia.id
        ).first()
        
        if existing:
            existing.rules = json.dumps(GEORGIA_RULES)
            existing.updated_at = datetime.utcnow()
            logger.info(f"Updated existing program: {existing.id}")
            return existing.id
        else:
            program = Program(
                id=str(uuid.uuid4()),
                jurisdiction_id=georgia.id,
                name="Georgia Film Tax Credit",
                description="Georgia's film tax credit program offers 20% base credit with bonuses.",
                rules=json.dumps(GEORGIA_RULES),
                active=True
            )
            db.add(program)
            db.commit()
            logger.info(f"Created new program: {program.id}")
            return program.id
            
    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_georgia()

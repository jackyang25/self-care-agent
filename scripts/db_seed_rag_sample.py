"""seed sample healthcare documents for RAG testing."""

import sys
from pathlib import Path

# add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.rag import store_document


def seed_sample_documents():
    """seed sample healthcare documents."""
    print("seeding sample healthcare documents...")
    
    documents = [
        {
            "title": "Fever Management Guidelines",
            "content": """Fever is a common symptom that indicates the body is fighting an infection. 
            
For adults with fever:
- Rest and stay hydrated by drinking plenty of fluids
- Take acetaminophen (paracetamol) or ibuprofen to reduce fever and discomfort
- Monitor temperature regularly
- Seek medical attention if fever persists for more than 3 days, exceeds 39.4°C (103°F), or is accompanied by severe symptoms like difficulty breathing, chest pain, or confusion

For children with fever:
- Ensure adequate fluid intake
- Use age-appropriate fever reducers (acetaminophen or ibuprofen) following dosage guidelines
- Seek immediate medical attention if child is under 3 months with any fever, or if fever is above 40°C (104°F)
- Watch for signs of dehydration or unusual behavior""",
            "content_type": "guideline",
            "metadata": {"category": "symptom_management", "condition": "fever"},
        },
        {
            "title": "Chest Pain Red Flags",
            "content": """Chest pain can be a sign of serious medical conditions and requires immediate evaluation in certain situations.

Red flag symptoms requiring immediate emergency care:
- Severe chest pain that radiates to arm, neck, or jaw
- Chest pain accompanied by shortness of breath, sweating, or nausea
- Chest pain in someone with known heart disease or risk factors
- Chest pain that worsens with exertion
- Chest pain with dizziness or fainting

If experiencing any red flag symptoms, seek emergency medical care immediately. Do not delay.

For non-urgent chest pain:
- Rest and avoid activities that trigger the pain
- Monitor symptoms and note any changes
- Consider evaluation within 24-48 hours if symptoms persist or worsen""",
            "content_type": "protocol",
            "metadata": {"category": "emergency", "condition": "chest_pain"},
        },
        {
            "title": "Diabetes Self-Care Basics",
            "content": """Diabetes management requires consistent self-care practices.

Key self-care components:
1. Blood glucose monitoring: Check levels as recommended by healthcare provider
2. Medication adherence: Take prescribed medications consistently
3. Healthy eating: Follow a balanced diet with controlled carbohydrate intake
4. Regular physical activity: Aim for at least 150 minutes of moderate exercise per week
5. Foot care: Inspect feet daily for cuts, sores, or changes
6. Regular healthcare visits: Maintain scheduled appointments with diabetes care team

Warning signs requiring immediate attention:
- Very high or very low blood glucose levels
- Signs of diabetic ketoacidosis (excessive thirst, frequent urination, nausea, confusion)
- Foot wounds that don't heal
- Vision changes

Always consult with healthcare providers before making significant changes to diabetes management.""",
            "content_type": "guideline",
            "metadata": {"category": "chronic_disease", "condition": "diabetes"},
        },
        {
            "title": "Hypertension Management",
            "content": """Hypertension (high blood pressure) is a common condition that requires ongoing management.

Lifestyle modifications:
- Reduce sodium intake to less than 2,300 mg per day
- Follow DASH (Dietary Approaches to Stop Hypertension) diet principles
- Engage in regular aerobic exercise (at least 30 minutes most days)
- Maintain healthy weight
- Limit alcohol consumption
- Manage stress through relaxation techniques

Medication management:
- Take prescribed blood pressure medications consistently
- Monitor blood pressure at home as recommended
- Report side effects or concerns to healthcare provider
- Do not stop medications without medical guidance

Target blood pressure goals vary by individual circumstances and should be discussed with healthcare provider. Regular monitoring and follow-up are essential.""",
            "content_type": "guideline",
            "metadata": {"category": "chronic_disease", "condition": "hypertension"},
        },
        {
            "title": "When to Seek Emergency Care",
            "content": """Certain symptoms require immediate emergency medical attention and should not be delayed.

Seek emergency care immediately for:
- Chest pain or pressure, especially with radiation to arm or jaw
- Severe difficulty breathing or shortness of breath
- Signs of stroke (sudden weakness, facial drooping, speech difficulty)
- Severe allergic reactions (difficulty breathing, swelling, hives)
- Loss of consciousness or severe confusion
- Severe trauma or injury
- Suspected poisoning or overdose
- Severe burns
- Signs of severe dehydration (no urination, extreme thirst, confusion)

For these situations, call emergency services immediately. Do not attempt to drive yourself to the hospital if experiencing these symptoms.

When in doubt about whether a situation is an emergency, err on the side of caution and seek immediate medical evaluation.""",
            "content_type": "protocol",
            "metadata": {"category": "emergency", "condition": "general"},
        },
    ]
    
    stored_count = 0
    for doc in documents:
        try:
            document_id = store_document(
                title=doc["title"],
                content=doc["content"],
                content_type=doc["content_type"],
                metadata=doc["metadata"],
            )
            print(f"  ✓ stored: {doc['title']} ({document_id[:8]}...)")
            stored_count += 1
        except Exception as e:
            print(f"  ✗ error storing {doc['title']}: {e}")
    
    print(f"✓ seeded {stored_count} sample documents")


if __name__ == "__main__":
    seed_sample_documents()


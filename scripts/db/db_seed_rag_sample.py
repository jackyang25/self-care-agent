"""seed sample healthcare documents for RAG testing."""

import sys
from pathlib import Path

# add project root to path (scripts/db/ -> scripts/ -> root/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.services.rag import store_document


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
        {
            "title": "Headache Management",
            "content": """Headaches are common and can have various causes. Most headaches are not serious, but some require medical attention.

Common headache types and management:
- Tension headaches: Often related to stress, poor posture, or fatigue. Rest, hydration, and over-the-counter pain relievers (acetaminophen or ibuprofen) may help
- Migraine headaches: Can be severe with sensitivity to light/sound. Rest in a dark, quiet room. Some people benefit from prescription medications
- Sinus headaches: Often associated with congestion. Treat underlying congestion with decongestants or saline nasal sprays

Self-care for headaches:
- Rest in a quiet, dark room
- Apply cold or warm compress to forehead or neck
- Stay hydrated
- Practice relaxation techniques
- Maintain regular sleep schedule
- Consider over-the-counter pain relievers as directed

Seek medical attention if:
- Headache is sudden and severe (thunderclap headache)
- Headache follows head injury
- Headache is accompanied by fever, stiff neck, confusion, or vision changes
- Headache is persistent and worsening
- Headache is different from usual pattern""",
            "content_type": "guideline",
            "metadata": {"category": "symptom_management", "condition": "headache"},
        },
        {
            "title": "Nausea and Vomiting Management",
            "content": """Nausea and vomiting can result from various causes including infections, motion sickness, pregnancy, medications, or underlying medical conditions.

Self-care strategies:
- Stay hydrated with small, frequent sips of clear fluids (water, electrolyte solutions, clear broths)
- Avoid solid foods until vomiting subsides
- Once able to tolerate fluids, try bland foods (crackers, toast, rice, bananas)
- Rest and avoid sudden movements
- Avoid strong odors or triggers
- Consider ginger (tea, candies, or supplements) which may help with nausea
- Use over-the-counter anti-nausea medications if appropriate and not contraindicated

For motion sickness:
- Focus on horizon or stationary object
- Avoid reading or screens while in motion
- Consider over-the-counter motion sickness medications before travel

Seek medical attention if:
- Vomiting persists for more than 24-48 hours
- Unable to keep fluids down
- Signs of dehydration (dry mouth, decreased urination, dizziness)
- Vomiting blood or dark material
- Severe abdominal pain
- High fever
- Head injury preceded vomiting
- Suspected poisoning""",
            "content_type": "guideline",
            "metadata": {"category": "symptom_management", "condition": "nausea_vomiting"},
        },
        {
            "title": "Common Cold and Flu Management",
            "content": """The common cold and influenza (flu) are viral respiratory infections. While similar, flu symptoms are typically more severe.

Common symptoms:
- Runny or stuffy nose
- Sneezing
- Sore throat
- Cough
- Mild body aches
- Fatigue
- Low-grade fever (more common with flu)

Self-care for cold and flu:
- Rest and allow your body to recover
- Stay hydrated with water, herbal teas, or clear broths
- Use saline nasal sprays or rinses for congestion
- Gargle with warm salt water for sore throat
- Use humidifier or steam to ease breathing
- Over-the-counter medications can help with symptoms (decongestants, pain relievers, cough suppressants)
- Wash hands frequently to prevent spread

When to seek medical care:
- Symptoms persist beyond 10 days
- High fever (above 38.9°C or 102°F) that doesn't respond to treatment
- Severe headache or body aches
- Difficulty breathing or chest pain
- Severe sore throat with difficulty swallowing
- Persistent cough with colored mucus
- Symptoms improve then worsen (possible secondary infection)

Prevention:
- Annual flu vaccination
- Frequent handwashing
- Avoid close contact with sick individuals
- Cover coughs and sneezes
- Stay home when sick""",
            "content_type": "guideline",
            "metadata": {"category": "symptom_management", "condition": "cold_flu"},
        },
        {
            "title": "Pregnancy Care Basics",
            "content": """Pregnancy requires special attention to health and wellness for both the pregnant person and developing baby.

Prenatal care essentials:
- Regular prenatal visits with healthcare provider
- Take prenatal vitamins with folic acid as recommended
- Maintain balanced nutrition with increased caloric needs
- Stay hydrated
- Get adequate rest and sleep
- Engage in safe, moderate exercise as approved by healthcare provider

Important considerations:
- Avoid alcohol, tobacco, and illicit drugs
- Discuss all medications (prescription and over-the-counter) with healthcare provider
- Avoid certain foods (raw fish, unpasteurized dairy, deli meats, high-mercury fish)
- Limit caffeine intake
- Practice good hygiene to prevent infections

Common pregnancy symptoms and when to seek care:
- Morning sickness: Usually normal, but seek care if severe or causing dehydration
- Fatigue: Normal, but ensure adequate rest
- Back pain: Common, but discuss persistent or severe pain with provider
- Swelling: Some is normal, but sudden or severe swelling needs evaluation

Seek immediate medical attention for:
- Vaginal bleeding
- Severe abdominal pain
- Signs of preterm labor (regular contractions, water breaking)
- Severe headaches or vision changes
- Decreased fetal movement (in later pregnancy)
- Signs of preeclampsia (swelling, high blood pressure, protein in urine)""",
            "content_type": "guideline",
            "metadata": {"category": "preventive_care", "condition": "pregnancy"},
        },
        {
            "title": "Wound Care and Infection Prevention",
            "content": """Proper wound care helps prevent infection and promotes healing.

Basic wound care steps:
1. Stop bleeding: Apply gentle pressure with clean cloth or bandage
2. Clean the wound: Rinse with clean water. Use mild soap around the wound (avoid getting soap in the wound)
3. Apply antibiotic ointment if appropriate (check for allergies)
4. Cover with sterile bandage or dressing
5. Keep wound clean and dry
6. Change bandage daily or when it becomes wet or dirty

Signs of wound infection:
- Increased redness, swelling, or warmth around wound
- Pus or drainage from wound
- Worsening pain
- Red streaks extending from wound
- Fever
- Swollen lymph nodes near wound

When to seek medical care:
- Deep or large wounds
- Wounds that won't stop bleeding
- Wounds with embedded debris that can't be removed
- Signs of infection
- Wounds from animal or human bites
- Wounds from rusty objects (may need tetanus shot)
- Wounds that don't show signs of healing after several days

Prevention:
- Keep wounds covered until healed
- Don't pick at scabs
- Maintain good hygiene
- Ensure tetanus vaccination is up to date""",
            "content_type": "guideline",
            "metadata": {"category": "symptom_management", "condition": "wound_care"},
        },
        {
            "title": "Mental Health and Stress Management",
            "content": """Mental health is an important component of overall well-being. Managing stress and recognizing when to seek help is crucial.

Stress management techniques:
- Regular physical activity and exercise
- Adequate sleep (7-9 hours for adults)
- Healthy eating habits
- Relaxation techniques (deep breathing, meditation, yoga)
- Social connections and support
- Time management and setting priorities
- Limiting alcohol and avoiding substance use
- Engaging in hobbies and activities you enjoy

Signs that may indicate need for professional support:
- Persistent feelings of sadness, anxiety, or hopelessness
- Changes in sleep or appetite
- Difficulty concentrating or making decisions
- Loss of interest in activities
- Irritability or mood swings
- Thoughts of self-harm or suicide
- Difficulty functioning in daily life
- Excessive worry or fear

When to seek immediate help:
- Thoughts of suicide or self-harm
- Severe anxiety or panic attacks
- Inability to care for yourself
- Psychotic symptoms (hallucinations, delusions)

Resources:
- Talk to healthcare provider about mental health concerns
- Consider therapy or counseling
- Reach out to mental health crisis lines if in crisis
- Connect with support groups
- Practice self-care and stress reduction techniques regularly""",
            "content_type": "guideline",
            "metadata": {"category": "preventive_care", "condition": "mental_health"},
        },
        {
            "title": "Medication Safety Guidelines",
            "content": """Safe medication use is essential for effective treatment and preventing harm.

Key medication safety practices:
- Take medications exactly as prescribed by healthcare provider
- Read and follow all medication labels and instructions
- Never share prescription medications with others
- Store medications properly (cool, dry place, out of reach of children)
- Check expiration dates and dispose of expired medications safely
- Keep a current list of all medications (prescription, over-the-counter, supplements)
- Inform all healthcare providers about all medications you take
- Ask questions if you don't understand medication instructions

Important considerations:
- Some medications interact with foods, alcohol, or other medications
- Some medications should not be taken during pregnancy or breastfeeding
- Follow timing instructions (with food, on empty stomach, etc.)
- Complete full course of antibiotics even if feeling better
- Don't stop medications abruptly without medical guidance

Common medication mistakes to avoid:
- Taking incorrect dose
- Missing doses or doubling up
- Mixing medications without checking for interactions
- Using medications prescribed for someone else
- Crushing or splitting medications without checking if safe

When to contact healthcare provider:
- Experiencing side effects or adverse reactions
- Medication doesn't seem to be working
- Questions about medication use
- Need to stop or change medication
- Starting new medications or supplements""",
            "content_type": "guideline",
            "metadata": {"category": "preventive_care", "condition": "medication_safety"},
        },
        {
            "title": "Nutrition and Healthy Eating Basics",
            "content": """Good nutrition is fundamental to health and well-being. A balanced diet provides essential nutrients for body function and disease prevention.

Basic nutrition principles:
- Eat variety of foods from all food groups
- Include plenty of fruits and vegetables (aim for variety of colors)
- Choose whole grains over refined grains
- Include lean proteins (poultry, fish, beans, legumes, nuts)
- Limit processed foods, added sugars, and saturated fats
- Stay hydrated with water as primary beverage
- Practice portion control

Key nutrients:
- Protein: Essential for tissue repair and muscle maintenance
- Carbohydrates: Primary energy source (choose complex carbs)
- Fats: Necessary for hormone production and nutrient absorption (choose healthy fats)
- Vitamins and minerals: Support various body functions
- Fiber: Promotes digestive health

Special considerations:
- Pregnant or breastfeeding: Increased nutritional needs
- Chronic conditions: May require dietary modifications (diabetes, hypertension, kidney disease)
- Food allergies or intolerances: Avoid trigger foods
- Age-specific needs: Children, elderly may have different requirements

When to consult healthcare provider or dietitian:
- Need help with meal planning
- Managing chronic conditions through diet
- Significant weight changes
- Food allergies or intolerances
- Eating disorders or disordered eating patterns
- Questions about supplements or special diets""",
            "content_type": "guideline",
            "metadata": {"category": "preventive_care", "condition": "nutrition"},
        },
        {
            "title": "Sleep Hygiene and Healthy Sleep",
            "content": """Quality sleep is essential for physical and mental health. Most adults need 7-9 hours of sleep per night.

Good sleep hygiene practices:
- Maintain consistent sleep schedule (even on weekends)
- Create comfortable sleep environment (cool, dark, quiet)
- Establish relaxing bedtime routine
- Avoid screens (phones, tablets, TV) 1-2 hours before bed
- Limit caffeine, especially in afternoon and evening
- Avoid large meals, alcohol, and nicotine close to bedtime
- Get regular exercise, but not too close to bedtime
- Use bed primarily for sleep (not work or entertainment)
- If unable to sleep after 20 minutes, get up and do something relaxing

Common sleep problems:
- Insomnia: Difficulty falling or staying asleep
- Sleep apnea: Breathing interruptions during sleep (may require medical evaluation)
- Restless leg syndrome: Uncomfortable sensations in legs
- Circadian rhythm disorders: Sleep-wake cycle disruptions

When to seek medical help:
- Persistent difficulty sleeping despite good sleep hygiene
- Excessive daytime sleepiness affecting daily function
- Loud snoring with breathing pauses (possible sleep apnea)
- Restless sleep or frequent waking
- Sleep problems affecting mood, concentration, or health

Tips for better sleep:
- Limit naps or keep them short (20-30 minutes) and early in day
- Manage stress and anxiety
- Address underlying health conditions that may affect sleep
- Consider relaxation techniques or meditation
- Avoid clock-watching if having trouble sleeping""",
            "content_type": "guideline",
            "metadata": {"category": "preventive_care", "condition": "sleep"},
        },
        {
            "title": "Dehydration Prevention and Management",
            "content": """Dehydration occurs when the body loses more fluids than it takes in. Proper hydration is essential for health.

Signs of mild to moderate dehydration:
- Thirst
- Dry mouth and lips
- Decreased urination or dark yellow urine
- Fatigue or weakness
- Dizziness or lightheadedness
- Headache

Signs of severe dehydration (seek immediate medical care):
- Very dark urine or no urination
- Extreme thirst
- Confusion or irritability
- Rapid heartbeat or breathing
- Sunken eyes
- Fainting or loss of consciousness

Prevention and treatment:
- Drink water regularly throughout the day
- Increase fluid intake during hot weather, exercise, or illness
- Include water-rich foods (fruits, vegetables) in diet
- For mild dehydration: Drink water or oral rehydration solutions
- For moderate dehydration: May need electrolyte solutions
- Avoid excessive caffeine or alcohol which can contribute to dehydration

Daily fluid needs:
- General guideline: 8 cups (2 liters) per day, but needs vary
- Increased needs with: Exercise, hot weather, illness, pregnancy, breastfeeding
- Listen to your body's thirst signals
- Monitor urine color (pale yellow indicates good hydration)

Special situations:
- Exercise: Drink water before, during, and after exercise
- Illness with fever, vomiting, or diarrhea: Increase fluid intake, may need electrolyte solutions
- Hot weather: Increase fluid intake, avoid excessive sun exposure
- Elderly: May have reduced thirst sensation, need to be mindful of hydration

When to seek medical care:
- Signs of severe dehydration
- Unable to keep fluids down
- Persistent vomiting or diarrhea
- Signs of heat exhaustion or heat stroke
- Underlying medical conditions affecting fluid balance""",
            "content_type": "guideline",
            "metadata": {"category": "preventive_care", "condition": "dehydration"},
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


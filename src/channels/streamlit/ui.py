"""streamlit UI components and configuration screens."""

from datetime import date

import streamlit as st


def initialize_session_state() -> None:
    """initialize session state with LMIC-focused defaults."""
    defaults = {
        # socio-technical context (LMIC-focused)
        "whatsapp_id": "+27834567890",
        "literacy_level": "intermediate",
        "primary_language": "en",
        "network_type": "high-speed",
        "geospatial_tag": "cape-town-khayelitsha",
        "social_context": "no-refrigeration",
        # Patient Summary (IPS)
        "emr_patient_id": "PT-ZA-001234",
        "patient_age": 28,
        "patient_gender": "female",
        "active_diagnoses": "",
        "current_medications": "",
        "allergies": "",
        "latest_vitals": "",
        # behavioral health
        "adherence_score": 85,
        "refill_due_date": date(2026, 2, 15),
        # chat state
        "messages": [],
        "processing": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_demo_context() -> None:
    """render socio-technical context configuration (LMIC-focused)."""
    # row 1: identity, socio-tech, linguistics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.session_state.whatsapp_id = st.text_input(
            "WhatsApp ID (Identity)",
            value=st.session_state.whatsapp_id,
            key="input_whatsapp_id",
            help="**Identity Assurance**: Phone number used for WhatsApp communication. In production, verified via 3-step handshake: (1) User initiates chat, (2) Agent sends OTP to phone on file at clinic, (3) Correct OTP binds WhatsApp ID to Patient UUID in EMR.\n\n**Shared Phone Exception (LMIC)**: Database allows One-to-Many mapping. Example: A mother uses her WhatsApp (+27123456789) for herself, her husband, and her child. Agent asks: \"Who are you checking for today: (A) Yourself, (B) Kofi, or (C) Baby Zayne?\" before fetching history."
        )

    with col2:
        literacy_options = ["proficient", "intermediate", "basic", "below-basic"]
        literacy_display = {
            "proficient": "Proficient (University/Clinical)",
            "intermediate": "Intermediate (High School)",
            "basic": "Basic (Primary School)",
            "below-basic": "Below Basic (Narrative/Concrete)"
        }
        st.session_state.literacy_level = st.selectbox(
            "Literacy Level (Socio-Tech)",
            options=literacy_options,
            format_func=lambda x: literacy_display[x],
            index=literacy_options.index(st.session_state.literacy_level) if st.session_state.literacy_level in literacy_options else 0,
            key="input_literacy_level",
            help="**Adaptive Communication**: Proficient uses technical terms & stats (\"hypertension\"); Intermediate uses plain language; Basic uses short sentences (<15 words, \"high blood pressure\" not \"hypertension\"); Below Basic uses action-only narrative (\"The Pill\", \"The Pain\") with emoji visual anchors 💊☀️"
        )

    with col3:
        language_options = ["en", "fr", "zu", "ny", "wo", "sw", "xh"]
        language_display = {
            "en": "English",
            "fr": "French (Senegal)",
            "zu": "Zulu (South Africa)",
            "ny": "Chichewa (Malawi)",
            "wo": "Wolof (Senegal)",
            "sw": "Swahili (East Africa)",
            "xh": "Xhosa (South Africa)"
        }
        lang_index = language_options.index(st.session_state.primary_language) if st.session_state.primary_language in language_options else 0
        st.session_state.primary_language = st.selectbox(
            "Primary Language (Linguistics)",
            options=language_options,
            format_func=lambda x: language_display[x],
            index=lang_index,
            key="input_primary_language",
            help="**Language Adaptation**: Sets the LLM system prompt to communicate in the patient's primary language and dialect. Supports English, French (Senegal), Wolof, Chichewa (Malawi), Zulu, Xhosa, and Swahili. Critical for LMIC contexts where multiple languages coexist."
        )

    # row 2: connectivity, location, determinants
    col1, col2, col3 = st.columns(3)

    with col1:
        network_options = ["high-speed", "unstable", "edge/2g"]
        network_display = {
            "high-speed": "High Speed (4G/5G)",
            "unstable": "Unstable Connection",
            "edge/2g": "Edge/2G (No Media)"
        }
        st.session_state.network_type = st.selectbox(
            "Network Type (Connectivity)",
            options=network_options,
            format_func=lambda x: network_display[x],
            index=network_options.index(st.session_state.network_type),
            key="input_network_type",
            help="**Bandwidth Optimization**: On Edge/2G networks, agent avoids sending images, videos, or large files. Uses text-only responses with emojis. On Unstable connections, sends compressed assets and provides download links instead of inline media. On High-speed, full multimedia responses are enabled."
        )

    with col2:
        location_options = [
            "cape-town-khayelitsha",
            "johannesburg-soweto",
            "lilongwe-area-25",
            "blantyre-ndirande",
            "dakar-pikine",
            "dakar-guediawaye",
            "nairobi-kibera",
            "lagos-makoko"
        ]
        location_display = {
            "cape-town-khayelitsha": "Cape Town - Khayelitsha (ZA)",
            "johannesburg-soweto": "Johannesburg - Soweto (ZA)",
            "lilongwe-area-25": "Lilongwe - Area 25 (MW)",
            "blantyre-ndirande": "Blantyre - Ndirande (MW)",
            "dakar-pikine": "Dakar - Pikine (SN)",
            "dakar-guediawaye": "Dakar - Guediawaye (SN)",
            "nairobi-kibera": "Nairobi - Kibera (KE)",
            "lagos-makoko": "Lagos - Makoko (NG)"
        }
        st.session_state.geospatial_tag = st.selectbox(
            "Location (Geospatial)",
            options=location_options,
            format_func=lambda x: location_display[x],
            index=location_options.index(st.session_state.geospatial_tag) if st.session_state.geospatial_tag in location_options else 0,
            key="input_geospatial_tag",
            help="**Proximity Intelligence**: Calculates 'Time to Clinic' based on patient location. Agent can recommend nearest health facility, estimate travel time via public transport, and suggest alternate sites if primary clinic is far. Also enables region-specific health alerts (e.g., malaria risk in specific neighborhoods)."
        )

    with col3:
        social_options = [
            "no-refrigeration",
            "daily-wage-worker",
            "single-parent",
            "no-running-water",
            "informal-housing"
        ]
        social_display = {
            "no-refrigeration": "No Refrigeration",
            "daily-wage-worker": "Daily Wage Worker",
            "single-parent": "Single Parent",
            "no-running-water": "No Running Water",
            "informal-housing": "Informal Housing"
        }
        st.session_state.social_context = st.selectbox(
            "Social Context (Determinants)",
            options=social_options,
            format_func=lambda x: social_display[x],
            index=social_options.index(st.session_state.social_context),
            key="input_social_context",
            help="**Social Determinants of Health (SDOH)**: Personalizes care based on living conditions. 'No Refrigeration' → non-refrigerated meds. 'Daily Wage Worker' → evening clinic hours. 'Single Parent' → simplified schedules. 'No Running Water' → adapted hygiene instructions.\n\n**How Agent Collects SDOH** (3 methods): (1) **Conversational Extraction**: NLP extracts facts from chat (user says \"can't keep medicine cold\" → agent tags [REFRIGERATION: NONE]). (2) **Self-Reported Profile**: Onboarding questions (\"How far is nearest clinic?\", \"Reliable transport?\"). (3) **Geospatial Lookup**: Cross-references location with National Health Map to infer water shortage, pharmacy distance (20km), etc."
        )


def render_patient_summary() -> None:
    """render International Patient Summary (IPS) configuration.
    
    IPS is a curated, FHIR-standardized extract of critical clinical facts
    designed for cross-system sharing and AI clinical reasoning.
    """
    # row 1: patient id and demographics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.session_state.emr_patient_id = st.text_input(
            "Patient ID (IPS)",
            value=st.session_state.get("emr_patient_id", "PT-ZA-001234"),
            key="input_emr_patient_id",
            help="**International Patient Summary (IPS)**: Unique patient identifier following ISO/EN 17269 standard by HL7. This is NOT raw EMR data—it's a curated, FHIR-standardized extract designed for interoperability. IPS represents data the patient carries (mobile-ready, patient-centric), not data 'owned' by a hospital. Enables safe AI reasoning across systems."
        )

    with col2:
        st.session_state.patient_age = st.number_input(
            "Age (Demographics)",
            min_value=0,
            max_value=120,
            value=st.session_state.get("patient_age", 28),
            key="input_patient_age",
            help="**Dosage & Safety**: Crucial for pediatric vs adult dosing and maternal health triggers. Affects medication recommendations and screening protocols."
        )

    with col3:
        gender_options = ["male", "female", "other"]
        gender_display = {"male": "Male", "female": "Female", "other": "Other"}
        st.session_state.patient_gender = st.selectbox(
            "Gender (Demographics)",
            options=gender_options,
            format_func=lambda x: gender_display[x],
            index=gender_options.index(st.session_state.get("patient_gender", "female")),
            key="input_patient_gender",
            help="**Clinical Context**: Essential for gender-specific screening (cervical/prostate cancer), pregnancy considerations, and hormone-related conditions."
        )

    # row 2: conditions and medications
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.active_diagnoses = st.text_area(
            "Active Diagnoses (Conditions)",
            value=st.session_state.get("active_diagnoses", ""),
            placeholder="e.g., Type 2 Diabetes, HIV, Hypertension",
            key="input_active_diagnoses",
            help="**Safety Guardrails**: List of chronic conditions (Diabetes, HIV, Asthma, etc.). Prevents AI from suggesting contraindicated advice. Example: Won't recommend high-sugar foods to diabetic patients."
        )

    with col2:
        st.session_state.current_medications = st.text_area(
            "Current Medications",
            value=st.session_state.get("current_medications", ""),
            placeholder="e.g., Metformin 500mg, Lisinopril 10mg",
            key="input_current_medications",
            help="**Drug-Drug Interaction Checks**: Used to prevent dangerous combinations. Example: \"Don't take ibuprofen with your current blood thinner (Warfarin)\"."
        )

    # row 3: allergies and vitals
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.allergies = st.text_area(
            "Allergies (Safety)",
            value=st.session_state.get("allergies", ""),
            placeholder="e.g., Penicillin, Sulfa drugs, Peanuts",
            key="input_allergies",
            help="**Ultimate Safety Guardrail**: Critical for preventing life-threatening reactions. Agent will never recommend penicillin-based antibiotics if allergy is documented."
        )

    with col2:
        st.session_state.latest_vitals = st.text_area(
            "Latest Vitals (Observations)",
            value=st.session_state.get("latest_vitals", ""),
            placeholder="e.g., BP: 140/90, Weight: 75kg, Glucose: 180mg/dL",
            key="input_latest_vitals",
            help="**Personalized Monitoring**: Last recorded vitals (BP, Weight, Glucose). Enables contextual responses like \"I see your sugar was high last week - let's discuss your diet\" or \"Your blood pressure needs attention\"."
        )

    # row 4: behavioral health tracking
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.adherence_score = st.slider(
            "Adherence Score (Behavioral)",
            min_value=0,
            max_value=100,
            value=st.session_state.get("adherence_score", 85),
            key="input_adherence_score",
            help="**Medication Adherence**: Percentage of prescribed doses taken on time. If low (<70%), AI prioritizes \"Habit Building\" strategies and reminder systems over new clinical advice. Example: At 50% adherence, agent focuses on \"Why are you missing doses?\" before adding new medications."
        )
        st.caption(f"{st.session_state.adherence_score}%")

    with col2:
        st.session_state.refill_due_date = st.date_input(
            "Refill Due Date (Behavioral)",
            value=st.session_state.get("refill_due_date", None),
            key="input_refill_due_date",
            help="**Proactive Medication Management**: Triggers \"Nudge\" conversations when refill is approaching. Example: \"I see your Metformin is running low in 3 days - do you have a plan to get more?\" Prevents treatment gaps due to missed refills."
        )


def render_chat_interface() -> None:
    """render chat interface."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # display tools and sources for assistant messages
            if message["role"] == "assistant":
                tools = message.get("tools")
                sources = message.get("sources")

                if tools:
                    st.caption(f"Tools: {', '.join(tools)}")

                if sources:
                    with st.expander("Sources", expanded=False):
                        for i, source in enumerate(sources, 1):
                            similarity = int(source.get("similarity", 0) * 100)
                            content_type = source.get("content_type", "")
                            type_badge = f"`{content_type}`" if content_type else ""
                            title = source.get("title", "Unknown")

                            st.markdown(
                                f"**{i}. {title}** {type_badge} *({similarity}% match)*"
                            )


def launch_app(handler) -> None:
    """launch the streamlit application."""
    st.set_page_config(
        page_title="AI Self-Care Agent Demo",
        layout="wide",
    )

    initialize_session_state()

    st.markdown("<h1 style='text-align: center;'>AI Self-Care Agent Demo</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # two-column layout: configuration on left, chat on right
    config_col, chat_col = st.columns([1, 1])

    with config_col:
        st.subheader("Configuration")
        
        # create a container with fixed height to match chat column
        config_container = st.container(height=600)
        with config_container:
            with st.expander("Socio-Technical Context", expanded=False):
                render_demo_context()

            with st.expander("Patient Summary (IPS)", expanded=False):
                render_patient_summary()
            
            st.markdown("---")
            
            # informational note about production data sourcing
            st.caption("Note: In production, all context fields are dynamically populated from backend systems (EMR, NLP, geospatial APIs). This demo allows manual configuration for testing.")
        
        # action buttons below the container
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset User", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        with col2:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

    with chat_col:
        st.subheader("Chat Interface")
        
        # create a container for chat messages with fixed height
        chat_container = st.container(height=600)
        with chat_container:
            render_chat_interface()
        
        # if we're processing, generate the agent response
        if st.session_state.get("processing", False):
            handler.handle_agent_response()
        
        # chat input stays at the bottom
        if prompt := st.chat_input("Type your message here..."):
            handler.handle_chat_input(prompt)


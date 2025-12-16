"""Questionnaire resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class QuestionnaireGenerator(FHIRResourceGenerator):
    """Generator for FHIR Questionnaire resources."""

    # Standard clinical questionnaire templates
    QUESTIONNAIRE_TEMPLATES: list[dict[str, Any]] = [
        {
            "name": "phq-9",
            "title": "Patient Health Questionnaire (PHQ-9)",
            "description": "A 9-item depression screening tool",
            "purpose": "Depression screening and severity assessment",
            "items": [
                {"linkId": "1", "text": "Little interest or pleasure in doing things", "type": "choice"},
                {"linkId": "2", "text": "Feeling down, depressed, or hopeless", "type": "choice"},
                {"linkId": "3", "text": "Trouble falling or staying asleep, or sleeping too much", "type": "choice"},
                {"linkId": "4", "text": "Feeling tired or having little energy", "type": "choice"},
                {"linkId": "5", "text": "Poor appetite or overeating", "type": "choice"},
                {"linkId": "6", "text": "Feeling bad about yourself", "type": "choice"},
                {"linkId": "7", "text": "Trouble concentrating on things", "type": "choice"},
                {"linkId": "8", "text": "Moving or speaking slowly, or being fidgety", "type": "choice"},
                {"linkId": "9", "text": "Thoughts of self-harm", "type": "choice"},
            ],
            "answer_options": [
                {"valueInteger": 0, "display": "Not at all"},
                {"valueInteger": 1, "display": "Several days"},
                {"valueInteger": 2, "display": "More than half the days"},
                {"valueInteger": 3, "display": "Nearly every day"},
            ],
        },
        {
            "name": "gad-7",
            "title": "Generalized Anxiety Disorder Assessment (GAD-7)",
            "description": "A 7-item anxiety screening tool",
            "purpose": "Anxiety screening and severity assessment",
            "items": [
                {"linkId": "1", "text": "Feeling nervous, anxious, or on edge", "type": "choice"},
                {"linkId": "2", "text": "Not being able to stop or control worrying", "type": "choice"},
                {"linkId": "3", "text": "Worrying too much about different things", "type": "choice"},
                {"linkId": "4", "text": "Trouble relaxing", "type": "choice"},
                {"linkId": "5", "text": "Being so restless that it's hard to sit still", "type": "choice"},
                {"linkId": "6", "text": "Becoming easily annoyed or irritable", "type": "choice"},
                {"linkId": "7", "text": "Feeling afraid as if something awful might happen", "type": "choice"},
            ],
            "answer_options": [
                {"valueInteger": 0, "display": "Not at all"},
                {"valueInteger": 1, "display": "Several days"},
                {"valueInteger": 2, "display": "More than half the days"},
                {"valueInteger": 3, "display": "Nearly every day"},
            ],
        },
        {
            "name": "health-intake",
            "title": "Patient Health Intake Form",
            "description": "General health intake questionnaire",
            "purpose": "Collect patient health history and current symptoms",
            "items": [
                {
                    "linkId": "emergency-contact",
                    "text": "Emergency Contact",
                    "type": "group",
                    "items": [
                        {"linkId": "ec1", "text": "Contact Name", "type": "string"},
                        {"linkId": "ec2", "text": "Relationship", "type": "string"},
                        {"linkId": "ec3", "text": "Phone Number", "type": "string"},
                    ],
                },
                {"linkId": "current-symptoms", "text": "What symptoms are you experiencing?", "type": "text"},
                {"linkId": "symptom-duration", "text": "How long have you had these symptoms?", "type": "string"},
                {"linkId": "medications", "text": "List current medications", "type": "text"},
                {"linkId": "allergies", "text": "Do you have any allergies?", "type": "boolean"},
                {"linkId": "allergy-list", "text": "If yes, please list allergies", "type": "text"},
                {"linkId": "smoking", "text": "Do you smoke?", "type": "boolean"},
                {"linkId": "alcohol", "text": "How often do you drink alcohol?", "type": "choice"},
            ],
            "answer_options": None,
        },
        {
            "name": "pain-assessment",
            "title": "Pain Assessment Questionnaire",
            "description": "Comprehensive pain evaluation form",
            "purpose": "Assess patient pain level and characteristics",
            "items": [
                {"linkId": "pain-level", "text": "Rate your pain level (0-10)", "type": "integer"},
                {"linkId": "pain-location", "text": "Where is your pain located?", "type": "string"},
                {"linkId": "pain-duration", "text": "How long have you had this pain?", "type": "string"},
                {"linkId": "pain-type", "text": "Describe your pain", "type": "choice"},
                {"linkId": "pain-worse", "text": "What makes the pain worse?", "type": "text"},
                {"linkId": "pain-better", "text": "What makes the pain better?", "type": "text"},
                {"linkId": "pain-interferes", "text": "Does pain interfere with daily activities?", "type": "boolean"},
            ],
            "answer_options": [
                {"valueString": "sharp", "display": "Sharp"},
                {"valueString": "dull", "display": "Dull"},
                {"valueString": "burning", "display": "Burning"},
                {"valueString": "aching", "display": "Aching"},
                {"valueString": "throbbing", "display": "Throbbing"},
            ],
        },
        {
            "name": "covid-screening",
            "title": "COVID-19 Screening Questionnaire",
            "description": "Pre-visit COVID-19 symptom screening",
            "purpose": "Screen for COVID-19 symptoms before healthcare visit",
            "items": [
                {"linkId": "fever", "text": "Do you have a fever or feel feverish?", "type": "boolean"},
                {"linkId": "cough", "text": "Do you have a new or worsening cough?", "type": "boolean"},
                {"linkId": "breathing", "text": "Are you experiencing shortness of breath?", "type": "boolean"},
                {"linkId": "taste-smell", "text": "Have you lost your sense of taste or smell?", "type": "boolean"},
                {
                    "linkId": "contact",
                    "text": "Have you been in contact with someone diagnosed with COVID-19?",
                    "type": "boolean",
                },
                {"linkId": "travel", "text": "Have you traveled in the past 14 days?", "type": "boolean"},
            ],
            "answer_options": None,
        },
        {
            "name": "audit-c",
            "title": "AUDIT-C Alcohol Screening",
            "description": "Alcohol Use Disorders Identification Test - Consumption",
            "purpose": "Brief alcohol screening tool to identify hazardous drinking",
            "items": [
                {"linkId": "1", "text": "How often do you have a drink containing alcohol?", "type": "choice"},
                {
                    "linkId": "2",
                    "text": "How many drinks containing alcohol do you have on a typical day when you are drinking?",
                    "type": "choice",
                },
                {"linkId": "3", "text": "How often do you have 6 or more drinks on one occasion?", "type": "choice"},
            ],
            "answer_options": [
                {"valueInteger": 0, "display": "Never"},
                {"valueInteger": 1, "display": "Monthly or less"},
                {"valueInteger": 2, "display": "2-4 times a month"},
                {"valueInteger": 3, "display": "2-3 times a week"},
                {"valueInteger": 4, "display": "4+ times a week"},
            ],
        },
        {
            "name": "falls-risk",
            "title": "Falls Risk Assessment",
            "description": "Assessment tool for fall risk in older adults",
            "purpose": "Identify patients at increased risk of falling",
            "items": [
                {"linkId": "fallen", "text": "Have you fallen in the past year?", "type": "boolean"},
                {"linkId": "fall-count", "text": "If yes, how many times?", "type": "integer"},
                {"linkId": "unsteady", "text": "Do you feel unsteady when standing or walking?", "type": "boolean"},
                {"linkId": "worry", "text": "Do you worry about falling?", "type": "boolean"},
                {"linkId": "assistance", "text": "Do you need assistance with walking?", "type": "choice"},
                {"linkId": "vision", "text": "Do you have vision problems?", "type": "boolean"},
                {"linkId": "medications", "text": "Do you take 4 or more medications daily?", "type": "boolean"},
                {"linkId": "dizziness", "text": "Do you experience dizziness or lightheadedness?", "type": "boolean"},
            ],
            "answer_options": [
                {"valueString": "none", "display": "No assistance needed"},
                {"valueString": "cane", "display": "Cane"},
                {"valueString": "walker", "display": "Walker"},
                {"valueString": "wheelchair", "display": "Wheelchair"},
                {"valueString": "person", "display": "Another person"},
            ],
        },
        {
            "name": "sdoh",
            "title": "Social Determinants of Health Screening",
            "description": "Screen for social factors affecting health",
            "purpose": "Identify social needs that may impact patient health outcomes",
            "items": [
                {
                    "linkId": "housing",
                    "text": "Housing",
                    "type": "group",
                    "items": [
                        {"linkId": "h1", "text": "Are you worried about losing your housing?", "type": "boolean"},
                        {
                            "linkId": "h2",
                            "text": "What is your current living situation?",
                            "type": "choice",
                        },
                    ],
                },
                {
                    "linkId": "food",
                    "text": "Food Security",
                    "type": "group",
                    "items": [
                        {
                            "linkId": "f1",
                            "text": "Within the past 12 months, did you worry about running out of food?",
                            "type": "boolean",
                        },
                        {
                            "linkId": "f2",
                            "text": "Within the past 12 months, did you run out of food and couldn't afford more?",
                            "type": "boolean",
                        },
                    ],
                },
                {
                    "linkId": "transportation",
                    "text": "Do you have trouble getting transportation to medical appointments?",
                    "type": "boolean",
                },
                {
                    "linkId": "utilities",
                    "text": "In the past year, have you had utilities shut off?",
                    "type": "boolean",
                },
                {
                    "linkId": "safety",
                    "text": "Do you feel physically or emotionally unsafe where you live?",
                    "type": "boolean",
                },
            ],
            "answer_options": [
                {"valueString": "own", "display": "I have housing and own my home"},
                {"valueString": "rent", "display": "I have housing and rent"},
                {"valueString": "temporary", "display": "Staying with others temporarily"},
                {"valueString": "shelter", "display": "Staying in a shelter"},
                {"valueString": "homeless", "display": "I do not have housing"},
            ],
        },
        {
            "name": "medication-adherence",
            "title": "Medication Adherence Questionnaire",
            "description": "Assessment of medication-taking behavior",
            "purpose": "Identify barriers to medication adherence",
            "items": [
                {"linkId": "1", "text": "Do you sometimes forget to take your medicine?", "type": "boolean"},
                {
                    "linkId": "2",
                    "text": "Over the past 2 weeks, were there days you didn't take your medicine?",
                    "type": "boolean",
                },
                {
                    "linkId": "3",
                    "text": "Have you ever stopped taking medicine without telling your doctor because you felt worse?",
                    "type": "boolean",
                },
                {
                    "linkId": "4",
                    "text": "When you travel or leave home, do you sometimes forget to bring your medicine?",
                    "type": "boolean",
                },
                {"linkId": "5", "text": "Did you take your medicine yesterday?", "type": "boolean"},
                {
                    "linkId": "6",
                    "text": "When you feel your symptoms are under control, do you sometimes stop taking medicine?",
                    "type": "boolean",
                },
                {
                    "linkId": "7",
                    "text": "Do you ever feel hassled about sticking to your treatment plan?",
                    "type": "boolean",
                },
                {
                    "linkId": "8",
                    "text": "How often do you have difficulty remembering to take all your medications?",
                    "type": "choice",
                },
            ],
            "answer_options": [
                {"valueInteger": 0, "display": "Never/Rarely"},
                {"valueInteger": 1, "display": "Once in a while"},
                {"valueInteger": 2, "display": "Sometimes"},
                {"valueInteger": 3, "display": "Usually"},
                {"valueInteger": 4, "display": "All the time"},
            ],
        },
        {
            "name": "patient-satisfaction",
            "title": "Patient Satisfaction Survey",
            "description": "Post-visit satisfaction questionnaire",
            "purpose": "Measure patient satisfaction with healthcare services",
            "items": [
                {"linkId": "wait-time", "text": "How would you rate your wait time?", "type": "choice"},
                {"linkId": "staff-courtesy", "text": "How courteous was the staff?", "type": "choice"},
                {"linkId": "provider-listen", "text": "Did the provider listen to your concerns?", "type": "choice"},
                {"linkId": "provider-explain", "text": "Did the provider explain things clearly?", "type": "choice"},
                {"linkId": "overall", "text": "Overall, how satisfied are you with your visit?", "type": "choice"},
                {"linkId": "recommend", "text": "Would you recommend this practice to others?", "type": "boolean"},
                {"linkId": "comments", "text": "Additional comments or suggestions", "type": "text"},
            ],
            "answer_options": [
                {"valueInteger": 1, "display": "Poor"},
                {"valueInteger": 2, "display": "Fair"},
                {"valueInteger": 3, "display": "Good"},
                {"valueInteger": 4, "display": "Very Good"},
                {"valueInteger": 5, "display": "Excellent"},
            ],
        },
        {
            "name": "brief-mental-status",
            "title": "Brief Mental Status Exam",
            "description": "Quick cognitive screening assessment",
            "purpose": "Screen for cognitive impairment",
            "items": [
                {"linkId": "orientation-time", "text": "What is today's date?", "type": "string"},
                {"linkId": "orientation-place", "text": "Where are we right now?", "type": "string"},
                {
                    "linkId": "recall-words",
                    "text": "I will say 3 words. Repeat them: Apple, Table, Penny",
                    "type": "display",
                },
                {"linkId": "recall-immediate", "text": "Can the patient repeat all 3 words?", "type": "boolean"},
                {"linkId": "spell-world", "text": "Spell WORLD backwards", "type": "string"},
                {
                    "linkId": "recall-delayed",
                    "text": "What were the 3 words I asked you to remember?",
                    "type": "string",
                },
                {"linkId": "recall-score", "text": "How many words did the patient recall? (0-3)", "type": "integer"},
                {"linkId": "clock-draw", "text": "Can the patient draw a clock showing 10 past 11?", "type": "boolean"},
            ],
            "answer_options": None,
        },
        {
            "name": "surgical-preop",
            "title": "Surgical Pre-Operative Assessment",
            "description": "Pre-surgery health assessment questionnaire",
            "purpose": "Evaluate patient readiness for surgery",
            "items": [
                {
                    "linkId": "cardiac",
                    "text": "Cardiac History",
                    "type": "group",
                    "items": [
                        {"linkId": "c1", "text": "Do you have a history of heart disease?", "type": "boolean"},
                        {"linkId": "c2", "text": "Do you have high blood pressure?", "type": "boolean"},
                        {"linkId": "c3", "text": "Do you have a pacemaker or defibrillator?", "type": "boolean"},
                    ],
                },
                {
                    "linkId": "respiratory",
                    "text": "Respiratory History",
                    "type": "group",
                    "items": [
                        {"linkId": "r1", "text": "Do you have asthma or COPD?", "type": "boolean"},
                        {"linkId": "r2", "text": "Do you use supplemental oxygen?", "type": "boolean"},
                        {"linkId": "r3", "text": "Have you had problems with anesthesia before?", "type": "boolean"},
                    ],
                },
                {
                    "linkId": "bleeding",
                    "text": "Do you have a bleeding disorder or take blood thinners?",
                    "type": "boolean",
                },
                {"linkId": "diabetes", "text": "Do you have diabetes?", "type": "boolean"},
                {"linkId": "sleep-apnea", "text": "Do you have sleep apnea?", "type": "boolean"},
                {"linkId": "last-meal", "text": "When did you last eat or drink?", "type": "dateTime"},
                {
                    "linkId": "ride-home",
                    "text": "Do you have someone to drive you home after surgery?",
                    "type": "boolean",
                },
            ],
            "answer_options": None,
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        questionnaire_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        template: str | None = None,
        status: str = "active",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Questionnaire resource.

        Args:
            questionnaire_id: Questionnaire ID (generates UUID if None)
            name: Computer-friendly name (uses template if None)
            title: Human-readable title (uses template if None)
            template: Template name to use (phq-9, gad-7, health-intake, pain-assessment, covid-screening)
            status: Publication status (draft, active, retired, unknown)

        Returns:
            Questionnaire FHIR resource
        """
        if questionnaire_id is None:
            questionnaire_id = self._generate_id()

        # Select template
        selected: dict[str, Any]
        if template:
            selected = next(
                (t for t in self.QUESTIONNAIRE_TEMPLATES if t["name"] == template),
                self.QUESTIONNAIRE_TEMPLATES[0],
            )
        else:
            selected = self.QUESTIONNAIRE_TEMPLATES[self.faker.random_int(0, len(self.QUESTIONNAIRE_TEMPLATES) - 1)]

        questionnaire_name = name or selected["name"]
        questionnaire_title = title or selected["title"]

        questionnaire: dict[str, Any] = {
            "resourceType": "Questionnaire",
            "id": questionnaire_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/Questionnaire/{questionnaire_name}",
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/questionnaire-ids",
                    value=f"Q-{questionnaire_name.upper()}",
                ),
            ],
            "version": "1.0.0",
            "name": questionnaire_name.replace("-", "_"),
            "title": questionnaire_title,
            "status": status,
            "subjectType": ["Patient"],
            "date": self._generate_date(),
            "publisher": "Example Healthcare Organization",
            "description": selected["description"],
            "purpose": selected["purpose"],
            "item": self._generate_items(selected),
        }

        return questionnaire

    def _generate_items(self, template: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate questionnaire items from template."""
        items = []
        answer_options = template.get("answer_options")

        for item_def in template["items"]:
            item: dict[str, Any] = {
                "linkId": item_def["linkId"],
                "text": item_def["text"],
                "type": item_def["type"],
            }

            # Handle nested items (groups)
            if item_def["type"] == "group" and "items" in item_def:
                item["item"] = [
                    {
                        "linkId": sub["linkId"],
                        "text": sub["text"],
                        "type": sub["type"],
                    }
                    for sub in item_def["items"]
                ]
            # Add answer options for choice items
            elif item_def["type"] == "choice" and answer_options:
                item["answerOption"] = [self._format_answer_option(opt) for opt in answer_options]

            items.append(item)

        return items

    def _format_answer_option(self, option: dict[str, Any]) -> dict[str, Any]:
        """Format an answer option."""
        formatted: dict[str, Any] = {}

        if "valueInteger" in option:
            formatted["valueInteger"] = option["valueInteger"]
        elif "valueString" in option:
            formatted["valueString"] = option["valueString"]
        elif "valueCoding" in option:
            formatted["valueCoding"] = option["valueCoding"]

        # Add extension for display if needed
        if "display" in option:
            formatted["extension"] = [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/questionnaire-optionDisplay",
                    "valueString": option["display"],
                }
            ]

        return formatted

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SourceRef:
    title: str
    url: str


@dataclass(frozen=True)
class FactItem:
    key: str
    label: str
    reason: str


@dataclass(frozen=True)
class EvidenceItem:
    key: str
    label: str
    reason: str
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class PermitRoute:
    route_id: str
    family: str
    phase: str
    name: str
    summary: str
    tags: tuple[str, ...]
    required_facts: tuple[FactItem, ...]
    required_evidence: tuple[EvidenceItem, ...]
    risk_flags: tuple[str, ...]
    sources: tuple[SourceRef, ...]
    agent_path: tuple[str, ...] = (
        "Intake",
        "Eligibility",
        "Evidence",
        "Legal Source",
        "Risk",
        "Packet",
        "Partner Review",
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


SOURCE_APPLY = SourceRef(
    "Migrationsverket: Apply for a permit to be in Sweden",
    "https://www.migrationsverket.se/en/you-want-to-apply.html",
)
SOURCE_EXTEND = SourceRef(
    "Migrationsverket: Extend your permit",
    "https://www.migrationsverket.se/en/you-want-to-extend.html",
)
SOURCE_APPEAL = SourceRef(
    "Migrationsverket: Appeal a decision",
    "https://www.migrationsverket.se/en/word-explanations/appeal-a-decision.html",
)
SOURCE_WORK = SourceRef(
    "Migrationsverket: Work permit or residence permit to work",
    "https://www.migrationsverket.se/en/you-want-to-apply/work.html",
)
SOURCE_WORK_EMPLOYEE = SourceRef(
    "Migrationsverket: Employees",
    "https://www.migrationsverket.se/en/you-want-to-apply/work/employee-or-self-employed/employees.html",
)
SOURCE_WORK_SELF_EMPLOYED = SourceRef(
    "Migrationsverket: Self-employed people",
    "https://www.migrationsverket.se/en/you-want-to-apply/work/employee-or-self-employed/self-employed-people.html",
)
SOURCE_STUDENT_FOUND_WORK = SourceRef(
    "Migrationsverket: Work permit after higher education",
    "https://www.migrationsverket.se/en/you-want-to-apply/work/employee-or-self-employed/students-who-have-found-work.html",
)
SOURCE_EU_BLUE_CARD = SourceRef(
    "Migrationsverket: EU Blue Cards",
    "https://www.migrationsverket.se/en/you-want-to-apply/work/employee-or-self-employed/eu-blue-cards.html",
)
SOURCE_ICT = SourceRef(
    "Migrationsverket: ICT permits",
    "https://www.migrationsverket.se/en/you-want-to-apply/work/employee-or-self-employed/ict-permits.html",
)
SOURCE_RESEARCHER = SourceRef(
    "Migrationsverket: Researchers",
    "https://www.migrationsverket.se/en/you-want-to-apply/work/employee-or-self-employed/researchers.html",
)
SOURCE_TEMP_WORK = SourceRef(
    "Migrationsverket: Temporary work in Sweden",
    "https://www.migrationsverket.se/en/you-want-to-apply/work/temporary-work-in-sweden.html",
)
SOURCE_SEASONAL = SourceRef(
    "Migrationsverket: Seasonal workers",
    "https://www.migrationsverket.se/en/you-want-to-apply/work/temporary-work-in-sweden/seasonal-workers.html",
)
SOURCE_AU_PAIR = SourceRef(
    "Migrationsverket: Au pairs",
    "https://www.migrationsverket.se/en/you-want-to-apply/work/temporary-work-in-sweden/au-pairs.html",
)
SOURCE_AFTER_VISIT_EMPLOYER = SourceRef(
    "Migrationsverket: Apply after visiting an employer",
    "https://www.migrationsverket.se/en/you-want-to-apply/work/employee-or-self-employed/apply-for-a-work-permit-after-visiting-an-employer.html",
)
SOURCE_STUDY = SourceRef(
    "Migrationsverket: Residence permit for studies",
    "https://www.migrationsverket.se/en/you-want-to-apply/study.html",
)
SOURCE_STUDY_HIGHER = SourceRef(
    "Migrationsverket: Higher education studies",
    "https://www.migrationsverket.se/en/you-want-to-apply/study/higher-education.html",
)
SOURCE_STUDY_EXTEND_HIGHER = SourceRef(
    "Migrationsverket: Extend higher education studies",
    "https://www.migrationsverket.se/en/you-want-to-extend/study/higher-education.html",
)
SOURCE_DOCTORAL = SourceRef(
    "Migrationsverket: Doctoral studies",
    "https://www.migrationsverket.se/en/you-want-to-apply/study/doctoral-studies.html",
)
SOURCE_MOBILITY_STUDY = SourceRef(
    "Migrationsverket: Studies in a mobility programme",
    "https://www.migrationsverket.se/en/you-want-to-apply/study/studies-in-a-mobility-programme.html",
)
SOURCE_POST_STUDY = SourceRef(
    "Migrationsverket: Look for work after completed studies",
    "https://www.migrationsverket.se/en/you-want-to-extend/study/look-for-work-after-completing-your-studies-in-sweden.html",
)
SOURCE_FAMILY = SourceRef(
    "Migrationsverket: Live with someone",
    "https://www.migrationsverket.se/en/you-want-to-apply/live-with-someone.html",
)
SOURCE_PARTNER = SourceRef(
    "Migrationsverket: Live with a partner",
    "https://www.migrationsverket.se/en/you-want-to-apply/live-with-someone/live-with-a-partner-child-or-other-relative/live-with-a-partner.html",
)
SOURCE_VISIT = SourceRef(
    "Migrationsverket: Visiting Sweden",
    "https://www.migrationsverket.se/en/you-want-to-apply/visiting-sweden.html",
)
SOURCE_VISIT_90 = SourceRef(
    "Migrationsverket: Visiting Sweden up to 90 days",
    "https://www.migrationsverket.se/en/you-want-to-apply/visiting-sweden/visiting-sweden-for-up-to-90-days-entry-visa.html",
)
SOURCE_VISIT_OVER_90 = SourceRef(
    "Migrationsverket: Visiting Sweden for more than 90 days",
    "https://www.migrationsverket.se/en/you-want-to-apply/visiting-sweden/visiting-sweden-for-more-than-90-days.html",
)
SOURCE_PERMANENT = SourceRef(
    "Migrationsverket: Permanent residence permit",
    "https://www.migrationsverket.se/en/you-want-to-apply/permanent-residence-permit.html",
)
SOURCE_CITIZENSHIP = SourceRef(
    "Migrationsverket: Swedish citizenship",
    "https://www.migrationsverket.se/en/you-want-to-apply/swedish-citizenship.html",
)
SOURCE_CITIZENSHIP_ADULT = SourceRef(
    "Migrationsverket: Citizenship for adults",
    "https://www.migrationsverket.se/en/you-want-to-apply/swedish-citizenship/citizenship-for-adults/citizenship-for-adults.html",
)
SOURCE_LONG_TERM_SWEDEN = SourceRef(
    "Migrationsverket: Long-term resident status in Sweden",
    "https://www.migrationsverket.se/en/you-want-to-apply/long-term-residents-in-sweden.html",
)
SOURCE_LONG_TERM_OTHER_EU = SourceRef(
    "Migrationsverket: Long-term residents in another EU country",
    "https://www.migrationsverket.se/en/you-want-to-apply/long-term-residents-in-another-eu-country.html",
)


FACT_IDENTITY = FactItem("identity_and_nationality", "Identity and nationality", "Route depends on citizenship and identity proof.")
FACT_LOCATION = FactItem("current_location", "Current location", "Some first-time routes must be applied for from outside Sweden or the EU.")
FACT_CURRENT_STATUS = FactItem("current_permit_status", "Current permit/status", "Determines whether this is first-time, extension, switch, or appeal.")
FACT_EXPIRY = FactItem("current_permit_expiry", "Current permit expiry date", "Many in-country routes require applying before the current permit expires.")
FACT_FAMILY = FactItem("family_relationship", "Family relationship", "Family routes depend on relationship and sponsor status.")
FACT_FUNDS = FactItem("maintenance_or_funds", "Maintenance/funds", "Most permit routes require proof of support.")
FACT_EMPLOYER = FactItem("employer_and_role", "Employer and role", "Work routes depend on employer, occupation, salary, and contract terms.")
FACT_STUDY = FactItem("study_programme", "Study programme", "Study routes depend on admission, level, workload, and progress.")
FACT_REJECTION = FactItem("decision_or_rejection", "Decision/rejection facts", "Appeal/rejection paths depend on the decision and its deadline.")

E_PASSPORT = EvidenceItem("passport_copy", "Passport copies", "Required across most routes.", ("passport", "identity_document"))
E_PHOTO_BIOMETRICS = EvidenceItem("biometrics", "Biometrics/passport presentation", "Usually required before residence-card decision.", ("fingerprints", "photo"))
E_FUNDS = EvidenceItem("maintenance_proof", "Proof of maintenance/funds", "Shows support during stay.", ("bank_statement", "payslip", "financial_support"))
E_INSURANCE = EvidenceItem("insurance_proof", "Insurance proof", "Required in several short-stay, work, study, and research routes.", ("health_insurance", "travel_insurance"))
E_CONTRACT = EvidenceItem("employment_contract", "Signed employment contract", "Needed for employee/work routes.", ("job_contract", "work_contract"))
E_EMPLOYER = EvidenceItem("employer_details", "Employer details", "Needed for employer-backed work routes.", ("employer_offer", "employer_information"))
E_SALARY = EvidenceItem("salary_terms", "Salary and employment terms", "Checks collective agreement/common practice and current salary thresholds.", ("salary", "wage", "collective_agreement"))
E_WORK_INSURANCE = EvidenceItem("employment_insurances", "Employment insurance package", "Health, life, industrial injury, and occupational pension insurance where required.", ("life_insurance", "occupational_pension"))
E_ADMISSION = EvidenceItem("admission_letter", "Admission letter", "Needed for study routes.", ("university_admission", "school_admission"))
E_STUDY_PROGRESS = EvidenceItem("study_progress", "Study progress or transcript", "Needed for extensions, post-study, and work-after-study routes.", ("transcript", "passed_courses", "completion_certificate"))
E_TUITION = EvidenceItem("tuition_payment", "Tuition payment proof", "Needed when tuition applies.", ("tuition_fee", "payment_receipt"))
E_HOSTING = EvidenceItem("hosting_agreement", "Hosting agreement", "Needed for researcher/doctoral research route.", ("research_hosting",))
E_BUSINESS = EvidenceItem("business_plan", "Business plan and company records", "Needed for self-employed routes.", ("company_registration", "business_budget"))
E_INVITATION = EvidenceItem("invitation", "Invitation", "Needed for several visit routes.", ("invite", "host_invitation"))
E_RELATIONSHIP = EvidenceItem("relationship_proof", "Relationship proof", "Needed for family routes.", ("marriage_certificate", "birth_certificate", "cohabitation_proof"))
E_SPONSOR_STATUS = EvidenceItem("sponsor_status", "Sponsor status in Sweden", "Needed for family and accompanying routes.", ("sponsor_permit", "sponsor_citizenship"))
E_HOUSING = EvidenceItem("housing_proof", "Housing proof", "Often needed for maintenance/housing requirement routes.", ("lease", "housing_contract"))
E_DECISION = EvidenceItem("decision_letter", "Decision letter", "Needed for appeal/rejection analysis.", ("rejection_decision", "court_judgment"))
E_APPEAL_DEADLINE = EvidenceItem("appeal_deadline", "Appeal instruction/deadline appendix", "The decision-specific deadline controls.", ("deadline_appendix", "appeal_instruction"))


def _route(
    route_id: str,
    family: str,
    phase: str,
    name: str,
    summary: str,
    tags: tuple[str, ...],
    facts: tuple[FactItem, ...],
    evidence: tuple[EvidenceItem, ...],
    risks: tuple[str, ...],
    sources: tuple[SourceRef, ...],
) -> PermitRoute:
    return PermitRoute(
        route_id=route_id,
        family=family,
        phase=phase,
        name=name,
        summary=summary,
        tags=tags,
        required_facts=facts,
        required_evidence=evidence,
        risk_flags=risks,
        sources=sources,
    )


PERMIT_ROUTES: tuple[PermitRoute, ...] = (
    _route(
        "visit_schengen_visa_90",
        "visiting",
        "apply",
        "Visit Sweden up to 90 days / Schengen visa",
        "For non-EU visitors who need an entry visa for up to 90 days.",
        ("visit", "tourism", "business_visit", "conference", "medical_visit", "religious_visit"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_FUNDS),
        (E_PASSPORT, E_INVITATION, E_FUNDS, E_INSURANCE),
        ("must_show_intent_to_leave",),
        (SOURCE_VISIT, SOURCE_VISIT_90),
    ),
    _route(
        "visit_residence_over_90",
        "visiting",
        "apply_or_extend",
        "Visitor residence permit over 90 days",
        "For visits longer than 90 days or extension of an ongoing visit.",
        ("visit", "visitor_residence", "over_90_days", "invitation"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_FUNDS),
        (E_PASSPORT, E_INVITATION, E_FUNDS, E_INSURANCE),
        ("must_intend_to_leave", "not_for_settlement"),
        (SOURCE_VISIT, SOURCE_VISIT_OVER_90),
    ),
    _route(
        "work_employee",
        "work",
        "apply",
        "Work permit as employee",
        "For a non-EU/EEA citizen with employment in Sweden.",
        ("work", "employee", "employment", "salary", "insurance"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_EMPLOYER, FACT_CURRENT_STATUS),
        (E_PASSPORT, E_CONTRACT, E_EMPLOYER, E_SALARY, E_WORK_INSURANCE, E_INSURANCE),
        ("salary_threshold_check", "occupation_exclusion_check", "employer_compliance_check"),
        (SOURCE_WORK, SOURCE_WORK_EMPLOYEE),
    ),
    _route(
        "work_self_employed",
        "work",
        "apply",
        "Residence permit as self-employed person",
        "For running your own business in Sweden.",
        ("work", "self_employed", "business", "entrepreneur"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_FUNDS),
        (E_PASSPORT, E_BUSINESS, E_FUNDS),
        ("first_time_outside_sweden_check", "business_viability_check"),
        (SOURCE_WORK, SOURCE_WORK_SELF_EMPLOYED),
    ),
    _route(
        "work_student_found_work",
        "work",
        "apply_or_switch",
        "Work permit after higher education",
        "For former students in Sweden who have found work.",
        ("work", "student", "former_student", "completed_studies", "employment"),
        (FACT_IDENTITY, FACT_CURRENT_STATUS, FACT_EXPIRY, FACT_STUDY, FACT_EMPLOYER),
        (E_PASSPORT, E_STUDY_PROGRESS, E_CONTRACT, E_SALARY, E_WORK_INSURANCE, E_INSURANCE),
        ("must_apply_before_current_permit_expires", "student_salary_exemption_first_application_check"),
        (SOURCE_STUDENT_FOUND_WORK, SOURCE_WORK_EMPLOYEE),
    ),
    _route(
        "work_eu_blue_card",
        "work",
        "apply",
        "EU Blue Card",
        "For highly qualified employment in Sweden.",
        ("work", "blue_card", "highly_qualified", "salary", "degree"),
        (FACT_IDENTITY, FACT_EMPLOYER, FACT_CURRENT_STATUS),
        (E_PASSPORT, E_CONTRACT, E_SALARY, E_INSURANCE, EvidenceItem("qualification_proof", "Degree or five years experience", "Shows higher education or equivalent experience.", ("degree", "experience_certificate"))),
        ("high_salary_threshold_check", "regulated_profession_check"),
        (SOURCE_EU_BLUE_CARD,),
    ),
    _route(
        "work_ict",
        "work",
        "apply",
        "ICT permit",
        "For intra-corporate transfer to Sweden from a business outside the EU/EEA.",
        ("work", "ict", "intra_corporate_transfer", "manager", "specialist", "trainee"),
        (FACT_IDENTITY, FACT_EMPLOYER, FACT_LOCATION),
        (E_PASSPORT, E_CONTRACT, E_SALARY, E_INSURANCE),
        ("assignment_group_company_check", "full_time_minimum_salary_check"),
        (SOURCE_ICT, SOURCE_WORK),
    ),
    _route(
        "work_researcher",
        "work",
        "apply",
        "Residence permit for researcher",
        "For research in Sweden under a hosting agreement.",
        ("work", "research", "researcher", "doctoral", "hosting_agreement"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_FUNDS),
        (E_PASSPORT, E_HOSTING, E_FUNDS, E_INSURANCE),
        ("research_principal_approval_check",),
        (SOURCE_RESEARCHER,),
    ),
    _route(
        "work_after_visiting_employer",
        "work",
        "apply_or_switch",
        "Work permit after visiting an employer",
        "For specific labour-shortage employment found during a permitted employer visit.",
        ("work", "visited_employer", "labour_shortage", "inside_sweden"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_EMPLOYER),
        (E_PASSPORT, E_CONTRACT, E_EMPLOYER, E_SALARY),
        ("labour_shortage_occupation_check", "tourist_visit_not_eligible_check"),
        (SOURCE_AFTER_VISIT_EMPLOYER, SOURCE_WORK_EMPLOYEE),
    ),
    _route(
        "work_athlete_coach",
        "work",
        "apply",
        "Athlete or coach",
        "For contracted athletes and coaches.",
        ("work", "athlete", "coach", "sports_contract"),
        (FACT_IDENTITY, FACT_EMPLOYER),
        (E_PASSPORT, E_CONTRACT, E_SALARY, E_INSURANCE),
        ("sports_contract_check",),
        (SOURCE_WORK,),
    ),
    _route(
        "work_artist",
        "work",
        "apply",
        "Artist, technician, or tour staff",
        "For artist/tour work in Sweden.",
        ("work", "artist", "tour", "technician"),
        (FACT_IDENTITY, FACT_EMPLOYER),
        (E_PASSPORT, E_CONTRACT, E_INSURANCE),
        ("short_assignment_visa_or_permit_check",),
        (SOURCE_WORK,),
    ),
    _route(
        "work_seafarer",
        "work",
        "apply",
        "Seafarer on Swedish ship",
        "For work as a seafarer on a Swedish ship in domestic traffic.",
        ("work", "seafarer", "ship"),
        (FACT_IDENTITY, FACT_EMPLOYER),
        (E_PASSPORT, E_CONTRACT, E_INSURANCE),
        ("ship_domestic_traffic_check",),
        (SOURCE_WORK,),
    ),
    _route(
        "work_family_afterwards",
        "work_family",
        "apply",
        "Family of employee or self-employed person",
        "For family members joining someone with or applying for a work-related permit.",
        ("family", "work_family", "employee_family", "blue_card_family", "ict_family", "researcher_family"),
        (FACT_IDENTITY, FACT_FAMILY, FACT_CURRENT_STATUS),
        (E_PASSPORT, E_RELATIONSHIP, E_SPONSOR_STATUS, E_FUNDS, E_HOUSING),
        ("maintenance_requirement_check", "age_limit_check"),
        (SourceRef("Migrationsverket: Family of employee or self-employed person", "https://www.migrationsverket.se/en/you-want-to-apply/work/employee-or-self-employed/family-of-an-employee-or-self-employed-person-who-apply-afterwards.html"),),
    ),
    _route(
        "temporary_au_pair",
        "temporary_work",
        "apply",
        "Au pair",
        "For young people applying to work as an au pair.",
        ("temporary_work", "au_pair", "age_18_29"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_EMPLOYER),
        (E_PASSPORT, E_CONTRACT, E_INSURANCE, EvidenceItem("swedish_language_course", "Swedish language course", "Au pair route usually needs language-study arrangement.", ("language_course",))),
        ("age_limit_check", "host_family_agreement_check"),
        (SOURCE_AU_PAIR, SOURCE_TEMP_WORK),
    ),
    _route(
        "temporary_seasonal_worker",
        "temporary_work",
        "apply",
        "Seasonal worker",
        "For seasonal employment in Sweden.",
        ("temporary_work", "seasonal", "seasonal_worker", "berry_picker"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_EMPLOYER),
        (E_PASSPORT, E_CONTRACT, E_SALARY, E_INSURANCE),
        ("first_time_outside_eu_check", "nine_month_maximum_check", "full_time_minimum_salary_check"),
        (SOURCE_SEASONAL, SOURCE_TEMP_WORK),
    ),
    _route(
        "temporary_berry_picker",
        "temporary_work",
        "apply",
        "Berry picker",
        "For berry-picking work where the seasonal/berry-picker rules apply.",
        ("temporary_work", "berry_picker", "seasonal"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_EMPLOYER),
        (E_PASSPORT, E_CONTRACT, E_SALARY, E_INSURANCE),
        ("normal_work_permit_exclusion_check", "seasonal_route_check"),
        (SOURCE_SEASONAL, SOURCE_TEMP_WORK),
    ),
    _route(
        "temporary_volunteer",
        "temporary_work",
        "apply",
        "Volunteer work",
        "For residence permit to work as a volunteer.",
        ("temporary_work", "volunteer"),
        (FACT_IDENTITY, FACT_LOCATION),
        (E_PASSPORT, E_INVITATION, E_FUNDS, E_INSURANCE),
        ("host_organisation_check",),
        (SOURCE_TEMP_WORK,),
    ),
    _route(
        "temporary_working_holiday",
        "temporary_work",
        "apply",
        "Working holiday visa",
        "For eligible young people who want to experience Swedish life and culture.",
        ("temporary_work", "working_holiday", "young_person"),
        (FACT_IDENTITY, FACT_LOCATION, FactItem("age_and_country", "Age and eligible country", "Working holiday routes depend on age and nationality.")),
        (E_PASSPORT, E_FUNDS, E_INSURANCE),
        ("age_and_nationality_check",),
        (SOURCE_TEMP_WORK,),
    ),
    _route(
        "temporary_traineeship",
        "temporary_work",
        "apply",
        "Traineeship or internship",
        "For traineeship/internship in Sweden.",
        ("temporary_work", "traineeship", "internship"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_EMPLOYER),
        (E_PASSPORT, E_CONTRACT, E_INSURANCE),
        ("traineeship_context_check",),
        (SOURCE_TEMP_WORK,),
    ),
    _route(
        "temporary_self_employed_assignment",
        "temporary_work",
        "apply",
        "Self-employed temporary assignment",
        "For people with a business outside the EU and a temporary assignment in Sweden.",
        ("temporary_work", "self_employed_assignment", "temporary_assignment"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_EMPLOYER),
        (E_PASSPORT, E_BUSINESS, E_CONTRACT, E_INSURANCE),
        ("temporary_assignment_check",),
        (SOURCE_TEMP_WORK,),
    ),
    _route(
        "temporary_work_contracting",
        "temporary_work",
        "apply",
        "Temporary work contracting",
        "For employees in another EU country whose business has a temporary assignment in Sweden.",
        ("temporary_work", "contracting", "posted_worker", "another_eu_permit"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_EMPLOYER, FACT_CURRENT_STATUS),
        (E_PASSPORT, E_CONTRACT, E_INSURANCE),
        ("another_eu_residence_permit_check",),
        (SOURCE_TEMP_WORK,),
    ),
    _route(
        "study_higher_education",
        "study",
        "apply",
        "Higher education studies",
        "For first- or second-cycle studies, higher vocational education, folk high school post-secondary level, or exchange studies.",
        ("study", "higher_education", "university", "masters", "bachelors"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_STUDY, FACT_FUNDS),
        (E_PASSPORT, E_ADMISSION, E_TUITION, E_FUNDS, E_INSURANCE),
        ("full_time_or_eligible_study_check", "new_2026_work_limit_check"),
        (SOURCE_STUDY, SOURCE_STUDY_HIGHER),
    ),
    _route(
        "study_extend_higher_education",
        "study",
        "extend",
        "Extend higher education studies",
        "For extending a higher education residence permit.",
        ("study", "extend", "higher_education", "study_progress"),
        (FACT_IDENTITY, FACT_CURRENT_STATUS, FACT_EXPIRY, FACT_STUDY, FACT_FUNDS),
        (E_PASSPORT, E_STUDY_PROGRESS, E_ADMISSION, E_TUITION, E_FUNDS, E_INSURANCE),
        ("must_apply_before_current_permit_expires", "acceptable_study_progress_check"),
        (SOURCE_STUDY_EXTEND_HIGHER, SOURCE_STUDY_HIGHER),
    ),
    _route(
        "study_doctoral",
        "study",
        "apply",
        "Doctoral studies",
        "For doctoral studies when the doctoral-study route applies.",
        ("study", "doctoral", "phd"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_STUDY, FACT_FUNDS),
        (E_PASSPORT, E_ADMISSION, E_FUNDS, E_INSURANCE),
        ("doctoral_vs_researcher_route_check",),
        (SOURCE_DOCTORAL, SOURCE_RESEARCHER),
    ),
    _route(
        "study_mobility",
        "study",
        "apply_or_notify",
        "Studies in a mobility programme",
        "For mobility studies starting in Sweden or notification for studies from another EU country.",
        ("study", "mobility", "eu_mobility"),
        (FACT_IDENTITY, FACT_CURRENT_STATUS, FACT_STUDY),
        (E_PASSPORT, E_ADMISSION, E_INSURANCE),
        ("mobility_notification_vs_permit_check",),
        (SOURCE_MOBILITY_STUDY, SOURCE_STUDY),
    ),
    _route(
        "study_contract_specialisation",
        "study",
        "apply",
        "Contract or specialisation education",
        "For contract/specialisation education.",
        ("study", "contract_education", "specialisation"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_STUDY, FACT_FUNDS),
        (E_PASSPORT, E_ADMISSION, E_TUITION, E_FUNDS, E_INSURANCE),
        ("education_type_check",),
        (SOURCE_STUDY,),
    ),
    _route(
        "study_other_upper_secondary",
        "study",
        "apply",
        "Other studies and upper secondary school",
        "For other studies or upper-secondary exchange longer than three months.",
        ("study", "other_studies", "upper_secondary", "exchange"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_STUDY, FACT_FUNDS),
        (E_PASSPORT, E_ADMISSION, E_TUITION, E_FUNDS, E_INSURANCE),
        ("full_time_not_distance_learning_check",),
        (SOURCE_STUDY,),
    ),
    _route(
        "study_post_study_look_for_work",
        "study",
        "apply_or_extend",
        "Look for work after completed studies",
        "For people who completed higher education studies in Sweden and want time to look for work or start a business.",
        ("study", "post_study", "look_for_work", "start_business", "completed_studies"),
        (FACT_IDENTITY, FACT_CURRENT_STATUS, FACT_EXPIRY, FACT_STUDY, FACT_FUNDS),
        (E_PASSPORT, E_STUDY_PROGRESS, E_FUNDS, E_INSURANCE),
        ("must_apply_before_current_permit_expires", "completed_entire_programme_check"),
        (SOURCE_POST_STUDY, SOURCE_STUDY),
    ),
    _route(
        "study_family_afterwards",
        "study_family",
        "apply",
        "Family of student applying afterwards",
        "For family members joining a student, doctoral student, or post-study job-search permit holder.",
        ("family", "student_family", "accompanying_student"),
        (FACT_IDENTITY, FACT_FAMILY, FACT_CURRENT_STATUS),
        (E_PASSPORT, E_RELATIONSHIP, E_SPONSOR_STATUS, E_FUNDS, E_HOUSING),
        ("student_sponsor_status_check",),
        (SOURCE_STUDY, SOURCE_FAMILY),
    ),
    _route(
        "family_partner_child_relative",
        "family",
        "apply",
        "Live with partner, child, parent, or other relative",
        "For family-based residence with someone in Sweden.",
        ("family", "partner", "spouse", "cohabitant", "child", "parent", "relative"),
        (FACT_IDENTITY, FACT_FAMILY, FACT_CURRENT_STATUS),
        (E_PASSPORT, E_RELATIONSHIP, E_SPONSOR_STATUS, E_FUNDS, E_HOUSING),
        ("maintenance_requirement_check", "relationship_genuineness_check", "child_best_interests_check"),
        (SOURCE_FAMILY, SOURCE_PARTNER),
    ),
    _route(
        "family_child_residence",
        "family",
        "apply",
        "Residence permit for children",
        "For a child who will live with a parent/relative or was born/adopted in Sweden.",
        ("family", "child", "child_born_in_sweden", "adoption"),
        (FACT_IDENTITY, FACT_FAMILY, FACT_CURRENT_STATUS),
        (E_PASSPORT, E_RELATIONSHIP, E_SPONSOR_STATUS),
        ("custody_consent_check", "child_best_interests_check"),
        (SOURCE_FAMILY,),
    ),
    _route(
        "family_other_ties",
        "family",
        "apply",
        "Other ties to Sweden",
        "For prior permanent residence, Swedish ancestry, or other specific ties.",
        ("family", "other_ties", "swedish_ancestry", "former_permanent_residence"),
        (FACT_IDENTITY, FACT_CURRENT_STATUS, FACT_FAMILY),
        (E_PASSPORT, E_RELATIONSHIP, E_SPONSOR_STATUS),
        ("route_specific_ties_check",),
        (SOURCE_FAMILY,),
    ),
    _route(
        "permanent_residence",
        "permanent",
        "apply_with_extension",
        "Permanent residence permit",
        "For people with a Swedish residence permit who may qualify for permanent residence.",
        ("permanent", "permanent_residence", "maintenance", "good_conduct"),
        (FACT_IDENTITY, FACT_CURRENT_STATUS, FACT_EXPIRY, FACT_FUNDS),
        (E_PASSPORT, EvidenceItem("residence_history", "Residence history", "Shows time in Sweden on qualifying permits.", ("permit_cards", "population_register")), E_FUNDS, EvidenceItem("good_conduct_records", "Good conduct evidence", "Supports good conduct review where relevant.", ("criminal_record", "debt_record"))),
        ("permit_type_duration_check", "maintenance_and_good_conduct_check"),
        (SOURCE_PERMANENT,),
    ),
    _route(
        "long_term_resident_sweden",
        "long_term_resident",
        "apply",
        "Long-term resident status in Sweden",
        "For non-EU/EEA citizens who have lived in Sweden continuously for five years.",
        ("long_term", "five_years", "resident_status"),
        (FACT_IDENTITY, FACT_CURRENT_STATUS, FactItem("five_year_residence", "Five years residence", "Long-term status requires five years continuous residence.")),
        (E_PASSPORT, EvidenceItem("residence_history", "Five-year residence evidence", "Shows continuous residence/legal stay.", ("permit_cards", "population_register")), E_FUNDS),
        ("temporary_permit_time_exclusion_check", "absence_from_sweden_check"),
        (SOURCE_LONG_TERM_SWEDEN,),
    ),
    _route(
        "long_term_resident_other_eu",
        "long_term_resident",
        "apply",
        "Long-term resident in another EU country",
        "For people with long-term resident status in another EU country moving to Sweden.",
        ("long_term", "another_eu_country", "work", "study", "self_support"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_CURRENT_STATUS),
        (E_PASSPORT, EvidenceItem("eu_long_term_card", "EC/EU long-term resident card", "Shows status in another EU country.", ("long_term_resident_card",)), E_FUNDS),
        ("purpose_of_stay_check",),
        (SOURCE_LONG_TERM_OTHER_EU,),
    ),
    _route(
        "family_long_term_resident_other_eu",
        "long_term_resident_family",
        "apply",
        "Family of long-term resident in another EU country",
        "For family of a person with long-term resident status in another EU country.",
        ("family", "long_term_eu_family"),
        (FACT_IDENTITY, FACT_FAMILY, FACT_CURRENT_STATUS),
        (E_PASSPORT, E_RELATIONSHIP, E_SPONSOR_STATUS, E_FUNDS),
        ("sponsor_long_term_status_check",),
        (SOURCE_LONG_TERM_OTHER_EU,),
    ),
    _route(
        "eu_eea_right_of_residence",
        "eu_eea",
        "information",
        "EU/EEA right of residence",
        "For EU/EEA citizens and family members where right of residence may apply rather than a normal permit.",
        ("eu_eea", "right_of_residence", "no_permit_needed"),
        (FACT_IDENTITY, FACT_CURRENT_STATUS),
        (E_PASSPORT, EvidenceItem("right_of_residence_basis", "Work/study/funds/family basis", "Shows the basis for right of residence.", ("employment", "study", "funds", "family"))),
        ("not_standard_permit_route",),
        (SOURCE_WORK_EMPLOYEE, SOURCE_APPLY),
    ),
    _route(
        "swiss_citizen_residence",
        "swiss",
        "apply",
        "Swiss citizen residence permit",
        "For Swiss citizens staying in Sweden more than three months.",
        ("swiss", "residence", "work", "study", "self_support"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_CURRENT_STATUS),
        (E_PASSPORT, E_FUNDS),
        ("swiss_specific_route_check",),
        (SOURCE_APPLY,),
    ),
    _route(
        "british_residence_status",
        "british",
        "apply_or_card",
        "British citizens / residence status",
        "For British citizens and family members under post-Brexit residence-status routes.",
        ("british", "residence_status", "brexit"),
        (FACT_IDENTITY, FACT_CURRENT_STATUS),
        (E_PASSPORT, EvidenceItem("residence_status_evidence", "Residence status evidence", "Shows eligibility/status under British citizen route.", ("residence_status_card",))),
        ("brexit_status_check",),
        (SOURCE_APPLY,),
    ),
    _route(
        "asylum_international_protection",
        "protection",
        "apply",
        "International protection / asylum",
        "For people seeking protection in Sweden.",
        ("asylum", "protection", "refugee", "subsidiary_protection"),
        (FACT_IDENTITY, FACT_LOCATION),
        (E_PASSPORT, EvidenceItem("protection_claim", "Protection claim and supporting evidence", "Explains protection grounds and evidence.", ("asylum_story", "country_evidence"))),
        ("high_sensitivity_boundary_review", "do_not_autonomously_complete_final_claim"),
        (SOURCE_APPLY,),
    ),
    _route(
        "temporary_protection_ukraine",
        "protection",
        "apply_or_extend",
        "Temporary Protection Directive",
        "For people covered by EU temporary protection, including Ukraine-related protection.",
        ("temporary_protection", "ukraine", "protection_directive"),
        (FACT_IDENTITY, FACT_LOCATION, FACT_CURRENT_STATUS),
        (E_PASSPORT, EvidenceItem("temporary_protection_basis", "Temporary protection basis", "Shows eligibility under the directive.", ("ukraine_documents", "residence_history"))),
        ("benefits_housing_support_change_check", "switching_route_risk"),
        (SOURCE_APPLY, SOURCE_EXTEND),
    ),
    _route(
        "alien_passport_travel_document",
        "travel_document",
        "apply",
        "Alien's passport or travel document",
        "For people who cannot obtain a passport from country of origin.",
        ("travel_document", "alien_passport", "emergency_alien_passport"),
        (FACT_IDENTITY, FACT_CURRENT_STATUS),
        (EvidenceItem("identity_documents", "Identity documents", "Shows identity and inability to obtain normal passport.", ("passport_refusal", "identity_card")),),
        ("identity_and_country_document_check",),
        (SOURCE_APPLY,),
    ),
    _route(
        "citizenship_adult",
        "citizenship",
        "apply",
        "Swedish citizenship for adults",
        "For adults applying to become Swedish citizens.",
        ("citizenship", "adult", "identity", "habitual_residence", "good_conduct"),
        (FACT_IDENTITY, FACT_CURRENT_STATUS, FactItem("habitual_residence", "Habitual residence period", "Citizenship depends on lawful residence period.")),
        (E_PASSPORT, EvidenceItem("identity_proof", "Identity proof", "Shows identity.", ("identity_card",)), EvidenceItem("residence_history", "Residence history", "Shows habitual residence.", ("population_register", "permit_history"))),
        ("identity_strictness_check", "good_conduct_check", "security_check"),
        (SOURCE_CITIZENSHIP, SOURCE_CITIZENSHIP_ADULT),
    ),
    _route(
        "citizenship_child",
        "citizenship",
        "apply_or_notify",
        "Swedish citizenship for children",
        "For child citizenship applications, notifications, or automatic-citizenship checks.",
        ("citizenship", "child", "stateless_child", "automatic_citizenship"),
        (FACT_IDENTITY, FACT_FAMILY, FACT_CURRENT_STATUS),
        (E_PASSPORT, E_RELATIONSHIP, EvidenceItem("custody_documents", "Custody documents", "Shows guardian authority/consent.", ("custody",))),
        ("child_identity_check", "custody_check", "personal_appearance_check"),
        (SOURCE_CITIZENSHIP,),
    ),
    _route(
        "citizenship_nordic",
        "citizenship",
        "notification",
        "Swedish citizenship for Nordic citizens",
        "For Nordic citizens using the notification path.",
        ("citizenship", "nordic", "notification"),
        (FACT_IDENTITY, FactItem("nordic_citizenship", "Nordic citizenship", "Route depends on Nordic citizenship."), FactItem("five_year_residence", "Five years residence", "Nordic notification route requires residence period.")),
        (E_PASSPORT, EvidenceItem("residence_history", "Residence history", "Shows period of habitual residence.", ("population_register",))),
        ("prison_sentence_check",),
        (SOURCE_CITIZENSHIP,),
    ),
    _route(
        "appeal_decision",
        "appeal",
        "appeal",
        "Appeal a migration decision",
        "For rejected decisions or court judgments where appeal or leave to appeal may be possible.",
        ("appeal", "rejection", "court", "deadline", "leave_to_appeal"),
        (FACT_IDENTITY, FACT_REJECTION),
        (E_DECISION, E_APPEAL_DEADLINE, E_PASSPORT),
        ("decision_specific_deadline_controls", "do_not_file_without_review", "removal_order_check"),
        (SOURCE_APPEAL,),
    ),
)


ROUTES_BY_ID: dict[str, PermitRoute] = {route.route_id: route for route in PERMIT_ROUTES}


def route_families() -> list[str]:
    return sorted({route.family for route in PERMIT_ROUTES})


def serialize_route(route: PermitRoute) -> dict[str, Any]:
    return route.to_dict()

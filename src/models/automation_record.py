"""Data model for a single automation record."""

from dataclasses import dataclass


@dataclass
class AutomationRecord:
    """
    Represents a single automation record from the MS List.

    All string fields are already cleaned/transformed (HTML stripped,
    JSON arrays joined, booleans converted, dates formatted).
    Empty values are represented as '—'.
    """

    # Section 1 — Identificació
    process_name: str = ""
    automation_name: str = ""
    internal_id: str = ""
    version: str = ""
    repository: str = ""
    last_update_date: str = ""
    current_process_description: str = ""

    # Section 2 — Context
    automated_process_description: str = ""

    # Section 3 — Responsabilitats
    product_owner: str = ""       # Propietari de l'automatització (Creat per in signatures)
    process_owner: str = ""       # Propietari del procés de negoci
    software_architect: str = ""  # Arquitecte de software (Responsable in signatures)
    manager: str = ""             # Manager (also signs the record)
    developers: str = ""          # Desenvolupadors
    user_units: str = ""          # Unitats i persones usuàries
    output_receivers: str = ""    # Persones i/o unitats que reben l'output
    input_feeders: str = ""       # Persones i/o unitats que alimenten l'input

    # Section 4 — Detalls Tècnics
    automation_type: str = ""
    technology: str = ""
    data_sources: str = ""
    expected_output: str = ""
    execution_frequency: str = ""
    dependencies_credentials: str = ""  # Dependències, credencials i permisos (combined)

    # Section 5 — Beneficis
    benefits: str = ""

    # Section 6 — Estat i Roadmap
    current_status: str = ""
    estimated_dev_time: str = ""
    implementation_deadline: str = ""
    future_improvements: str = ""

    # Section 7 — Seguretat i Compliance
    risks: str = ""

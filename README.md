# ASANA_workspace_simulation

Asana Workspace Simulation – Seed Data Generator
Overview :-

This repository contains a reproducible data generation pipeline that simulates a realistic Asana-like enterprise workspace.
The generated dataset is designed to serve as high-quality seed data for reinforcement learning (RL) environments and computer-use agents operating in project management workflows.

The simulation models how a large B2B SaaS company (5,000–10,000 employees) uses Asana across engineering, product, marketing, and operations teams, with realistic task hierarchies, timelines, and metadata.

The output is a fully populated SQLite database suitable for downstream evaluation, training, or environment simulation.

Key Design Goals:

Realism over simplicity
Avoids synthetic shortcuts such as uniform due dates, generic task names, or flat hierarchies.

Enterprise-scale structure
Models multi-team organizations, matrix memberships, cross-project collaboration, and governance features like custom fields.

Reproducible & offline-safe
Pipeline runs deterministically without requiring external APIs or credentials.

Extensible by design
Optional hooks exist for scraping and LLM-based enrichment, gated behind feature flags.

Simulated Asana Entities

The dataset includes the following core entities:

Organizations / Workspaces
Users (admins, members, guests)
Teams and Team Memberships
Projects and Sections
Tasks and Subtasks
Task–Project–Section mappings
Comments / Activity
Custom Field Definitions
Project-specific Custom Fields
Task-level Custom Field Values
Tags and Task–Tag associations
All relationships are enforced via foreign keys and generated with realistic distributions.


Key Files

schema.sql – Complete SQLite schema (DDL)
src/main.py – Orchestrates the full data generation pipeline
src/generators/ – Table-specific data generation logic
src/scrapers/ – Optional public-data scraping utilities
output/asana_simulation.sqlite – Final generated database
External Data Sources

The pipeline uses public, non-sensitive data sources only.

Tech Companies and Startups Dataset (CSV)
GitHub repository used for organization name sampling:

No proprietary, private, or personally identifiable information is used.

Setup Instructions
1) Clone the repository
2) Install dependencies
3) Configure environment :- Create a .env file in the repository root:
4) Run the pipeline :- python src/main.py
5) After successful execution, the generated SQLite database will be available at :- output/asana_simulation.sqlite
6) You can inspect it using :- sqlite3 output/asana_simulation.sqlite

License & Ethics

This project uses only synthetic or publicly available data.
All generated user information is fictional.
The dataset is designed with privacy, ethics, and reproducibility in mind.



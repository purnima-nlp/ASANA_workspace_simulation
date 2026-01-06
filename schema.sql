-- Enable foreign key enforcement (CRITICAL for SQLite)
PRAGMA foreign_keys = ON;

-- =========================
-- Organizations / Workspaces
-- =========================
CREATE TABLE organizations (
    org_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    plan_type TEXT,
    created_at TEXT NOT NULL,
    is_active INTEGER DEFAULT 1
);

-- =====
-- Users
-- =====
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role TEXT CHECK (role IN ('admin', 'member', 'guest')),
    created_at TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

-- =====
-- Teams
-- =====
CREATE TABLE teams (
    team_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

-- =================
-- Team Memberships
-- =================
CREATE TABLE team_memberships (
    team_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT CHECK (role IN ('member', 'lead')),
    joined_at TEXT NOT NULL,
    PRIMARY KEY (team_id, user_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- =========
-- Projects
-- =========
CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT CHECK (status IN ('active', 'archived')),
    created_at TEXT NOT NULL,
    due_date TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- =========
-- Sections
-- =========
CREATE TABLE sections (
    section_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    position INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- =====
-- Tasks
-- =====
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    parent_task_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    assignee_id TEXT,
    due_date TEXT,
    priority TEXT CHECK (priority IN ('low', 'medium', 'high')),
    status TEXT CHECK (status IN ('todo', 'in_progress', 'completed')),
    created_at TEXT NOT NULL,
    completed_at TEXT,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id),
    FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (assignee_id) REFERENCES users(user_id)
);

-- =======================
-- Task–Project Association
-- =======================
CREATE TABLE task_projects (
    task_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    section_id TEXT,
    PRIMARY KEY (task_id, project_id),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (section_id) REFERENCES sections(section_id)
);

-- =========
-- Comments
-- =========
CREATE TABLE comments (
    comment_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- =========================
-- Custom Field Definitions
-- =========================
CREATE TABLE custom_field_definitions (
    field_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    name TEXT NOT NULL,
    field_type TEXT CHECK (field_type IN ('text', 'number', 'enum', 'date')),
    created_at TEXT NOT NULL,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

-- ======================
-- Project Custom Fields
-- ======================
CREATE TABLE project_custom_fields (
    project_id TEXT NOT NULL,
    field_id TEXT NOT NULL,
    is_required INTEGER DEFAULT 0,
    PRIMARY KEY (project_id, field_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (field_id) REFERENCES custom_field_definitions(field_id)
);

-- ===================
-- Custom Field Values
-- ===================
CREATE TABLE custom_field_values (
    task_id TEXT NOT NULL,
    field_id TEXT NOT NULL,
    value_text TEXT,
    value_number REAL,
    value_date TEXT,
    value_enum TEXT,
    PRIMARY KEY (task_id, field_id),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (field_id) REFERENCES custom_field_definitions(field_id)
);

-- ====
-- Tags
-- ====
CREATE TABLE tags (
    tag_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

-- =================
-- Task–Tag Mapping
-- =================
CREATE TABLE task_tags (
    task_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    PRIMARY KEY (task_id, tag_id),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);


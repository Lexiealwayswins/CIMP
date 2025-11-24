# CIMP - Campus Information Management Platform

**CIMP** is a robust backend system built with Python and Django, designed to provide a comprehensive information management solution for campus environments.

The system integrates Role-Based Access Control (RBAC), a Content Management System (Notice/News), Academic Paper Management, and a highly configurable, **Data-Driven Graduate Design Workflow Engine**.

## 🛠 Tech Stack

  * **Language**: Python 3.x
  * **Framework**: Django 3.x/4.x
  * **Database**: SQLite (Dev) / MySQL (Prod supported)
  * **API Interaction**: JSON (RESTful design)
  * **Architecture**: MVT (Model-View-Template), primarily functioning as a decoupled API service.

## ✨ Core Features

### 1\. RBAC (Role-Based Access Control)

Supports a multi-role user system where different roles have distinct API access permissions:

  * **Superuser**: System configuration and user management.
  * **Admin (Staff)**: Content moderation, publishing notices and news.
  * **Teacher**: Reviewing graduate designs, grading, and managing student associations.
  * **Student**: Submitting designs, viewing grades, and selecting supervisors.

### 2\. Content Management System (CMS)

  * **Notices & News**: Full lifecycle management including publishing, withdrawing, banning, and deleting.
  * **Academic Papers**: Repository for students/teachers to upload papers with social interaction features (likes/thumb-ups).

### 3\. Profile & Supervisor Selection

  * Maintains Student-Teacher relationships via the `Profile` model.
  * Allows students to browse and select their academic supervisors.

### 4\. 🚀 Highlight: Configurable Workflow Engine

This feature implements a **Finite State Machine (FSM)** for business processes (specifically Graduate Designs).

  * **Data-Driven Design**: All workflow rules, permission logic, and form field definitions are stored in a configuration dictionary (`WF_RULE`) within `models.py`, rather than hardcoded in business logic.
  * **High Extensibility**: Adding approval steps or modifying transition logic only requires updating the configuration, not rewriting code.
  * **Universal API**: A single `stepaction` endpoint handles all state transitions.

**Workflow Cycle:**

> Start -\> Student Creates Topic -\> Teacher Reviews -\> (Reject/Approve) -\> Student Submits Design -\> Teacher Grades -\> End

## 📂 Project Structure

```bash
CIMP/
├── manage.py
├── config/               # Project settings (settings.py, etc.)
│   └── settings.py       # Contains UPLOAD_DIR configuration
├── lib/
│   └── share.py          # Utility library (JSON Response wrapper)
├── main/                 # Core Application
│   ├── models.py         # Data Models & Workflow Configuration (WF_RULE)
│   ├── views.py          # Request Handlers (Dispatcher Pattern)
│   └── urls.py           # URL Routing
└── upload/               # Static file upload directory
```

## 🚀 Quick Start

### 1\. Prerequisites

```bash
# Clone the repository
git clone <your-repo-url>
cd CIMP

# Install dependencies (assuming requirements.txt exists)
pip install django
```

### 2\. Database Initialization

```bash
# Generate migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 3\. Create Superuser

```bash
python manage.py createsuperuser
# Follow prompts to set username (e.g., admin) and password.
# Note: After creation, ensure the 'usertype' field is set appropriately (Recommended: 1) in the database.
```

### 4\. Run Server

```bash
python manage.py runserver
```

## 🔌 API Usage Examples

All interfaces use `POST` requests with JSON bodies (unless specified otherwise).

### 1\. User Login

**URL**: `/api/sign`

```json
{
  "action": "signin",
  "username": "student1",
  "password": "password123"
}
```

### 2\. Workflow Engine - Execute Action

**URL**: `/api/wf_graduatedesign`

This is a universal endpoint. The operation performed depends on the `key` parameter defined in the config.

**Example: Teacher Approves a Topic**

```json
{
  "action": "stepaction",
  "wf_id": 15,             // Workflow ID
  "key": "approve_topic",  // Operation Key (from config)
  "submitdata": [          // Form data required for this step
    {
      "name": "Comments",
      "type": "richtext",
      "value": "Topic approved. Please proceed."
    }
  ]
}
```

### 3\. Check Available Actions (What Can I Do?)

**URL**: `/api/wf_graduatedesign`

```json
{
  "action": "getone",
  "wf_id": 15,
  "withwhatcanido": true
}
```

*The response will dynamically return the buttons and form definitions valid for the current user in the current state.*

## 📝 Development Notes

1.  **Upload Directory**: Ensure an `upload` folder exists in the project root, or confirm `UPLOAD_DIR` is correctly configured in `settings.py`.
2.  **Postman Testing**:
      * For file uploads (`/api/upload`), set the Body type to `form-data`. Set the Key to `upload1` and change the input type from Text to **File**.
      * For other endpoints, use `raw` -\> `JSON`.
      * Ensure the request includes the `sessionid` Cookie after logging in.

-----

**Author**: Lexie
**Last Updated**: November 2025
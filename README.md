# Smart Task Tracker

**Project Description:**
- Build a team productivity tracking system where users can create tasks, assign them, track time spent, and  generate performance analytics.

- A Django REST Framework (DRF) based backend system designed to manage user productivity, track tasks, monitor time spent and generate performance analytics.

**Project: smart-task-tracker**

**Apps:**
1. accounts
2. workspace
3. projects
4. tasks
5. analytics

# Project Overview:
- The Smart Task Tracker allows users to:
* Manage tasks within projects and workspaces
* Assign tasks to team members
* Track time spent on tasks
* Monitor productivity using analytics
* Generate reports and export csv via email

# Tech Stack:
* Backend: Django, Django REST Framework
* Database: PostgreSQL
* Authentication: JWT Authentication
* API Testing: Postman
* Other Tools: Django Filters, CSV module, Email (SMTP)

# Features

**1. Accounts Module**
* User Registration & Login (JWT Authentication)
* Secure authentication system
* Soft delete support
* Unique email validation with soft-delete handling

**2. Workspace Management**
* CRUD operations for workspaces
* Add and remove members to workspace
* Role-based access (Owner, Member)
* Only workspace members can access related data

**3. Project Management**
* CRUD operations for projects
* Projects belong to workspaces
* Assign workspace members to projects
* Soft delete support
* Access control based on workspace ownership

**4. Project Member Assignment**
* Assign users to projects
* Update roles (Developer, Manager)
* Prevent duplicate assignment
* Validate workspace membership before assigning

**5. Task Module**
**1. Task Management**
* Create, update, delete tasks
* Assign tasks to project members
* Add priority (Low, Medium, High)
* Set deadlines
    
**2. Task Status Workflow**
* Todo --> In Progress --> Done
* Controlled transitions (optional validation)

**3. Permissions**
* Creator --> Full access
* Assignee --> Can update only status

**6. Time Tracking (TimeLog)**
* Log time spent on tasks
* Add description for work done
* Retrieve total time per task
* Only project members can log time

**7. Analytics Module**
**1. User Analytics**
* Total tasks assigned
* Completed tasks
* Total time spent

**2. Productivity Score**
* Productivity Score = (Completed Tasks / Total Tasks) * 100 + Total Time

**3. Reports**
* Weekly report
* Monthly report

**4. Overdue Tasks**
* Tasks with deadline passed and not completed

**8. Filtering & Search**
**1. Filter tasks by:**
* Priority
* Status
* Assigned user

**2. Search tasks by:**
* Title

**9. CSV Export & Email Feature**
* Export analytics data into CSV
* Send report via email
* On-demand API trigger

**10. Permissions & Security**
* Role-based access control
* Workspace-level security
* Project-level validation
* Soft delete for all major models
* Restricted update/delete operations
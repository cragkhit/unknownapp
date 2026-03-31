# unknownapp
Course Enrollment System reengineered from a Java CLI application.

## Overview
This repository contains:
- The original Java course enrollment CLI application under `src/`
- A new Python port of the student enrollment use case under `python/enrollment.py`
- Updated documentation with a use case diagram and Mermaid flowchart

## Use Case Diagram
```mermaid
usecaseDiagram
    actor Student
    actor Admin

    Student --> (Login as Student)
    Admin --> (Login as Admin)

    (Login as Student) --> (View Course Catalog)
    (Login as Student) --> (Register for a Course)
    (Login as Student) --> (Drop a Course)
    (Login as Student) --> (View My Schedule)
    (Login as Student) --> (Billing Summary)
    (Login as Student) --> (Edit My Profile)

    (Login as Admin) --> (View Course Catalog)
    (Login as Admin) --> (View Class Roster)
    (Login as Admin) --> (View All Students)
    (Login as Admin) --> (Add New Student)
    (Login as Admin) --> (Edit Student Profile)
    (Login as Admin) --> (Add New Course)
    (Login as Admin) --> (Edit Course)
    (Login as Admin) --> (View Student Schedule)
    (Login as Admin) --> (Billing Summary)
```

## Flowchart of the main workflow
```mermaid
flowchart TD
    A[Start] --> B[Login Menu]
    B --> |Student| C[Enter Student ID or 'new']
    B --> |Admin| D[Enter Admin Password]
    B --> |Exit| Z[Save Data and Exit]

    C --> |new| F[Create Student Profile]
    C --> |valid| E[Student Menu]
    C --> |invalid| B
    F --> E

    E[Student Menu] --> E1[View Course Catalog]
    E --> E2[Register for Course]
    E --> E3[Drop Course]
    E --> E4[View Schedule]
    E --> E5[Billing Summary]
    E --> E6[Edit Profile]
    E --> E7[Logout and Save]
    E7 --> B

    D --> |valid| G[Admin Menu]
    D --> |invalid| B
    G --> G1[View Course Catalog]
    G --> G2[View Roster / Student Info]
    G --> G3[Add / Edit Students or Courses]
    G --> G4[Logout and Save]
    G4 --> B
```

## Python Port
The Python version is located in `python/enrollment.py` and implements the student enrollment use case with:
- student login / profile creation
- course catalog browsing
- registration and drop operations
- schedule display and tuition calculation
- JSON persistence under `python/data/`

### Run the Python version
```bash
python3 python/enrollment.py
```

## Prompts
- "Create a Python CLI version of the student enrollment use case from a Java course enrollment system. It should support student login, view catalog, register/drop courses, view schedule, billing summary, edit profile, and JSON persistence using only Python standard library."

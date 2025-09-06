# Campus Event Reporting System – Design Document

## 1. Data to Track

The system keeps track of:

- **Events** → Title, date, venue, description
- **Students** → Name, email
- **Registrations** → Which students registered for which events
- **Attendance** → Present/Absent for each student in each event
- **Feedback** → Optional comments from students after events

---

## 2. Database Schema

**Tables:**

- **Student** (`id`, `name`, `email`)
- **Event** (`id`, `title`, `date`, `venue`)
- **Registration** (`id`, `student_id`, `event_id`)
- **Attendance** (`id`, `student_id`, `event_id`, `status`)
- **Feedback** (`id`, `student_id`, `event_id`, `comment`)

📌 ER Diagram is saved as:  
`docs/er_diagram.png`

---

## 3. API Design

| Endpoint                    | Method | Description                             |
| --------------------------- | ------ | --------------------------------------- | --- |
| `/events`                   | POST   | Create a new event                      |
| `/students`                 | POST   | Add a student                           |
| `/register`                 | POST   | Register a student for an event         |
| `/attendance`               | POST   | Mark student’s attendance               |
| `/feedback`                 | POST   | Submit feedback                         |
| `/reports/event-popularity` | GET    | Report: Events ranked by registrations  |
| `/reports/student/<id>`     | GET    | Report: Student’s participation history |     |
| `/reports/top-students`     | GET    | Report: Top 3 most active students      |

---

## 4. Workflows

### a) Student Registration Workflow

1. Admin creates an event (`/events`)
2. Student registers (`/register`)
3. Entry saved in `Registration` table

### b) Attendance Workflow

1. On event day, admin calls `/attendance`
2. Updates `Attendance` table with Present/Absent

### c) Reporting Workflow

1. Reports pulled from database via `/reports/...`
2. SQL queries aggregate data

_(See `docs/reports/` for screenshots of reports run in Postman.)_

---

## 5. Assumptions & Edge Cases

- **Duplicate registrations** are prevented.
- **Feedback** is optional.
- **Cancelled events** are marked as cancelled, not deleted.
- **Unmarked attendance** → default = Absent.

---

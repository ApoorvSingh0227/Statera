from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import connection
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from datetime import date

from .models import Employee, Department, Project, Task

def register(request):
    if request.method == "POST":
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']
        email = request.POST['email']
        phone = request.POST['phone']
        hire_date = request.POST['hire-date']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']

        # Validate password confirmation
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        # Hash the password
        hashed_password = make_password(password)

        # Insert the data into the Employee table
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Employee (firstName, lastName, email, phone, hireDate, password)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    [first_name, last_name, email, phone, hire_date, hashed_password]
                )
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('register')

    return render(request, 'statera register.html')

def dashboard(request):
    if 'employee_id' not in request.session:
        return redirect('login')
    
    employee_id = request.session['employee_id']
    tasks = []
    projects = []

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT firstName, lastName FROM Employee WHERE employeeID = %s", [employee_id])
            user = cursor.fetchone()
            first_name = user[0]
            last_name = user[1]
    except Exception as e:
        first_name, last_name = '', ''

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    t.taskID,
                    t.taskName, 
                    p.projectID,
                    p.projectName, 
                    t.status, 
                    t.priority, 
                    t.estimatedHours,
                    t.actualHours,
                    t.dueDate
                FROM Task t
                JOIN Project p ON t.projectID = p.projectID
                WHERE t.assignedTo = %s
                """,
                [employee_id]
            )
            tasks = cursor.fetchall()
            
            updated_tasks = []
        for task in tasks:
            estimated_hours = task[4]
            actual_hours = task[5]
            if estimated_hours and actual_hours:  # Ensure values are not None or 0
                progress = (actual_hours / estimated_hours) * 100
            else:
                progress = 0
            updated_tasks.append((*task, progress))  # Append with progress

        tasks = updated_tasks
            
    except Exception as e:
        print(f"Error fetching tasks: {e}")

    return render(request, 'statera dashboard.html', {'tasks': tasks,
        'first_name': first_name,
        'last_name': last_name})

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT employeeID, password FROM Employee WHERE email = %s", [email]
                )
                result = cursor.fetchone()

            if result:
                employee_id, hashed_password = result
                if check_password(password, hashed_password):  # Verify password
                    # Simulate user login (use session or authentication system)
                    request.session['employee_id'] = employee_id  # Store session
                    messages.success(request, "Login successful!")
                    return redirect('dashboard')  # Redirect to the homepage
                else:
                    messages.error(request, "Invalid password!")
            else:
                messages.error(request, "User does not exist!")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, 'home.html')

def project_main(request, project_id):
    if 'employee_id' not in request.session:
        return redirect('login')
    
    try:
        # Fetch project details (name, manager, description, due date, progress)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    p.projectName,
                    CONCAT(e.firstName, ' ', e.lastName) AS managerName,
                    p.description,
                    MAX(t.dueDate) AS dueDate,
                    SUM(t.actualHours) AS actualHours,
                    SUM(t.estimatedHours) AS estimatedHours
                FROM Project p
                LEFT JOIN Employee e ON p.projectManagerID = e.employeeID
                LEFT JOIN Task t ON t.projectID = p.projectID
                WHERE p.projectID = %s
                GROUP BY p.projectID, e.firstName, e.lastName, p.description
                """,
                [project_id]
            )
            project = cursor.fetchone()

        if project:
            project_name = project[0]
            manager_name = project[1] if project[1] else "Unassigned"
            description = project[2] if project[2] else "No description provided."
            due_date = project[3] if project[3] else "N/A"
            actual_hours = project[4] or 0
            estimated_hours = project[5] or 0
            progress = (actual_hours / estimated_hours) * 100 if estimated_hours else 0
        else:
            project_name = "Project not found"
            manager_name = "-"
            description = "-"
            due_date = "-"
            progress = 0

        # Fetch task list for the project
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    t.taskID, t.taskName
                FROM Task t
                WHERE t.projectID = %s
                """,
                [project_id]
            )
            tasks = cursor.fetchall()

        # Fetch participant list
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    CONCAT(e.firstName, ' ', e.lastName) AS participantName,
                    t.taskName,
                    t.dueDate,
                    SUM(t.actualHours) AS actualHours,
                    t.estimatedHours,
                    t.taskID,
                    e.employeeID
                FROM Task t
                JOIN Employee e ON t.assignedTo = e.employeeID
                WHERE t.projectID = %s
                GROUP BY e.employeeID, t.taskName, t.dueDate, t.estimatedHours, t.taskID
                """,
                [project_id]
            )
            participants = cursor.fetchall()

        processed_participants = []
        for participant in participants:
            actual = participant[3] or 0
            estimated = participant[4] or 1  # Avoid division by zero
            progress = (actual / estimated) * 100 if estimated else 0
            processed_participants.append((*participant, progress))
        participants = processed_participants

    except Exception as e:
        project_name = "Error fetching project details"
        manager_name = "-"
        description = "-"
        due_date = "-"
        progress = 0
        tasks = []
        participants = []

    return render(request, 'statera projectmain.html', {
        'project_name': project_name,
        'manager_name': manager_name,
        'description': description,
        'due_date': due_date,
        'progress': progress,
        'tasks': tasks,
        'participants': participants,
        'actual_hours':actual_hours,
        'estimated_hours':estimated_hours
        })

def task_info(request, task_id):
    if 'employee_id' not in request.session:
        return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    t.taskName, 
                    p.projectName, 
                    p.projectID, 
                    t.description, 
                    t.dueDate, 
                    t.actualHours, 
                    t.estimatedHours
                FROM Task t
                JOIN Project p ON t.projectID = p.projectID
                WHERE t.taskID = %s
                """,
                [task_id]
            )
            task = cursor.fetchone()
            
            if task:
                task_name = task[0]
                project_name = task[1]
                project_id = task[2]
                description = task[3] if task[3] else "No description provided."
                due_date = task[4] if task[4] else "N/A"
                actual_hours = task[5] or 0
                estimated_hours = task[6] or 1 
                progress = (actual_hours / estimated_hours) * 100 if estimated_hours else 0
            else:
                task_name = "-"
                project_name = "-"
                project_id = None
                description = "-"
                due_date = "-"
                progress = 0

    except Exception as e:
        task_name = "Error fetching task details"
        project_name = "Error fetching project details"
        project_id = None
        description = "-"
        due_date = "-"
        progress = 0

    return render(request, 'statera task info.html', {
        'task_id': task_id,
        'task_name': task_name,
        'project_name': project_name,
        'project_id': project_id,
        'description': description,
        'due_date': due_date,
        'progress': progress,
        'actual_hours': actual_hours,
        'estimated_hours': estimated_hours,
        })

def update_information(request):
    if 'employee_id' not in request.session:
        return redirect('login')

    employee_id = request.session['employee_id']

    if request.method == "POST":
        selected_skills = request.POST.getlist('skills', [])
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        position = request.POST.get('position', '').strip()
        hire_date = request.POST.get('hire_date', '').strip()
        department = request.POST.get('department', '').strip()

        try:
            with connection.cursor() as cursor:
                # Remove old skills
                cursor.execute(
                    """
                    DELETE FROM EmployeeSkills
                    WHERE employeeID = %s
                    """,
                    [employee_id]
                )
                # Add new skills
                for skill_id in selected_skills:
                    cursor.execute(
                        """
                        INSERT INTO EmployeeSkills (employeeID, skillID)
                        VALUES (%s, %s)
                        """,
                        [employee_id, skill_id]
                )
        except Exception as e:
            messages.error(request, f"Error updating skills: {e}")
            
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE Employee
                    SET firstName = %s, lastName = %s, email = %s, phone = %s,
                        position = %s, hireDate = %s, departmentID = (
                            SELECT departmentID FROM Department WHERE departmentName = %s
                        )
                    WHERE employeeID = %s
                    """,
                    [first_name, last_name, email, phone, position, hire_date, department, employee_id]
                )
            messages.success(request, "Information updated successfully!")
            return redirect('employee_info', employee_id=employee_id)
        except Exception as e:
            messages.error(request, f"Error updating information: {e}")
            return redirect('update-information')

    # Fetch current employee info
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    e.firstName, e.lastName, e.email, e.phone, e.hireDate, e.position, d.departmentName
                FROM Employee e
                LEFT JOIN Department d ON e.departmentID = d.departmentID
                WHERE e.employeeID = %s
                """,
                [employee_id]
            )
            employee = cursor.fetchone()

            cursor.execute("SELECT departmentName FROM Department")
            departments = [row[0] for row in cursor.fetchall()]

            if not employee:
                messages.error(request, "Employee record not found.")
                return redirect('dashboard')

            cursor.execute(
                """
                SELECT 
                    s.skillID, s.skillName
                FROM Skill s
                JOIN EmployeeSkills es ON s.skillID = es.skillID
                WHERE es.employeeID = %s
                """,
                [employee_id]
            )
            employee_skills = [row for row in cursor.fetchall()]

            cursor.execute("SELECT skillID, skillName FROM Skill")
            all_skills = [row for row in cursor.fetchall()]
        
        if employee:
            context = {
                'first_name': employee[0],
                'last_name': employee[1],
                'email': employee[2],
                'phone': employee[3],
                'hire_date': employee[4],
                'position': employee[5],
                'department': employee[6] if employee[6] else "Unassigned",
                'employee_skills': employee_skills,
                'skills': all_skills,
                'departments': departments,
            }
        else:
            messages.error(request, "Employee not found.")
            return redirect('dashboard')

    except Exception as e:
        messages.error(request, f"Error fetching information: {e}")
        return redirect('dashboard')

    return render(request, 'statera updateinfo.html', context)

def employee_info(request, employee_id):
    if 'employee_id' not in request.session:
        return redirect('login')

    session_employee_id = request.session['employee_id']  # Current logged-in user's ID
    is_own_profile = session_employee_id == employee_id

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    e.firstName,
                    e.lastName,
                    e.email,
                    e.phone,
                    e.hireDate,
                    d.departmentName,
                    e.position
                FROM Employee e
                LEFT JOIN Department d ON e.departmentID = d.departmentID
                WHERE e.employeeID = %s
                """,
                [employee_id]
            )
            employee = cursor.fetchone()
  
            cursor.execute(  
                """  
                SELECT 
                    s.skillName  
                FROM EmployeeSkills es  
                JOIN Skill s ON es.skillID = s.skillID  
                WHERE es.employeeID = %s  
                """,  
                [employee_id]  
            )  
            skills = [row[0] for row in cursor.fetchall()]  

        if employee:
            full_name = f"{employee[0]} {employee[1]}"
            email = employee[2]
            phone = employee[3]
            hire_date = employee[4]
            department = employee[5] if employee[5] else "Unassigned"
            position = employee[6] if employee[6] else "Not specified"
        else:
            full_name = "N/A"
            email = "N/A"
            phone = "N/A"
            hire_date = "N/A"
            department = "N/A"
            position = "N/A"
            skills = []

    except Exception as e:
        full_name = "Error fetching data"
        email = "-"
        phone = "-"
        hire_date = "-"
        department = "-"
        position = "-"
        skills = []
        print(f"Error: {e}")
        
    return render(request, 'statera empinfo.html', {
        'full_name': full_name,
        'email': email,
        'phone': phone,
        'hire_date': hire_date,
        'department': department,
        'position': position,
        'skills': skills,
        'is_own_profile': is_own_profile,
        'employee_id': employee_id,
    })
    
    
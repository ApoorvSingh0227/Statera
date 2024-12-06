from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import connection
from django.contrib.auth.hashers import check_password

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
        with connection.cursor() as cursor:
            cursor.execute("SELECT projectName FROM Project WHERE projectID = %s", [project_id])
            project = cursor.fetchone()
            project_name = project[0] if project else "Project not found"
    except Exception as e:
        project_name = "Error fetching project details"

    return render(request, 'statera projectmain.html', {'project_name': project_name})

def task_info(request, task_id):
    if 'employee_id' not in request.session:
        return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT t.taskName, p.projectName, p.projectID
                FROM Task t
                JOIN Project p ON t.projectID = p.projectID
                WHERE t.taskID = %s
                """,
                  [task_id])
            task = cursor.fetchone()
            if task:
                task_name = task[0]  # First column: taskName
                project_name = task[1]  # Second column: projectName
                project_id = task[2]  # Project ID
            else:
                task_name = "-"
                project_name = "-"
                project_id = None
    except Exception as e:
        task_name = "Error fetching task details"
        project_name = "Error fetching project details"
        project_id = None

    return render(request, 'statera task info.html', {'task_id': task_id, 'task_name':task_name, 'project_name': project_name ,'project_id': project_id})

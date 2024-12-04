from django.db import models

from django.db import models

# Department model
class Department(models.Model):
    departmentID = models.AutoField(primary_key=True)
    departmentName = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True)
    managerID = models.ForeignKey(
        'Employee', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_departments'  # Custom reverse name
    )

    def __str__(self):
        return self.departmentName


# Employee model
class Employee(models.Model):
    employeeID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    hireDate = models.DateField()
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='employees'  # Custom reverse name for clarity
    )
    position = models.CharField(max_length=50, null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reportsTo = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='subordinates'
    )

    def __str__(self):
        return f'{self.firstName} {self.lastName}'


# Project model
class Project(models.Model):
    projectName = models.CharField(max_length=100)
    description = models.TextField()
    startDate = models.DateField()
    endDate = models.DateField()
    status = models.CharField(max_length=50)
    budget = models.DecimalField(max_digits=15, decimal_places=2)
    projectManager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.projectName


# Task model
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    taskName = models.CharField(max_length=100)
    description = models.TextField()
    assignedTo = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50)
    priority = models.CharField(max_length=20)
    estimatedHours = models.DecimalField(max_digits=5, decimal_places=2)
    startDate = models.DateField()
    dueDate = models.DateField(null=True, blank=True)
    ETA = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.taskName


# TimeEntry model
class TimeEntry(models.Model):
    date = models.DateField()
    hoursWorked = models.IntegerField()
    description = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.employee} - {self.task} on {self.date}'


from django.db import models
from django.utils import timezone
import uuid

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

    
class ClassSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.class_name

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)

    STATUS_CHOICES = (
        ("INITIATED", "Initiated"),
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("CANCELED", "Canceled"),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_schedule = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE)

    month = models.CharField(max_length=20)  # e.g. "March 2026"
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Rs
    amount_paisa = models.PositiveIntegerField(default=0)          # Rs*100

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="INITIATED")

    # Khalti fields
    purchase_order_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    purchase_order_name = models.CharField(max_length=200, default="Music Class Fee")
    pidx = models.CharField(max_length=100, blank=True, null=True)
    khalti_transaction_id = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.class_schedule.class_name} - {self.month}"


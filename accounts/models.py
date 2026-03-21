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

class Assessment(models.Model):
    assessment_id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    class_schedule = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE)

    title = models.CharField(max_length=150)
    instructions = models.TextField(blank=True, null=True)
    deadline = models.DateField()

    reference_audio = models.FileField(upload_to="assessments/reference/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.class_schedule.class_name})"


class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    student_audio = models.FileField(upload_to="assessments/submissions/")
    comment = models.TextField(blank=True, null=True)

    # teacher grading
    score = models.IntegerField(blank=True, null=True)  # 0-100
    feedback = models.TextField(blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(blank=True, null=True)
    auto_score = models.FloatField(null=True, blank=True)
    pitch_score = models.FloatField(null=True, blank=True)
    rhythm_score = models.FloatField(null=True, blank=True)
    auto_feedback = models.TextField(null=True, blank=True)
    ai_feedback = models.TextField(null=True, blank=True)
    pitch_plot = models.ImageField(upload_to="assessment_graphs/", null=True, blank=True)
    rhythm_plot = models.ImageField(upload_to="assessment_graphs/", null=True, blank=True)

    class Meta:
        unique_together = ("assessment", "student")  # 1 submission per student per assessment

    def __str__(self):
        return f"{self.student.full_name} - {self.assessment.title}"
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import Student, Teacher, ClassSchedule, Payment, Assessment, Submission
import bcrypt
import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from .audio_ai import analyze_audio
from .gemini_feedback import generate_gemini_feedback
from .graph_utils import generate_pitch_plot , generate_rhythm_plot

def home(request):
    return render(request, "home.html")

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            request.session["role"] = "admin"
            request.session["admin"] = True
            return redirect("/panel/dashboard/")
        return render(request, "admin_login.html", {"error": "Invalid admin credentials"})

    return render(request, "admin_login.html")


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get("role") != "admin":
            return redirect("/panel/login/")
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_payments = Payment.objects.count()
    paid_payments = Payment.objects.filter(status="PAID").count()
    pending_payments = Payment.objects.filter(status="PENDING").count()

    students = Student.objects.all().order_by("-student_id")[:10]
    teachers = Teacher.objects.all().order_by("-teacher_id")[:10]
    recent_paid = Payment.objects.filter(status="PAID").order_by("-updated_at")[:10]

    return render(request, "admin_dashboard.html", {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_payments": total_payments,
        "paid_payments": paid_payments,
        "pending_payments": pending_payments,
        "students": students,
        "teachers": teachers,
        "recent_paid": recent_paid,
    })


@admin_required
def admin_students(request):
    students = Student.objects.all().order_by("-student_id")
    return render(request, "admin_students.html", {"students": students})


@admin_required
def admin_teachers(request):
    teachers = Teacher.objects.all().order_by("-teacher_id")
    return render(request, "admin_teachers.html", {"teachers": teachers})


@admin_required
def admin_payments(request):
    payments = Payment.objects.all().order_by("-updated_at")
    return render(request, "admin_payments.html", {"payments": payments})


@admin_required
def admin_delete_student(request, student_id):
    s = get_object_or_404(Student, student_id=student_id)
    s.delete()
    return redirect("/panel/students/")


@admin_required
def admin_delete_teacher(request, teacher_id):
    t = get_object_or_404(Teacher, teacher_id=teacher_id)
    t.delete()
    return redirect("/panel/teachers/")


def admin_logout(request):
    request.session.flush()
    return redirect("/panel/login/")

def logout_view(request):
    request.session.flush()
    return redirect("/login/")


def student_register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']

        if Student.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('student_register')

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        Student.objects.create(
            full_name=name,
            email=email,
            phone=phone,
            password=hashed,
            is_verified=True   
        )

        messages.success(request, "Student registered successfully")
        return redirect('login')

    return render(request, 'student_register.html')


def teacher_register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']

        if Teacher.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('teacher_register')

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        Teacher.objects.create(
            full_name=name,
            email=email,
            phone=phone,
            password=hashed,
            is_verified=True
        )

        messages.success(request, "Teacher registered successfully")
        return redirect('login')

    return render(request, 'teacher_register.html')

def loginPage(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # check student
        try:
            student = Student.objects.get(email=email)
            if bcrypt.checkpw(password.encode(), student.password.encode()):
                request.session['user_id'] = student.student_id
                request.session['role'] = 'student'
                return redirect('student_dashboard')
        except:
            pass

        # check teacher
        try:
            teacher = Teacher.objects.get(email=email)
            if bcrypt.checkpw(password.encode(), teacher.password.encode()):
                request.session['user_id'] = teacher.teacher_id
                request.session['role'] = 'teacher'
                return redirect('teacher_dashboard')
        except:
            pass

        messages.error(request, "Invalid credentials")

    return render(request, 'login.html')


def student_dashboard(request):
    if request.session.get("role") != "student":
        return redirect("/login/")

    sid = request.session.get("user_id")
    student = get_object_or_404(Student, student_id=sid)

    classes = ClassSchedule.objects.all()

    return render(request, 'student_dashboard.html', {
        'student': student,
        'classes': classes
    })

def teacher_dashboard(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    tid = request.session.get("user_id")
    teacher = get_object_or_404(Teacher, teacher_id=tid)

    total_classes = ClassSchedule.objects.filter(teacher=teacher).count()
    total_assessments = Assessment.objects.filter(teacher=teacher).count()

    pending_submissions = Submission.objects.filter(
        assessment__teacher=teacher,
        score__isnull=True
    ).count()

    recent_classes = ClassSchedule.objects.filter(teacher=teacher).order_by("-date")[:5]
    recent_assessments = Assessment.objects.filter(teacher=teacher).order_by("-created_at")[:5]

    return render(request, "teacher_dashboard.html", {
        "teacher": teacher,
        "total_classes": total_classes,
        "total_assessments": total_assessments,
        "pending_submissions": pending_submissions,
        "recent_classes": recent_classes,
        "recent_assessments": recent_assessments,
    })


def teacher_profile(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    tid = request.session.get("user_id")
    teacher = get_object_or_404(Teacher, teacher_id=tid)
    return render(request, "teacher_profile.html", {"teacher": teacher})

def student_profile(request):
    if request.session.get("role") != "student":
        return redirect("/login/")

    sid = request.session.get("user_id")
    student = get_object_or_404(Student, student_id=sid)

    return render(request, "student_profile.html", {"student": student})

def student_payment(request):
    return render(request, 'student_payments.html')

def create_class(request):
    if request.method == 'POST':
        class_name = request.POST['class_name']
        date = request.POST['date']
        start = request.POST['start_time']
        end = request.POST['end_time']

        teacher_id = request.session.get('user_id')
        teacher = Teacher.objects.get(teacher_id=teacher_id)

        ClassSchedule.objects.create(
            teacher=teacher,
            class_name=class_name,
            date=date,
            start_time=start,
            end_time=end
        )

        return redirect('teacher_dashboard')

    return render(request, 'create_class.html')

def student_payment(request):
    if request.session.get("role") != "student":
        return redirect("/login/")

    sid = request.session.get("user_id")  # should be student_id
    student = get_object_or_404(Student, student_id=sid)

    payments = Payment.objects.filter(student=student).order_by("-created_at")
    return render(request, "student_payments.html", {"payments": payments})


def student_payment_new(request):
    if request.session.get("role") != "student":
        return redirect("/login/")

    sid = request.session.get("user_id")
    student = get_object_or_404(Student, student_id=sid)

    classes = ClassSchedule.objects.all().order_by("-date")

    if request.method == "POST":
        schedule_id = request.POST.get("schedule_id")
        month = request.POST.get("month")
        amount = request.POST.get("amount")

        cls = get_object_or_404(ClassSchedule, schedule_id=schedule_id)

        p = Payment.objects.create(
            student=student,
            class_schedule=cls,
            month=month,
            amount=amount,
            status="INITIATED",
        )

        return redirect(f"/khalti/initiate/{p.payment_id}/")

    return render(request, "student_payment_create.html", {"classes": classes})


def khalti_initiate(request, payment_id):
    if request.session.get("role") != "student":
        return redirect("/login/")

    payment = get_object_or_404(Payment, payment_id=payment_id)

    sid = request.session.get("user_id")
    if payment.student.student_id != sid:
        return redirect("/student/payments/")

    payment.amount_paisa = int(float(payment.amount) * 100)
    payment.status = "INITIATED"
    payment.save()

    url = f"{settings.KHALTI_BASE_URL}/epayment/initiate/"
    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "return_url": f"{settings.WEBSITE_URL}/khalti/return/",
        "website_url": settings.WEBSITE_URL,
        "amount": payment.amount_paisa,
        "purchase_order_id": str(payment.purchase_order_id),
        "purchase_order_name": payment.purchase_order_name,
        "customer_info": {
            "name": payment.student.full_name,
            "email": payment.student.email,
            "phone": payment.student.phone,
        },
    }

    res = requests.post(url, json=payload, headers=headers, timeout=30)
    if res.status_code != 200:
        return HttpResponse(f"Khalti initiate failed: {res.status_code} {res.text}")

    data = res.json()
    payment.pidx = data.get("pidx")
    payment.save()

    return redirect(data.get("payment_url"))


def khalti_return(request):
    pidx = request.GET.get("pidx")
    if not pidx:
        return HttpResponse("Missing pidx.")

    payment = get_object_or_404(Payment, pidx=pidx)

    lookup_url = f"{settings.KHALTI_BASE_URL}/epayment/lookup/"
    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    res = requests.post(lookup_url, json={"pidx": pidx}, headers=headers, timeout=30)
    if res.status_code != 200:
        payment.status = "PENDING"
        payment.save()
        return HttpResponse(f"Khalti lookup failed: {res.status_code} {res.text}")

    info = res.json()
    final_status = info.get("status")
    payment.khalti_transaction_id = info.get("transaction_id")

    if final_status == "Completed":
        payment.status = "PAID"
    elif final_status == "Pending":
        payment.status = "PENDING"
    elif final_status == "User canceled":
        payment.status = "CANCELED"
    else:
        payment.status = "FAILED"

    payment.save()
    return redirect("/student/payments/")

def teacher_assessments(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    tid = request.session.get("user_id")
    teacher = get_object_or_404(Teacher, teacher_id=tid)

    assessments = Assessment.objects.filter(teacher=teacher).order_by("-created_at")
    return render(request, "teacher_assessments.html", {"assessments": assessments})


def teacher_create_assessment(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    tid = request.session.get("user_id")
    teacher = get_object_or_404(Teacher, teacher_id=tid)

    # teacher's classes only
    classes = ClassSchedule.objects.filter(teacher=teacher).order_by("-date")

    if request.method == "POST":
        schedule_id = request.POST.get("schedule_id")
        title = request.POST.get("title")
        instructions = request.POST.get("instructions")
        deadline = request.POST.get("deadline")
        ref_audio = request.FILES.get("reference_audio")

        cls = get_object_or_404(ClassSchedule, schedule_id=schedule_id)

        Assessment.objects.create(
            teacher=teacher,
            class_schedule=cls,
            title=title,
            instructions=instructions,
            deadline=deadline,
            reference_audio=ref_audio
        )

        return redirect("/teacher/assessments/")

    return render(request, "teacher_create_assessment.html", {"classes": classes})

def teacher_submissions(request, assessment_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    tid = request.session.get("user_id")
    teacher = get_object_or_404(Teacher, teacher_id=tid)

    assessment = get_object_or_404(Assessment, assessment_id=assessment_id, teacher=teacher)
    submissions = Submission.objects.filter(assessment=assessment).order_by("-submitted_at")

    return render(request, "teacher_submissions.html", {
        "assessment": assessment,   
        "submissions": submissions
    })


def teacher_grade_submission(request, submission_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    tid = request.session.get("user_id")
    teacher = get_object_or_404(Teacher, teacher_id=tid)

    submission = get_object_or_404(Submission, submission_id=submission_id)
    # safety: teacher must own this assessment
    if submission.assessment.teacher.teacher_id != teacher.teacher_id:
        return redirect("/teacher/assessments/")

    if request.method == "POST":
        score = request.POST.get("score")
        feedback = request.POST.get("feedback")

        submission.score = int(score) if score else None
        submission.feedback = feedback
        submission.graded_at = timezone.now()
        submission.save()

        return redirect(f"/teacher/assessments/{submission.assessment.assessment_id}/submissions/")

    return render(request, "teacher_grade_submission.html", {"s": submission})

def student_assessments(request):
    if request.session.get("role") != "student":
        return redirect("/login/")

    sid = request.session.get("user_id")
    student = get_object_or_404(Student, student_id=sid)

    # simple: show all assessments (later you can filter by enrolled class)
    assessments = Assessment.objects.all().order_by("-created_at")

    # map submission status
    submitted_ids = set(Submission.objects.filter(student=student).values_list("assessment_id", flat=True))

    return render(request, "student_assessments.html", {
        "assessments": assessments,
        "submitted_ids": submitted_ids
    })


def student_submit_assessment(request, assessment_id):
    if request.session.get("role") != "student":
        return redirect("/login/")

    sid = request.session.get("user_id")
    student = get_object_or_404(Student, student_id=sid)

    a = get_object_or_404(Assessment, assessment_id=assessment_id)

    existing = Submission.objects.filter(assessment=a, student=student).first()

    if request.method == "POST":
        audio = request.FILES.get("student_audio")
        comment = request.POST.get("comment")

        if not audio:
            return render(request, "student_submit_assessment.html", {
                "a": a,
                "existing": existing,
                "error": "Please upload an audio file."
            })

        # Save / update submission
        if existing:
            existing.student_audio = audio
            existing.comment = comment
            existing.submitted_at = timezone.now()
            existing.save()
            submission_obj = existing
        else:
            submission_obj = Submission.objects.create(
                assessment=a,
                student=student,
                student_audio=audio,
                comment=comment
            )

        # Auto feedback + AI feedback + graphs (only if teacher uploaded reference audio)
        if a.reference_audio:
            ref_path = a.reference_audio.path
            stu_path = submission_obj.student_audio.path

            # ---- Librosa scoring ----
            try:
                result = analyze_audio(ref_path, stu_path)

                submission_obj.pitch_score = result["pitch_score"]
                submission_obj.rhythm_score = result["rhythm_score"]
                submission_obj.auto_score = result["auto_score"]
                submission_obj.auto_feedback = result["feedback"]
            except Exception as e:
                print("LIBROSA ERROR:", e)

            # ---- Gemini dynamic feedback ----
            try:
                # Only call Gemini if we have scores computed
                if submission_obj.auto_score is not None:
                    submission_obj.ai_feedback = generate_gemini_feedback(
                        title=a.title,
                        pitch_score=float(submission_obj.pitch_score or 0),
                        rhythm_score=float(submission_obj.rhythm_score or 0),
                        auto_score=float(submission_obj.auto_score or 0),
                    )
            except Exception as e:
                print("GEMINI ERROR:", e)
                submission_obj.ai_feedback = None

            # ---- Graph generation ----
            try:
                pitch_rel = generate_pitch_plot(ref_path, stu_path)
                rhythm_rel = generate_rhythm_plot(ref_path, stu_path)

                # Assign to ImageFields
                submission_obj.pitch_plot.name = pitch_rel
                submission_obj.rhythm_plot.name = rhythm_rel
            except Exception as e:
                print("GRAPH ERROR:", e)

            # Save all updates
            submission_obj.save()

        return redirect("/student/assessments/")

    return render(request, "student_submit_assessment.html", {"a": a, "existing": existing})

def student_results(request):
    if request.session.get("role") != "student":
        return redirect("/login/")

    sid = request.session.get("user_id")
    student = get_object_or_404(Student, student_id=sid)

    submissions = Submission.objects.filter(student=student).order_by("-submitted_at")
    return render(request, "student_results.html", {"submissions": submissions})
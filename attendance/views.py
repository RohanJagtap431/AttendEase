from datetime import date
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from academics.models import TeacherAssignment
from students.models import StudentProfile
from .models import Attendance

from students.models import StudentProfile
from django.db.models import Count, Q
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from io import BytesIO

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)




@login_required
@require_http_methods(["GET", "POST"])
def mark_attendance(request, assignment_id):

    if request.user.role != 'teacher':
        messages.error(request, "Only teachers can mark attendance.")
        return redirect('dashboard_redirect')

    assignment = get_object_or_404(
        TeacherAssignment,
        id=assignment_id,
        teacher__user=request.user
    )

    students = StudentProfile.objects.filter(
        classroom=assignment.classroom,
        user__is_active=True
    ).select_related('user').order_by('roll_number')

    if not students.exists():
        messages.warning(request, "No students found in this class.")
        return redirect('teacher_dashboard')

    # Get selected attendance date
    date_value = request.GET.get('date', date.today().isoformat())

    if request.method == 'POST':
        date_value = request.POST.get('date', '').strip()

    try:
        selected_date = date.fromisoformat(date_value)
    except (ValueError, TypeError):
        messages.error(request, "Invalid attendance date.")
        return redirect('mark_attendance', assignment_id=assignment.id)

    # Save attendance
    if request.method == 'POST':

        allowed_statuses = {'present', 'absent', 'late'}
        attendance_data = []

        # Validate every student's data BEFORE saving anything
        for student in students:

            status = request.POST.get(
                f'status_{student.id}', ''
            ).strip()

            remarks = request.POST.get(
                f'remarks_{student.id}', ''
            ).strip()

            if status not in allowed_statuses:
                messages.error(
                    request,
                    f"Invalid attendance status for {student.user.username}."
                )

                return redirect(
                    f"{request.path}?date={selected_date.isoformat()}"
                )

            attendance_data.append({
                'student': student,
                'status': status,
                'remarks': remarks[:255],
            })

        # Save all records together
        with transaction.atomic():

            for item in attendance_data:

                Attendance.objects.update_or_create(
                    student=item['student'],
                    assignment=assignment,
                    date=selected_date,
                    defaults={
                        'status': item['status'],
                        'marked_by': request.user,
                        'remarks': item['remarks'],
                    }
                )

        messages.success(
            request,
            "Attendance saved successfully!"
        )

        return redirect(
            f"{request.path}?date={selected_date.isoformat()}"
        )

    # Load previously saved attendance for selected date
    existing_records = {
        record.student_id: record
        for record in Attendance.objects.filter(
            assignment=assignment,
            date=selected_date,
            student__in=students
        )
    }

    context = {
        'assignment': assignment,
        'students': students,
        'selected_date': selected_date,
        'existing_records': existing_records,
        'active_page': 'attendance',
    }

    return render(
        request,
        'attendance/mark_attendance.html',
        context
    )
 


from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404

from academics.models import TeacherAssignment
from students.models import StudentProfile


@login_required
def attendance_report(request, assignment_id):

    if request.user.role != 'teacher':
        messages.error(request, "Only teachers can view attendance reports.")
        return redirect('dashboard_redirect')

    assignment = get_object_or_404(
        TeacherAssignment,
        id=assignment_id,
        teacher__user=request.user
    )

    # Read date filters
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    # Validate dates
    try:
        start_date = date.fromisoformat(date_from) if date_from else None
        end_date = date.fromisoformat(date_to) if date_to else None

    except ValueError:
        messages.error(request, "Invalid date filter.")
        return redirect('attendance_report', assignment_id=assignment.id)

    if start_date and end_date and start_date > end_date:
        messages.error(request, "From Date cannot be after To Date.")
        return redirect('attendance_report', assignment_id=assignment.id)

    # Build attendance date conditions
    attendance_filter = Q(
        attendance_records__assignment=assignment
    )

    if start_date:
        attendance_filter &= Q(
            attendance_records__date__gte=start_date
        )

    if end_date:
        attendance_filter &= Q(
            attendance_records__date__lte=end_date
        )

    # Get students and filtered attendance counts
    students = StudentProfile.objects.filter(
        classroom=assignment.classroom,
        user__is_active=True
    ).select_related('user').annotate(

        present_count=Count(
            'attendance_records',
            filter=attendance_filter & Q(
                attendance_records__status='present'
            )
        ),

        absent_count=Count(
            'attendance_records',
            filter=attendance_filter & Q(
                attendance_records__status='absent'
            )
        ),

        late_count=Count(
            'attendance_records',
            filter=attendance_filter & Q(
                attendance_records__status='late'
            )
        )

    ).order_by('roll_number')

    # Calculate report
    report_data = []

    above_75 = 0
    below_75 = 0
    no_records = 0

    for student in students:

        total = (
            student.present_count +
            student.absent_count +
            student.late_count
        )

        attended = student.present_count + student.late_count

        percentage = (
            round((attended / total) * 100, 2)
            if total > 0 else 0
        )

        if total == 0:
            no_records += 1
        elif percentage >= 75:
            above_75 += 1
        else:
            below_75 += 1

        report_data.append({
            'student': student,
            'present': student.present_count,
            'absent': student.absent_count,
            'late': student.late_count,
            'total': total,
            'percentage': percentage,
        })

    context = {
        'assignment': assignment,
        'report_data': report_data,
        'total_students': len(report_data),
        'above_75': above_75,
        'below_75': below_75,
        'no_records': no_records,
        'date_from': date_from,
        'date_to': date_to,
        'active_page': 'attendance',
        'active_page': 'dashboard',
    }

    return render(
        request,
        'attendance/attendance_report.html',
        context
    )


@login_required
def export_attendance_excel(request, assignment_id):

    if request.user.role != 'teacher':
        messages.error(request, "Only teachers can export reports.")
        return redirect('dashboard_redirect')

    assignment = get_object_or_404(
        TeacherAssignment,
        id=assignment_id,
        teacher__user=request.user
    )

    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    try:
        start_date = date.fromisoformat(date_from) if date_from else None
        end_date = date.fromisoformat(date_to) if date_to else None
    except ValueError:
        messages.error(request, "Invalid date filter.")
        return redirect('attendance_report', assignment_id=assignment.id)

    if start_date and end_date and start_date > end_date:
        messages.error(request, "Invalid date range.")
        return redirect('attendance_report', assignment_id=assignment.id)

    attendance_filter = Q(
        attendance_records__assignment=assignment
    )

    if start_date:
        attendance_filter &= Q(
            attendance_records__date__gte=start_date
        )

    if end_date:
        attendance_filter &= Q(
            attendance_records__date__lte=end_date
        )

    students = StudentProfile.objects.filter(
        classroom=assignment.classroom,
        user__is_active=True
    ).select_related('user').annotate(

        present_count=Count(
            'attendance_records',
            filter=attendance_filter & Q(
                attendance_records__status='present'
            )
        ),

        absent_count=Count(
            'attendance_records',
            filter=attendance_filter & Q(
                attendance_records__status='absent'
            )
        ),

        late_count=Count(
            'attendance_records',
            filter=attendance_filter & Q(
                attendance_records__status='late'
            )
        )

    ).order_by('roll_number')

    # Create Excel workbook
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Attendance Report"

    # Title
    sheet.merge_cells('A1:G1')
    sheet['A1'] = 'AttendEase - Attendance Report'
    sheet['A1'].font = Font(
        bold=True,
        size=16,
        color='FFFFFF'
    )
    sheet['A1'].fill = PatternFill(
        start_color='243B6B',
        end_color='243B6B',
        fill_type='solid'
    )
    sheet['A1'].alignment = Alignment(horizontal='center')

    sheet.append([])
    sheet.append(['Class', str(assignment.classroom)])
    sheet.append(['Subject', str(assignment.subject.name)])
    sheet.append(['From Date', date_from or 'All'])
    sheet.append(['To Date', date_to or 'All'])
    sheet.append([])

    headers = [
        'Student Name',
        'Roll Number',
        'Present',
        'Absent',
        'Late',
        'Total',
        'Attendance %'
    ]

    sheet.append(headers)

    for cell in sheet[8]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(
            start_color='243B6B',
            end_color='243B6B',
            fill_type='solid'
        )

    for student in students:

        present = student.present_count
        absent = student.absent_count
        late = student.late_count

        total = present + absent + late
        attended = present + late

        percentage = (
            round((attended / total) * 100, 2)
            if total > 0 else 0
        )

        sheet.append([
            student.user.get_full_name() or student.user.username,
            student.roll_number,
            present,
            absent,
            late,
            total,
            percentage
        ])

    # Column widths
    widths = [25, 15, 12, 12, 12, 12, 18]

    for index, width in enumerate(widths, start=1):
        sheet.column_dimensions[
            chr(64 + index)
        ].width = width

    # Response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = (
        'attachment; filename="AttendEase_Attendance_Report.xlsx"'
    )

    workbook.save(response)

    return response


@login_required
def export_attendance_pdf(request, assignment_id):

    if request.user.role != 'teacher':
        messages.error(request, "Only teachers can export reports.")
        return redirect('dashboard_redirect')

    assignment = get_object_or_404(
        TeacherAssignment,
        id=assignment_id,
        teacher__user=request.user
    )

    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    # Validate date filters
    try:
        start_date = date.fromisoformat(date_from) if date_from else None
        end_date = date.fromisoformat(date_to) if date_to else None

    except ValueError:
        messages.error(request, "Invalid date filter.")
        return redirect(
            'attendance_report',
            assignment_id=assignment.id
        )

    if start_date and end_date and start_date > end_date:
        messages.error(request, "Invalid date range.")
        return redirect(
            'attendance_report',
            assignment_id=assignment.id
        )

    # Attendance filters
    attendance_filter = Q(
        attendance_records__assignment=assignment
    )

    if start_date:
        attendance_filter &= Q(
            attendance_records__date__gte=start_date
        )

    if end_date:
        attendance_filter &= Q(
            attendance_records__date__lte=end_date
        )

    students = StudentProfile.objects.filter(
        classroom=assignment.classroom,
        user__is_active=True
    ).select_related('user').annotate(

        present_count=Count(
            'attendance_records',
            filter=attendance_filter & Q(
                attendance_records__status='present'
            )
        ),

        absent_count=Count(
            'attendance_records',
            filter=attendance_filter & Q(
                attendance_records__status='absent'
            )
        ),

        late_count=Count(
            'attendance_records',
            filter=attendance_filter & Q(
                attendance_records__status='late'
            )
        )

    ).order_by('roll_number')

    # Create PDF buffer
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        alignment=TA_CENTER,
        fontSize=20,
        textColor=colors.HexColor('#243B6B'),
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=18
    )

    elements = []

    # Heading
    elements.append(
        Paragraph('AttendEase', title_style)
    )

    elements.append(
        Paragraph('STUDENT ATTENDANCE REPORT', subtitle_style)
    )

    # Class details
    date_range = (
        f"{date_from or 'All dates'} to {date_to or 'All dates'}"
    )

    details = [
        ['Class:', str(assignment.classroom),
         'Subject:', str(assignment.subject.name)],
        ['Date Range:', date_range,
         'Total Students:', str(students.count())],
    ]

    details_table = Table(
        details,
        colWidths=[30*mm, 65*mm, 30*mm, 65*mm]
    )

    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1E293B')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(details_table)
    elements.append(Spacer(1, 12))

    # Student attendance data
    table_data = [[
        'Student Name',
        'Roll No.',
        'Present',
        'Absent',
        'Late',
        'Total',
        'Attendance %'
    ]]

    above_75 = 0
    below_75 = 0
    no_records = 0

    for student in students:

        present = student.present_count
        absent = student.absent_count
        late = student.late_count

        total = present + absent + late
        attended = present + late

        percentage = (
            round((attended / total) * 100, 2)
            if total > 0 else 0
        )

        if total == 0:
            no_records += 1
            percentage_text = 'No Records'
        else:
            percentage_text = f'{percentage}%'

            if percentage >= 75:
                above_75 += 1
            else:
                below_75 += 1

        student_name = (
            student.user.get_full_name()
            or student.user.username
        )

        table_data.append([
            student_name,
            str(student.roll_number),
            str(present),
            str(absent),
            str(late),
            str(total),
            percentage_text
        ])

    report_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            65*mm, 30*mm, 25*mm, 25*mm,
            25*mm, 25*mm, 35*mm
        ]
    )

    report_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#243B6B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor('#F8FAFC')
        ]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(report_table)
    elements.append(Spacer(1, 16))

    # Summary
    summary_data = [
        ['75% & Above', 'Below 75%', 'No Records'],
        [str(above_75), str(below_75), str(no_records)]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[55*mm, 55*mm, 55*mm]
    )

    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 9),
    ]))

    elements.append(summary_table)

    # Build PDF
    document.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(
        pdf,
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        'attachment; filename="AttendEase_Attendance_Report.pdf"'
    )

    return response



@login_required
def student_attendance_report(request, assignment_id, student_id):

    if request.user.role != 'teacher':
        messages.error(request, "Only teachers can view attendance reports.")
        return redirect('dashboard_redirect')

    assignment = get_object_or_404(
        TeacherAssignment,
        id=assignment_id,
        teacher__user=request.user
    )

    student = get_object_or_404(
        StudentProfile.objects.select_related('user'),
        id=student_id,
        classroom=assignment.classroom,
        user__is_active=True
    )

    # Student attendance history for this subject
    records = Attendance.objects.filter(
        student=student,
        assignment=assignment
    ).order_by('-date')

    # Overall summary
    total = records.count()

    present = records.filter(status='present').count()
    absent = records.filter(status='absent').count()
    late = records.filter(status='late').count()

    attended = present + late

    percentage = (
        round((attended / total) * 100, 2)
        if total > 0 else 0
    )

    # Monthly attendance summary
    monthly_records = records.values(
        'date__year',
        'date__month'
    ).annotate(
        present_count=Count(
            'id',
            filter=Q(status='present')
        ),
        absent_count=Count(
            'id',
            filter=Q(status='absent')
        ),
        late_count=Count(
            'id',
            filter=Q(status='late')
        )
    ).order_by('-date__year', '-date__month')

    monthly_data = []

    for item in monthly_records:

        month_total = (
            item['present_count'] +
            item['absent_count'] +
            item['late_count']
        )

        month_attended = (
            item['present_count'] +
            item['late_count']
        )

        month_percentage = (
            round((month_attended / month_total) * 100, 2)
            if month_total > 0 else 0
        )

        monthly_data.append({
            'year': item['date__year'],
            'month': item['date__month'],
            'present': item['present_count'],
            'absent': item['absent_count'],
            'late': item['late_count'],
            'total': month_total,
            'percentage': month_percentage,
        })

    context = {
        'assignment': assignment,
        'student': student,
        'records': records,
        'total': total,
        'present': present,
        'absent': absent,
        'late': late,
        'percentage': percentage,
        'monthly_data': monthly_data,
    }

    return render(
        request,
        'attendance/student_attendance_report.html',
        context
    )



# ==============================
# ADMIN ATTENDANCE MONITORING
# ==============================

from academics.models import ClassRoom, TeacherProfile


@login_required
def admin_attendance_monitor(request):

    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('dashboard_redirect')

    records = Attendance.objects.select_related(
        'student__user',
        'student__classroom',
        'assignment__teacher__user',
        'assignment__subject',
        'marked_by'
    ).order_by('-date', 'student__roll_number')

    # Filters
    selected_date = request.GET.get('date', '').strip()
    selected_classroom = request.GET.get('classroom', '').strip()
    selected_teacher = request.GET.get('teacher', '').strip()

    if selected_date:
        try:
            selected_date = date.fromisoformat(selected_date)
            records = records.filter(date=selected_date)
        except ValueError:
            messages.error(request, "Invalid date filter.")
            selected_date = ''

    if selected_classroom.isdigit():
        records = records.filter(
            assignment__classroom_id=int(selected_classroom)
        )

    if selected_teacher.isdigit():
        records = records.filter(
            assignment__teacher_id=int(selected_teacher)
        )

    # Statistics based on filtered records
    statistics = records.aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late')),
    )

    context = {
        'records': records,
        'statistics': statistics,
        'classrooms': ClassRoom.objects.all().order_by('name'),
        'teachers': TeacherProfile.objects.select_related(
            'user'
        ).order_by('user__first_name'),
        'selected_date': selected_date,
        'selected_classroom': selected_classroom,
        'selected_teacher': selected_teacher,
        'active_page': 'attendance',
    }

    return render(
        request,
        'admin/admin_attendance.html',
        context
    )

@login_required
def teacher_attendance_records(request):

    if request.user.role != 'teacher':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('dashboard_redirect')

    # Only current teacher's attendance records
    records = Attendance.objects.filter(
        assignment__teacher__user=request.user
    ).select_related(
        'student__user',
        'student__classroom',
        'assignment__subject',
        'assignment__classroom',
        'marked_by'
    ).order_by('-date', 'student__roll_number')

    assignments = TeacherAssignment.objects.filter(
        teacher__user=request.user
    ).select_related(
        'classroom',
        'subject'
    )

    # Filters
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    selected_assignment = request.GET.get('assignment', '').strip()
    selected_status = request.GET.get('status', '').strip()

    if date_from:
        parsed_date = parse_date(date_from)
        if parsed_date:
            records = records.filter(date__gte=parsed_date)
        else:
            messages.error(request, "Invalid From Date.")

    if date_to:
        parsed_date = parse_date(date_to)
        if parsed_date:
            records = records.filter(date__lte=parsed_date)
        else:
            messages.error(request, "Invalid To Date.")

    if selected_assignment.isdigit():
        records = records.filter(
            assignment_id=int(selected_assignment)
        )

    if selected_status in ['present', 'absent', 'late']:
        records = records.filter(status=selected_status)

    statistics = records.aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late')),
    )

    context = {
        'records': records,
        'assignments': assignments,
        'statistics': statistics,
        'date_from': date_from,
        'date_to': date_to,
        'selected_assignment': selected_assignment,
        'selected_status': selected_status,
    }

    return render(
        request,
        'attendance/teacher_attendance_records.html',
        context
    )

@login_required
def student_my_attendance(request):

    if request.user.role != 'student':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('dashboard_redirect')

    try:
        student = StudentProfile.objects.select_related(
            'classroom'
        ).get(user=request.user)

    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('login')

    records = Attendance.objects.filter(
        student=student
    ).select_related(
        'assignment__subject',
        'assignment__classroom',
        'marked_by'
    ).order_by('-date')

    subject_data = records.values(
        'assignment__subject__name',
        'assignment__subject__code'
    ).annotate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late')),
    ).order_by('assignment__subject__name')

    subject_stats = []

    for item in subject_data:
        total = item['total']
        attended = item['present'] + item['late']

        percentage = round((attended / total) * 100, 2) if total else 0

        subject_stats.append({
            **item,
            'percentage': percentage,
        })

    statistics = records.aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late')),
    )

    total = statistics['total']
    attended = statistics['present'] + statistics['late']

    overall_percentage = round(
        (attended / total) * 100, 2
    ) if total else 0

    context = {
        'student': student,
        'records': records,
        'statistics': statistics,
        'subject_stats': subject_stats,
        'overall_percentage': overall_percentage,
    }

    return render(
        request,
        'attendance/student_my_attendance.html',
        context
    )


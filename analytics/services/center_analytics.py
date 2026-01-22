from datetime import timedelta
from django.db.models import Avg
from django.utils.timezone import now

from accounts.models import User
from assignments.models import Assignment, AssignmentSubmission
from progress.models import StudentProgress


def get_center_summary(center):
    last_7_days = now() - timedelta(days=7)

    # Students
    students_qs = User.objects.filter(
        memberships__center=center,
        role="student"
    )

    total_students = students_qs.count()
    active_students = students_qs.filter(
        last_login__gte=last_7_days
    ).count()

    # Assignments
    total_assignments = Assignment.objects.filter(
        group__center=center
    ).count()

    completed_submissions = AssignmentSubmission.objects.filter(
        session__assignment__group__center=center,
        is_completed=True
    ).count()

    # XP
    avg_xp = (
        StudentProgress.objects
        .filter(student__memberships__center=center)
        .aggregate(avg=Avg("xp"))
        .get("avg") or 0
    )

    return {
        "students": {
            "total": total_students,
            "active_7d": active_students,
        },
        "assignments": {
            "total": total_assignments,
            "completed": completed_submissions,
        },
        "xp": {
            "average": int(avg_xp),
        },
    }

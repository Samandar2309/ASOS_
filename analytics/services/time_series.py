from datetime import timedelta
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate
from django.utils.timezone import now

from accounts.models import User
from assignments.models import AssignmentSubmission
from progress.models import StudentProgress


def get_center_growth(center, days: int = 7):
    end_date = now().date()
    start_date = end_date - timedelta(days=days - 1)

    # 1. New students per day
    students_qs = (
        User.objects
        .filter(
            memberships__center=center,
            role="student",
            date_joined__date__range=(start_date, end_date)
        )
        .annotate(day=TruncDate("date_joined"))
        .values("day")
        .annotate(count=Count("id"))
    )

    # 2. Completed submissions per day
    submissions_qs = (
        AssignmentSubmission.objects
        .filter(
            session__assignment__group__center=center,
            is_completed=True,
            finished_at__date__range=(start_date, end_date)
        )
        .annotate(day=TruncDate("finished_at"))
        .values("day")
        .annotate(count=Count("id"))
    )

    # 3. Average XP per day (snapshot-like)
    xp_qs = (
        StudentProgress.objects
        .filter(
            student__memberships__center=center,
            updated_at__date__range=(start_date, end_date)
            if hasattr(StudentProgress, "updated_at")
            else None
        )
    )

    # Normalize results into dict by date
    def normalize(qs):
        return {
            item["day"].isoformat(): item["count"]
            for item in qs
        }

    students_map = normalize(students_qs)
    submissions_map = normalize(submissions_qs)

    # Build full timeline
    timeline = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        day_str = day.isoformat()

        timeline.append({
            "date": day_str,
            "new_students": students_map.get(day_str, 0),
            "completed_submissions": submissions_map.get(day_str, 0),
        })

    return {
        "range_days": days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "timeline": timeline,
    }

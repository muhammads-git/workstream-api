from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.models import Task, Assignment, Notification, NotificationType, TaskStatus
from datetime import datetime, timedelta, timezone

schedular = BackgroundScheduler()

def check_deadlines():
   db = SessionLocal()

   # time now
   now = datetime.now(timezone.utc)
   # time upcoming
   upcoming = now + timedelta(hours=24)

   try:

      tasks = db.query(Task).filter(
         Task.deadline >= now,
         Task.deadline <= upcoming,
         Task.status != TaskStatus.done
      ).all()

      for task in tasks:
         assignments = db.query(Assignment).filter(
            Assignment.task_id == task.id
         ).all()

         for assignment in assignments:
            existing = db.query(Notification).filter(
               Notification.user_id == assignment.user_id,
               Notification.task_id == assignment.task_id,
               Notification.type == NotificationType.deadline_approaching
            ).first()

            if not existing:
               notification = Notification(
                        user_id=assignment.user_id,
                        task_id=task.id,
                        message=f'Deadline approaching: {task.title} is due within 24 hours',
                        type=NotificationType.deadline_approaching
                    )
               db.add(notification)

      db.commit()

   finally:
      db.close()


def start_schedular():
   schedular.add_job(check_deadlines, 'interval', hours=1)
   schedular.start()
   return schedular

def shuttdown_schedular():
   schedular.shutdown()




import django_rq
from django.core.management.base import BaseCommand, CommandError

from devilry.devilry_superadmin import tasks
from devilry.utils.management import add_input_encoding_argument


class Command(BaseCommand):
    help = "Used to queue tasks for testing if RQ and error reporting works as intended."

    def add_arguments(self, parser):
        parser.add_argument("taskname", help="The task to enqueue.", choices=["success", "fail", "crash"])
        parser.add_argument(
            "--userid", type=int, help="User ID to run the task as. Only used for the 'fail' task.", required=False
        )
        parser.add_argument("--queue", default="default", help="RQ queue. Which queue the task should run on.")
        add_input_encoding_argument(parser)

    def handle(self, *args, **options):
        queue = django_rq.get_queue(name=options["queue"])
        taskname = options["taskname"]
        userid = options.get("userid")
        if taskname == "success":
            queue.enqueue(tasks.success, 3, 5)
        elif taskname == "fail":
            queue.enqueue(tasks.fail, userid=userid)
        elif taskname == "crash":
            queue.enqueue(tasks.crash)

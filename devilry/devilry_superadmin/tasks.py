from django.contrib.auth import get_user_model

from devilry.utils.report_error import debug_error_trigger, report_devilry_error


def success(x, y):
    return x + y


def crash():
    raise ValueError("This task always crashes.")


def fail(userid=None):
    user = None
    try:
        if userid:
            user = get_user_model().objects.get(id=userid)
        debug_error_trigger(user=user, context="'fail' debug task")
        raise ValueError("This task always fails gracefully.")
    except Exception as e:
        report_devilry_error(
            context=f"'fail' debug task",
            message="Error in the 'fail' debug task: {}".format(str(e)),
            exception=e,
            user=user,
        )

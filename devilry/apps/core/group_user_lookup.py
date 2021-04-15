from django.template import Template, Context
from django.utils.translation import gettext_lazy

from devilry.apps.core import models as core_models


class UserInfo(object):
    def __init__(self, groupuserlookup, user):
        self.groupuserlookup = groupuserlookup
        self.user = user

    @property
    def candidate(self):
        if not hasattr(self, '_candidate'):
            try:
                self._candidate = core_models.Candidate.objects.get(
                    assignment_group=self.groupuserlookup.group,
                    relatedstudent__user=self.user)
            except core_models.Candidate.DoesNotExist:
                self._candidate = None
        return self._candidate

    @property
    def relatedexaminer(self):
        if not hasattr(self, '_relatedexaminer'):
            try:
                self._relatedexaminer = core_models.RelatedExaminer.objects.get(
                    period_id=self.groupuserlookup.assignment.parentnode_id,
                    user=self.user)
            except core_models.RelatedExaminer.DoesNotExist:
                self._relatedexaminer = None
        return self._relatedexaminer

    @property
    def relatedstudent(self):
        if not hasattr(self, '_relatedstudent'):
            try:
                self._relatedstudent = core_models.RelatedStudent.objects.get(
                    period_id=self.groupuserlookup.assignment.parentnode_id,
                    user=self.user)
            except core_models.RelatedStudent.DoesNotExist:
                self._relatedstudent = None
        return self._relatedstudent

    def _render_template(self, templatestring, **contextdata):
        return Template(templatestring).render(Context(contextdata))

    def _render_span(self, cssclass, content):
        return self._render_template("""
        <span class="{{ cssclass }}">
            {{ content }}
        </span>
        """, cssclass=cssclass, content=content)

    def get_unanonymized_long_name_from_user(self, user, html=False):
        if user is None:
            fallback = gettext_lazy('Deleted user')
            if html:
                return self._render_span(cssclass='text-danger', content=fallback)
            else:
                return fallback
        if html:
            return self._render_template('{% load devilry_account_tags %}{% devilry_user_verbose_inline user %}', user=user)
        else:
            return user.get_displayname()

    def get_unanonymized_short_name_from_user(self, user, html=False):
        if user is None:
            fallback = gettext_lazy('Deleted user')
            if html:
                return self._render_span(cssclass='text-danger', content=fallback)
            else:
                return fallback
        return user.get_short_name()

    def __get_anonymized_name_from_user(self, user, user_role):
        if user_role == 'student':
            if self.groupuserlookup.assignment.uses_custom_candidate_ids:
                return self.candidate.get_anonymous_name(assignment=self.groupuserlookup.assignment)
            elif self.relatedstudent:
                return self.relatedstudent.get_anonymous_name()
        elif user_role == 'examiner':
            if self.relatedexaminer:
                return self.relatedexaminer.get_anonymous_name()
        else:
            raise ValueError('Can only call __get_anonymized_name_from_user '
                             'with user_role "examiner" or "student".')
        return gettext_lazy('User removed from semester')

    def get_anonymized_name_from_user(self, user, user_role, html=False):
        name = self.__get_anonymized_name_from_user(user=user, user_role=user_role)
        if html:
            if user_role == 'student':
                return self._render_span(cssclass='devilry-core-candidate-anonymous-name',
                                         content=name)
            else:
                return self._render_span(cssclass='devilry-core-examiner-anonymous-name',
                                         content=name)
        return name


class GroupUserLookup(object):
    """
    """
    def __init__(self, assignment, group, requestuser_devilryrole, requestuser=None):
        """
        Args:
            group:
            requestuser:
            requestuser_devilryrole:
        """
        assert assignment.id == group.parentnode_id
        self.assignment = assignment
        self.group = group
        self.requestuser = requestuser
        self.requestuser_devilryrole = requestuser_devilryrole
        self._usercache = {}

    def is_requestuser(self, user):
        """
        """
        if not self.requestuser:
            return False
        return self.requestuser == user

    def _get_userinfo(self, user):
        if user.id not in self._usercache:
            self._usercache[user.id] = UserInfo(groupuserlookup=self, user=user)
        return self._usercache[user.id]

    def get_long_name_from_user(self, user, user_role, html=False):
        userinfo = self._get_userinfo(user=user)
        if not self.is_requestuser(user=user):
            if user_role == 'student' and self.assignment.students_must_be_anonymized_for_devilryrole(devilryrole=self.requestuser_devilryrole):
                return userinfo.get_anonymized_name_from_user(user=user, user_role=user_role, html=html)
            elif user_role == 'examiner' and self.assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole=self.requestuser_devilryrole):
                return userinfo.get_anonymized_name_from_user(user=user, user_role=user_role, html=html)
        return userinfo.get_unanonymized_long_name_from_user(user=user, html=html)

    def get_plaintext_short_name_from_user(self, user, user_role, html=False):
        userinfo = self._get_userinfo(user=user)
        if not self.is_requestuser(user=user):
            if user_role == 'student' and self.assignment.students_must_be_anonymized_for_devilryrole(devilryrole=self.requestuser_devilryrole):
                return userinfo.get_anonymized_name_from_user(user=user, user_role=user_role, html=html)
            elif user_role == 'examiner' and self.assignment.examiners_must_be_anonymized_for_devilryrole(devilryrole=self.requestuser_devilryrole):
                return userinfo.get_anonymized_name_from_user(user=user, user_role=user_role, html=html)
        return userinfo.get_unanonymized_short_name_from_user(user=user)

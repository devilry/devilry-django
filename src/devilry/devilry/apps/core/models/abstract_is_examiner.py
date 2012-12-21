class AbstractIsExaminer(object):
    """ Abstract class implemented by all classes where it is natural to
    need to check if a user is examiner. """

    @classmethod
    def q_published(cls, old=True, active=True):
        """
        Return a django.models.Q object which matches all items of this type
        where :attr:`Assignment.publishing_time` is in the past.

        :param old: Include assignments where :attr:`Period.end_time`
            is in the past?
        :param active: Include assignments where :attr:`Period.end_time`
            is in the future?
        """
        raise NotImplementedError()


    @classmethod
    def q_is_examiner(cls, user_obj):
        """
        Return a django.models.Q object which matches items
        where the given user is examiner.
        """
        raise NotImplementedError()


    @classmethod
    def where_is_examiner(cls, user_obj):
        """ Get all items of this type where the given ``user_obj`` is
        examiner on one of the assignment groups.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return cls.objects.filter(
                cls.q_is_examiner(user_obj)
            ).distinct()

    @classmethod
    def published_where_is_examiner(cls, user_obj, old=True, active=True):
        """
        Get all published items of this type
        where the given ``user_obj`` is examiner on one of the assignment
        groups. Combines :meth:`q_is_examiner` and :meth:`q_published`.

        :param user_obj: :meth:`q_is_examiner`.
        :param old: :meth:`q_published`.
        :param active: :meth:`q_published`.
        :return: A django.db.models.query.QuerySet with duplicate
            assignments eliminated.
        """
        return cls.objects.filter(
                cls.q_published(old=old, active=active) &
                cls.q_is_examiner(user_obj)
                ).distinct()

    @classmethod
    def active_where_is_examiner(cls, user_obj):
        """
        Shortcut for :meth:`published_where_is_examiner` with
        ``old=False``.
        """
        return cls.published_where_is_examiner(user_obj, old=False,
                active=True)

    @classmethod
    def old_where_is_examiner(cls, user_obj):
        """
        Shortcut for :meth:`published_where_is_examiner` with
        ``active=False``.
        """
        return cls.published_where_is_examiner(user_obj, active=False)

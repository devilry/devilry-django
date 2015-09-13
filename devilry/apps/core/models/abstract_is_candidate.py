class AbstractIsCandidate(object):
    @classmethod
    def q_is_candidate(cls, user_obj):
        raise NotImplementedError()

    @classmethod
    def q_published(cls, old, active):
        raise NotImplementedError()

    @classmethod
    def where_is_candidate(cls, user_obj):
        return cls.objects.filter(
            cls.q_is_candidate(user_obj)
        ).distinct()

    @classmethod
    def published_where_is_candidate(cls, user_obj, old=True, active=True):
        return cls.objects.filter(
            cls.q_published(old=old, active=active) &
            cls.q_is_candidate(user_obj)
        ).distinct()

    @classmethod
    def active_where_is_candidate(cls, user_obj):
        return cls.published_where_is_candidate(user_obj, old=False, active=True)

    @classmethod
    def old_where_is_candidate(cls, user_obj):
        return cls.published_where_is_candidate(user_obj, active=False)

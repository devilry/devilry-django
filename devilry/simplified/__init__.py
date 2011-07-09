from exceptions import PermissionDenied
from qryresultwrapper import QryResultWrapper
from fieldspec import FieldSpec
from modelapi import simplified_modelapi


__all__ = ('PermissionDenied', 'QryResultWrapper', 'FieldSpec',
           'simplified_modelapi', 'SimplifiedModelApi')



class SimplifiedModelApi(object):
    """
    Base class for all simplified APIs.
    """
    @classmethod
    def create_search_qryresultwrapper(cls, user,
                                       result_fieldgroups, search_fieldgroups,
                                       **create_searchqryset_kwargs):
        """
        A more powerful alternative to :meth:`create_searchqryset`. By
        default, this method runs :meth:`create_searchqryset`. Override
        this to control the searchfields and resultfields forwarded
        to :class:`QryResultWrapper`.

        :return: A :class:`QryResultWrapper`.
        """
        qryset = cls.create_searchqryset(user, **create_searchqryset_kwargs)
        resultfields = cls._meta.resultfields.aslist(result_fieldgroups)
        searchfields = cls._meta.searchfields.aslist(search_fieldgroups)
        result = QryResultWrapper(resultfields, searchfields, qryset)
        return result

    @classmethod
    def create_searchqryset(cls, user, **filters):
        """
        """

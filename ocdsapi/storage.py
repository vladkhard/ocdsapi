import arrow
import couchdb
import logging
import sys
from iso8601 import parse_date
from couchdb.design import ViewDefinition
from ocdsapi.utils import prepare_responce_doc
from .utils import get_or_create_db


releases_ocid = ViewDefinition(
    'releases', 'id_index',
    map_fun=u"""function(doc) {emit([doc._id, doc.ocid], doc.date);}"""
)

releases_id = ViewDefinition(
    'releases', 'date_index',
    map_fun=u"""function(doc) {emit([doc.date, doc._id], doc.ocid);}"""
)
LOGGER = logging.getLogger("ocdsapi")


class ReleaseStorage(object):

    def __init__(self, host_url, db_name):
        server = couchdb.Server(host_url)
        if server.uuids():
            self.uid = server.uuids()[0]
        self.db = get_or_create_db(server, db_name)

        ViewDefinition.sync_many(
            self.db,
            [releases_ocid, releases_id]
            )
        LOGGER.info("Starting storage: {}".format(
            self.db.info()
        ))

    def _by_id(self, startkey, endkey):
        responce = self.db.view(
            'releases/id_index',
            startkey=startkey,
            endkey=endkey,
            include_docs=True,
            limit=1,
            )
        if responce.rows:
            for row in responce.rows:
                doc = row.get('doc')
                if doc:
                    return prepare_responce_doc(doc)
        return ""

    def get_id(self, id):
        startkey = (id, '')
        endkey = (id, 'xxxxxxxxxxx')
        return self._by_id(startkey, endkey)

    def get_ocid(self, ocid):
        startkey = ('', ocid)
        endkey = ('x' * 33, ocid)
        return self._by_id(startkey, endkey)

    def _by_date(self, **kw):
        for item in self.db.view(
                'releases/date_index',
                **kw
                ):
            key = item.get('key')
            if key:
                return arrow.get(key[0]).format("YYYY-MM-DD")
    
    def min_date(self):
        return self._by_date(
            limit=1,
            )
        
    def max_date(self):
        return self._by_date(
            limit=1,
            descending=True,
            )

    def get_window(self):
        return (self.min_date(), self.max_date())

    def _by_limit(self, start_key, view_limit=101, **kw):
        key = parse_date(start_key).isoformat() if start_key else ""
        if key:
            kw['startkey'] = (key, "")
        return self.db.view(
            'releases/date_index',
            limit=view_limit,
            **kw
        )

    def page(self, start_date, **kw):
        resp = self._by_limit(start_date, **kw)
        
        if resp and resp.rows:
            data = [
                (item['key'][1], item['key'][0], item.value)
                for item in resp
            ]
            last = data[-1][1]
            return last, data[:-1]
        return ("", "")
    
    def _inside(self, start_date, end_date):
        return self.db.view(
            'releases/date_index',
            startkey=(parse_date(start_date).isoformat(), ""),
            endkey=(parse_date(end_date).isoformat(), ""),
            )

    def ids_inside(self, start_date="", end_date=""):
        return [
            item.get('key')[1]
            if item else ""
            for item in self._inside(start_date, end_date)
        ]

    def ocids_inside(self, start_date, end_date):
        return [
            row.value
            for row in self._inside(start_date, end_date)
        ]

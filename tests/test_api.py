import pytest
import couchdb
from iso8601 import parse_date
from datetime import timedelta
from ocdsapi.storage import (
    ReleaseStorage
)
from ocdsapi.app import (
    create_app,
)

test_docs = [
    {
        "_id": "test_id",
        "language": "uk",
        "ocid": "test_ocid",
        "initiationType": "tender",
        "date": "2017-01-01",
        "tag": [
            "tender"
        ],
        "tender": {
            "procurementMethod": "limited",
            "status": "complete",
            "id": "test_id"
        },
        "id": "test_id",
        "$schema": ""
    },
    {
        "_id": "spam_id",
        "ocid": "spam_ocid",
        "date": "2017-01-01",
        "$schema": "",
    }
]
DB_HOST = "http://admin:admin@127.0.0.1:5984"
DB_NAME = "test"



@pytest.fixture(scope='function')
def db(request):
    SERVER = couchdb.Server(DB_HOST)
    def delete():
        del SERVER[DB_NAME]

    if DB_NAME in SERVER:
        delete()
    SERVER.create(DB_NAME)
    request.addfinalizer(delete)


@pytest.fixture(scope='function')
def storage(request):
    storage = ReleaseStorage(DB_HOST, DB_NAME)
    try:
        for doc in test_docs:
            storage.db.save(doc)
    except couchdb.http.ResourceConflict:
        pass
    except:
        raise
    return storage


@pytest.fixture
def app():
    app = create_app({},
        couchdb_url=DB_HOST,
        couchdb_dbname=DB_NAME,
        debug=True
    )
    return app


def test_app(db, storage, client):
    # res = client.get("/releases.json")
    # import pdb;pdb.set_trace()
    # assert res.status_code == 200
    # Release.json
    res = client.get(
        "/release.json?releaseID={}".format(test_docs[0]['id']))
    assert '_id' not in res.json
    assert '_rev' not in res.json
    assert res.status_code == 200

    # res = client.get(
    #     "/release.json?ocid={}".format(test_doc['ocid'])
    #     )
    # assert '_id' not in res.json
    # assert '_rev' not in res.json
    # assert res.status_code == 200
    res = client.get("/release.json?releaseID=invalid")
    # import pdb;pdb.set_trace()
    assert res.status_code == 404

    res = client.get("/release.json")
    # assert "message" in res.json
    assert res.status_code == 404
    # assert res.json["message"] == {
    #     "releaseID": "Provide valid releaseID"
    # }
    # Releases.json
    # res = client.get("/releases.json")
    # assert res.status_code == 200
    # assert "links" in res.json
    # assert "releases" in res.json
    # assert type(res.json['releases']) == list
    # assert res.json['releases'][0] == "/release.json?id={}".format(test_doc['id'])
    # assert "next" in res.json['links']

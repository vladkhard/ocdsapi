from gevent import monkey; monkey.patch_all()

from flask import Flask
from flask_restful import Api
from ocdsapi.storage import ReleaseStorage
from ocdsapi.utils import build_meta
from pkg_resources import iter_entry_points


def create_app(global_config, **options):
    app = Flask('ocdsapi')
    app.config['DEBUG'] = options.get('debug', False)
    api = Api(app)
    db = ReleaseStorage(
        options.get('couchdb_url'),
        options.get('couchdb_dbname'),
    )
    app.config['metainfo'] = build_meta(options)
    for plugin in iter_entry_points('ocdsapi.resources'):
        includeme = plugin.load()
        includeme(api, db=db, **options)
    return app


if __name__ == '__main__':
    app = create_app(
        {},
        couchdb_host='admin:admin@localhost',
        couchdb_port='5984',
        couchdb_dbname='releasedb',
        debug=True
    )
    app.run()
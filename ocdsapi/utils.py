import argparse
import yaml
from iso8601 import parse_date
from datetime import timedelta
import ocdsmerge


def read_config(path):
    with open(path) as cfg:
        config = yaml.load(cfg)
    return config


def parse_args():
    parser = argparse.ArgumentParser('Release Packages')
    parser.add_argument('-c', '--config',
                        required=True,
                        help="Path to configuration file")
    return parser.parse_args()


def form_next_date(start_date, page=None):
    # End for listing = start for url
    if page:
        # Here we should take a week later date for next page
        start_for_url = (parse_date(start_date) + timedelta(days=1 * int(page))
                         ).isoformat().split("T")[0]
        end_for_url = (parse_date(start_date) + timedelta(days=1 * (int(page) + 1))
                       ).isoformat().split("T")[0]
        start_for_listing = (parse_date(start_date) + timedelta(days=1 * (int(page) - 1))
                             ).isoformat().split("T")[0]
        return start_for_url, end_for_url, start_for_listing
    next_date = (parse_date(start_date) + timedelta(days=1)
                 ).isoformat().split("T")[0]
    return start_date, next_date


def get_releases_list(request, start_date, end_date, db):
    single_rel_url = '{}release.json?id={}'
    if request.args.get("idsOnly"):
        return [doc.value
                for doc in db.get_all_ids_between_dates(start_date,
                                                        end_date)]
    else:
        return [single_rel_url.format(request.url_root, doc.value)
                for doc in db.get_all_ids_between_dates(start_date,
                                                        end_date)]


def get_package_url(db, request, id=None, ocid=None):
    start_date = parse_date(db.get_dates()[0])
    release_date = parse_date(db.get_by_id(id)['date']) if id else parse_date(
        db.get_by_ocid(ocid)['date'])
    # How much weeks is after start date
    dayss = (release_date - start_date).days
    root_url = request.url_root
    st_date = (start_date + timedelta(days=1 * int(dayss))
               ).isoformat().split("T")[0]
    end_date = (start_date + timedelta(days=1 * int(dayss + 1))
                ).isoformat().split("T")[0]
    url = '{}releases.json?start_date={}&end_date={}'.format(
        root_url, st_date, end_date)
    return url


def compile_releases(releases, versioned=False):
    return ocdsmerge.merge(releases) if not versioned\
        else ocdsmerge.merge_versioned(releases)


def form_record(releases):
    record = {}
    record['releases'] = [releases]
    record['compiledRelease'] = compile_releases(record['releases'])
    record['ocid'] = record['releases'][0]['ocid']
    return record


def filter_id_rev(doc):
    if '_id' in doc:
        del doc['_id']
    if "_rev" in doc:
        del doc['_rev']
    return doc


def get_records_list(request, start_date, end_date, db):
    single_rel_url = '{}record.json?ocid={}'
    if request.args.get("idsOnly"):
        return [doc.value
                for doc in db.get_all_ocids_between_dates(start_date,
                                                          end_date)]
    else:
        return [single_rel_url.format(request.url_root, doc.value)
                for doc in db.get_all_ocids_between_dates(start_date,
                                                          end_date)]
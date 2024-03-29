import os
import json

from main import db, loadedPlugins
from models import EventTemplate, Authorization, Platform, Resource
from config import settings
import plugins


def populate_auths():
    auth_map = {'Woodshop': 416232,
                'Metalshop': 416231,
                'Forge': 420386,
                'LaserCutter': 416230,
                'Mig welding': 420387,
                'Tig welding': 420388,
                'Stick welding': 420389,
                'Manual mill': 420390,
                'Plasma': 420391,
                'Metal lathes': 420392,
                'CNC Plasma': 420393,
                'Intro Tormach': 420394,
                'Full Tormach': 420395}

    for auth in auth_map:
        if not Authorization.query.filter_by(name=auth).first():
            print(f"Adding new authorization: {auth}")
            a = Authorization(name=auth, wa_group_id=auth_map[auth])
            db.session.add(a)
            db.session.commit()


def populate_platforms():
    event_plugins = [plugin for plugin in loadedPlugins
                     if isinstance(loadedPlugins[plugin], plugins.EventPlugin)]

    for plugin in event_plugins:
        if not Platform.query.filter_by(name=plugin).first():
            print(f"Adding new platform: {plugin}")
            new_platform = Platform(name=plugin)
            db.session.add(new_platform)
            db.session.commit()


def populate_resources():
    resourceJSON = settings.get('plugin-GoogleCalendar', 'Resources')
    resources = json.loads(resourceJSON)
    # print(resources)
    for res in resources:
        # print(res)
        existing_resource = Resource.query.filter_by(email=res['resourceEmail']).first()
        if not existing_resource:
            print(f"Adding new resource: {res['resourceName']}")
            new_resource = Resource(name=res['resourceName'], email=res['resourceEmail'], capacity=res.get("capacity"))
            db.session.add(new_resource)
            db.session.commit()
        else:
            print(f"Updating resource: {res['resourceName']}")
            existing_resource.name = res["resourceName"]
            existing_resource.capacity = res.get("capacity")
            db.session.add(existing_resource)
            db.session.commit()

def create_default_template():
    if not EventTemplate.query.get(1):
        default = EventTemplate()
        default.title = "Default Template"
        default.description = "This automatically generated default template can be edited and saved to fit your needs."
        db.session.add(default)
        db.session.commit()


# if os.path.exists('migrations/'):
#     os.system('rm -r migrations/versions/*')
# else:
#     os.system('flask db init')
# if os.path.exists('site.db'):
#     os.system('rm site.db')


# os.system('flask db migrate')
os.system('flask db upgrade')

populate_auths()
populate_platforms()
populate_resources()
create_default_template()

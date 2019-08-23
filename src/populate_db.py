import os
from main import db, Event, Authorization


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
        print(auth)
        a = Authorization(name=auth, wa_group_id=auth_map[auth])
        db.session.add(a)
        db.session.commit()


if os.path.exists('migrations/'):
    os.system('rm -r migrations/versions/*')
else:
    os.system('flask db init')
if os.path.exists('site.db'):
    os.system('rm site.db')


os.system('flask db migrate')
os.system('flask db upgrade')

populate_auths()

import datetime

from main import db, loadedPlugins
import plugins


association_table = db.Table('association', db.Model.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('authorization_id', db.Integer, db.ForeignKey('authorization.id'))
)
event_price = db.Table('event_price', db.Model.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('price_id', db.Integer, db.ForeignKey('price.id'))
)
event_platform = db.Table('event_platform', db.Model.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('platform_id', db.Integer, db.ForeignKey('platform.id')),
)
event_resource = db.Table('event_resource', db.Model.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('resource_id', db.Integer, db.ForeignKey('resource.id')),
)


class BaseModel(db.Model):
    """
    A base for all database models to implement common requirements.
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_date = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    def update(self):
        self.modified_date = datetime.datetime.utcnow()
        db.session.add(self)
        db.session.commit()


class Event(BaseModel):
    _tablename_ = "event"

    title = db.Column(db.String(50), unique=False, nullable=False)
    instructor_email = db.Column(db.String(120), unique=False, nullable=True)
    instructor_name = db.Column(db.String(60))
    location = db.Column(db.String(120))
    start_date = db.Column(db.DateTime(), nullable=True, default=None)
    end_date = db.Column(db.DateTime(), nullable=True, default=None)
    # duration = db.Column(db.Interval(), nullable=False, default=datetime.timedelta(hours=1))
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')
    description = db.Column(db.String(500), nullable=False)
    min_age = db.Column(db.Integer(), nullable=True)
    max_age = db.Column(db.Integer(), nullable=True)
    registration_limit = db.Column(db.Integer(), nullable=True)

    prices = db.relationship("Price", secondary=event_price)
    authorizations = db.relationship("Authorization", secondary=association_table)
    resources = db.relationship("Resource", secondary=event_resource)
    platforms = db.relationship("Platform", secondary=event_platform)
    external_events = db.relationship("ExternalEvent")

    def __repr__(self):
        return f"Event('{self.title}', '{self.start_date}')"

    def registrationURL(self):
        return "placeholder.com"

    def addExternalEvent(self, platform_name, external_id, external_url):
        platform = Platform.query.filter_by(name=platform_name).first()
        ext_event = ExternalEvent(event_id=self.id,
                                  platform_id=platform.id,
                                  ext_event_id=external_id,
                                  ext_event_url=external_url)
        self. external_events.append(ext_event)

        return ext_event

    def getExternalEventByPlatformName(self, platform_name):
        ext_event = next(event for event in self.external_events
                         if event.platformName() == platform_name)
        return ext_event

    def fullySynced(self):
        synced = True
        ext_event_platforms = [ext.platform_id for ext in self.external_events]

        # check for out of date external events
        for ext_event in self.external_events:
            if ext_event.sync_date < self.modified_date:
                synced = False

        # check for uninitialized external events
        for platform in self.platforms:
            if platform.id not in ext_event_platforms:
                synced = False

        # check for deleted external events
        for platform_id in ext_event_platforms:
            if platform_id not in [platform.id for platform in self.platforms]:
                synced = False

        return synced

    def detailedDescription(self):
        desc = f"Instructor: {self.instructor_name}\n\n"
        desc += self.description
        if self.authorizations:
            auths = [auth.name for auth in self.authorizations]
            desc += f"\n\nRequired Authorizations: {auths}\n\n"

        if self.min_age and not self.max_age:
            desc += f"Ages: {self.min_age} and up\n\n"
        elif self.max_age and not self.min_age:
            desc += f"Ages: {self.max_age} and under\n\n"
        elif self.min_age and self.max_age:
            desc += f"Ages: {self.min_age} to {self.max_age}\n\n"

        if self.prices:
            desc += "Event Prices:\n"
            for price in self.prices:
                desc += f"- {price.name}: ${price.value:.2f}\n"

        return desc

    def htmlSummary(self, all_links=False, omit=[]):
        desc = ""

        if 'time' not in omit:
            desc += "<b>Time:</b> " \
                + self.start_date.strftime('%b %d %I:%M %p - ') \
                + self.end_date.strftime('%I:%M %p')

        if 'instr' not in omit:
            desc += f"<br><b>Instructor:</b> {self.instructor_name}"

        if all_links:
            for ext_event in self.external_events:
                platform_name = Platform.query.get(ext_event.platform_id).name
                desc += f"<br><b>{platform_name}:</b> <a href='{ext_event.ext_event_url}'>" \
                        f"link</a>"
        else:
            if self.external_events and 'reg' not in omit:
                for ext_event in self.external_events:
                    if ext_event.primary_event:
                        desc += f"<br><b>Register:</b> <a href='{ext_event.ext_event_url}'>" \
                                       f"{ext_event.ext_event_url}</a>"

        if 'price' not in omit:
            for price in self.prices:
                desc += f"<br><b>Price:</b> {price.name} - ${price.value:.2f}"

        if 'age' not in omit:
            if self.min_age and not self.max_age:
                desc += f"<br><b>Ages</b>: {self.min_age} and up"
            elif self.max_age and not self.min_age:
                desc += f"<br><b>Ages</b>: {self.max_age} and under"
            elif self.min_age and self.max_age:
                desc += f"<br><b>Ages</b>: {self.min_age} to {self.max_age}"

        if self.authorizations and 'auth' not in omit:
            desc += f"<br><b>Required Authorizations:</b> " \
                + f"{', '.join([auth.name for auth in self.authorizations])}"

        desc += '<br><br>' + '<br>'.join(self.description.split('\n'))

        return desc


class Authorization(db.Model):
    _tablename_ = "authorization"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    wa_group_id = db.Column(db.Integer, nullable=False, unique=True)

    events = db.relationship("Event", secondary=association_table,
                             back_populates="authorizations")

    def __repr__(self):
        return f"Authorization('{self.name}': '{self.wa_group_id}')"

class Resource(BaseModel):
    _tablename_ = "resource"

    name = db.Column(db.String(40), nullable=False, unique=True)
    email = db.Column(db.String(200), unique=False, nullable=True)

    events = db.relationship("Event", secondary=event_resource,
                             back_populates="resources")

    def __repr__(self):
        return f"Resource('{self.name}')"


class Price(db.Model):
    _tablename_ = "price"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    value = db.Column(db.Float(), nullable=False)
    description = db.Column(db.String(40), nullable=True)
    availability = db.Column(db.String(30), nullable=False)

    events = db.relationship("Event", secondary=event_price,
                             back_populates="prices")

    def __repr__(self):
        return f"Price('{self.name}': '{self.value}', '{self.availability}', '{self.events}')"


class Platform(db.Model):
    _tablename_ = "platform"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)

    events = db.relationship("Event", secondary=event_platform,
                             back_populates="platforms")


class ExternalEvent(BaseModel):
    _tablename_ = "external_event"

    primary_event = db.Column(db.Boolean, default=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    ext_event_id = db.Column(db.String(100))
    ext_event_url = db.Column(db.String(300))

    sync_date = db.Column(db.DateTime, nullable=True, default=None)

    def updateSyncDate(self):
        self.sync_date = datetime.datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def platformName(self):
        return Platform.query.get(self.platform_id).name

# class Location(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(40), nullable=False, unique=True)
#     description = db.Column(db.String(120), nullable=False, unique=True)

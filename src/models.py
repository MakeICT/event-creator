from datetime import datetime, timedelta
import enum
import itertools

from sqlalchemy.ext.declarative import declared_attr

from main import db, loadedPlugins
import plugins


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
        self.modified_date = datetime.utcnow()
        db.session.add(self)
        db.session.commit()


class SpecialBase(BaseModel):
    __abstract__ = True

    name = db.Column(db.String(40), nullable=False)

    @property
    def all_owners(self):
        return list(
            itertools.chain(
            *[
                getattr(self, attr)
                for attr in [a for a in dir(self) if a.endswith("_parents")]
            ]
        ))


class Tag(SpecialBase):
    __tablename__ = "tag"

    parent_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=True, unique=False)  
    children = db.relationship('Tag', lazy=True)

    def __repr__(self):
        return f"Tag('{self.name}')"
    db.UniqueConstraint('name', name='tag_uq')


class Authorization(SpecialBase):
    __tablename__ = "authorization"

    wa_group_id = db.Column(db.Integer, nullable=False, unique=True)

    def __repr__(self):
        return f"Authorization('{self.name}': '{self.wa_group_id}')"


class Resource(SpecialBase):
    _tablename_ = "resource"

    email = db.Column(db.String(200), unique=False, nullable=True)

    def __repr__(self):
        return f"Resource('{self.name}')"


class Price(SpecialBase):
    _tablename_ = "price"

    value = db.Column(db.Float(), nullable=False)
    description = db.Column(db.String(40), nullable=True)
    availability = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"Price('{self.name}': '{self.value}', '{self.availability}')"


class Platform(SpecialBase):
    _tablename_ = "platform"

    def __repr__(self):
        return f"Platform('{self.name}')"


# class Location(SpecialBase):
#     __tablename__ = "location"

#     description = db.Column(db.String(120), nullable=False, unique=True)

#     def __repr__(self):
#         return f"Location('{self.name}')"


class ExternalEvent(BaseModel):
    _tablename_ = "external_event"

    primary_event = db.Column(db.Boolean, default=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    ext_event_id = db.Column(db.String(100))
    ext_event_url = db.Column(db.String(300))

    sync_date = db.Column(db.DateTime, nullable=True, default=None)

    def updateSyncDate(self):
        self.sync_date = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def platformName(self):
        return Platform.query.get(self.platform_id).name


class EventStatus(enum.Enum):
    draft = 1
    submitted = 2
    approved = 3
    rejected = 4
    cancelled = 5
    deleted = 6


class EventType(enum.Enum):
    event = 0
    _class = 1
    reservation = 2


class BaseEventTemplate(BaseModel):
    __abstract__ = True

    event_type = db.Column(db.Enum(EventType), nullable=False, default=EventType._class)

    title = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(4000), nullable=False)
    host_email = db.Column(db.String(120), unique=False, nullable=True)
    host_name = db.Column(db.String(60))
    location = db.Column(db.String(120))
    start_time = db.Column(db.Time(), nullable=True, default=None)
    duration = db.Column(db.Interval(), nullable=False, default=timedelta(hours=1))
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')

    @declared_attr
    def tags(cls):
        resource_association = db.Table(
            '%s_tags' % cls.__tablename__,
            cls.metadata,
            db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
            db.Column('%s_id' % cls.__tablename__,
                      db.Integer, db.ForeignKey('%s.id' % cls.__tablename__)),
        )
        return db.relationship(Tag, secondary=resource_association,
                               backref="%s_parents" % cls.__name__.lower())

    @declared_attr
    def resources(cls):
        resource_association = db.Table(
            '%s_resources' % cls.__tablename__,
            cls.metadata,
            db.Column('resource_id', db.Integer, db.ForeignKey('resource.id')),
            db.Column('%s_id' % cls.__tablename__,
                      db.Integer, db.ForeignKey('%s.id' % cls.__tablename__)),
        )
        return db.relationship(Resource, secondary=resource_association,
                               backref="%s_parents" % cls.__name__.lower())

    @declared_attr
    def platforms(cls):
        platform_association = db.Table(
            '%s_platform' % cls.__tablename__,
            cls.metadata,
            db.Column('platform_id', db.Integer, db.ForeignKey('platform.id')),
            db.Column('%s_id' % cls.__tablename__,
                      db.Integer, db.ForeignKey('%s.id' % cls.__tablename__)),
        )
        return db.relationship(Platform, secondary=platform_association)


    # Restrictions
    min_age = db.Column(db.Integer(), nullable=True)
    max_age = db.Column(db.Integer(), nullable=True)
    registration_limit = db.Column(db.Integer(), nullable=True)

    @declared_attr
    def prices(cls):
        price_association = db.Table(
            '%s_price' % cls.__tablename__,
            cls.metadata,
            db.Column('price_id', db.Integer, db.ForeignKey('price.id')),
            db.Column('%s_id' % cls.__tablename__,
                      db.Integer, db.ForeignKey('%s.id' % cls.__tablename__)),
        )
        return db.relationship(Price, secondary=price_association)
    @declared_attr
    def authorizations(cls):
        authorization_association = db.Table(
            '%s_authorization' % cls.__tablename__,
            cls.metadata,
            db.Column('authorization_id', db.Integer, db.ForeignKey('authorization.id')),
            db.Column('%s_id' % cls.__tablename__,
                      db.Integer, db.ForeignKey('%s.id' % cls.__tablename__)),
        )
        return db.relationship(Authorization, secondary=authorization_association)

    # # Grants
    # def grant_auths(cls):
    #     authorization_association = db.Table(
    #         '%s_authorization' % cls.__tablename__,
    #         cls.metadata,
    #         db.Column('authorization_id', db.Integer, db.ForeignKey('authorization.id')),
    #         db.Column('%s_id' % cls.__tablename__,
    #                   db.Integer, db.ForeignKey('%s.id' % cls.__tablename__)),
    #     )
    #     return db.relationship(Authorization, secondary=authorization_association)

    def __repr__(self):
        return f"Event Template('{self.title}')"


class EventTemplate(BaseEventTemplate):
    __tablename__ = "event_template"

    def uniqueName(self):
        return f"{self.title} [{self.host_name}] ({self.id})"


class Event(BaseEventTemplate):
    _tablename_ = "event"

    status = db.Column(db.Enum(EventStatus), nullable=False, default=EventStatus.approved)

    start_date = db.Column(db.Date(), nullable=True, default=None)
    submission_date = db.Column(db.DateTime(), nullable=True, default=None)
    decision_date = db.Column(db.DateTime(), nullable=True, default=None)
    cancelled_date = db.Column(db.DateTime(), nullable=True, default=None)

    external_events = db.relationship("ExternalEvent")

    def __repr__(self):
        return f"Event('{self.title}', '{self.start_date}')"

    def startDateTime(self):
        dt = datetime.combine(self.start_date, self.start_time)
        return dt

    def startDate(self):
        return self.startDateTime().date()

    def startTime(self):
        return self.startDateTime().time()

    def endDateTime(self):
        dt = datetime.combine(self.start_date, self.start_time)
        dt = dt + self.duration
        return dt

    def endDate(self):
        return self.endDateTime().date()

    def endTime(self):
        return self.endDateTime().time()

    def registrationURL(self):
        for ext_event in self.external_events:
            if ext_event.primary_event:
                return ext_event.ext_event_url
        return None

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

    def htmlSummary(self, all_links=False, omit=[]):
        desc = ""

        if 'time' not in omit:
            desc += "<b>Time:</b> " \
                + self.startDateTime().strftime('%b %d %I:%M %p - ') \
                + self.endTime().strftime('%I:%M %p')

        if 'instr' not in omit:
            desc += f"<br><b>Instructor:</b> {self.host_name}"

        if all_links:
            for ext_event in self.external_events:
                platform_name = Platform.query.get(ext_event.platform_id).name
                desc += f"<br><b>{platform_name}:</b> <a href='{ext_event.ext_event_url}'>" \
                        f"link</a>"
        else:
            if self.external_events and 'reg' not in omit:
                reg_url = self.registrationURL()
                if reg_url:
                    desc += f"<br><b>Register:</b> <a href='{reg_url}'>" \
                                   f"{reg_url}</a>"

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

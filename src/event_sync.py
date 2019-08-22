from main import db, Event, Platform, ExternalEvent

import plugins

loadedPlugins = plugins.loadAllFromPath()

event = Event.query.first()

loadedPlugins['WildApricot'].createEvent(event)
print(loadedPlugins['WildApricot'])

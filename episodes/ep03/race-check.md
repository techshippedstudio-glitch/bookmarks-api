# Ep3 race check: save a link while its existing bookmark is deleted mid-save
# Coordinator probe, 2026-10-24, Python 3.12, real Postgres, each branch's own code and test database.
# Probe: race_http.py (deletes the row right after the skipped insert, before the lookup).

== shortcut-r1
(server log) sqlalchemy.exc.NoResultFound: No row was found when one was required
save new link      -> 201
save it again      -> 200
save while deleted -> 500 internal_error
== flowback-r1
save new link      -> 201
save it again      -> 200
save while deleted -> 201 
== flowback-r2
save new link      -> 201
save it again      -> 200
save while deleted -> 201 
== forward-r1
save new link      -> 201
save it again      -> 200
save while deleted -> 201 
== forward-r2
save new link      -> 201
save it again      -> 200
save while deleted -> 201 
== living-r1
save new link      -> 201
save it again      -> 200
save while deleted -> 201 
== living-r2
save new link      -> 201
save it again      -> 200
save while deleted -> 201 

== forward-r3
save new link      -> 201
save it again      -> 200
save while deleted -> 201
== forward-r4
save new link      -> 201
save it again      -> 200
save while deleted -> 201
== ep03-start (before the change, 409 rule)
save new link      -> 201
save it again      -> 409
save while deleted -> 409 duplicate_url

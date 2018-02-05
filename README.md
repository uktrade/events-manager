# Events Manager

![](readme.png)

An application for the management of events.

At this point, there is no real functionality.

## Database

We use Postgres 9.5; for convenience you can start an instance via Docker:

    docker-compose up postgres
    
This will automatically create a database called `events_manager`.    
    
There is only one related environment variable - `DATABASE_URL` - which is mandatory; if using
the above instance you can set it like so:
    
    export DATABASE_URL='postgres://postgres@localhost/events_manager'
    
Please note that, if deploying to Gov PaaS, this will be set automatically.    

## Authentication

All endpoints (of which there is currently only one), are protected by [Staff SSO](https://github.com/uktrade/staff-sso).

The following environment variables are mandatory:

| Key                       | Comments          
| -------------             |---------------------------------------------------------------|
| SSO_PROVIDER              | The url to the SSO provider, without a trailing slash         |   
| SSO_CLIENT_ID             |                                                               |
| SSO_CLIENT_SECRET         |                                                               |
| SSO_RETURNING_BASE_URI    | The root uri of this application - without trailing slash (e.g. https://events-manager-dev.cloudapps.digital) |                                                           |

## Local running

At this point, we recommend that you point to the UAT Staff SSO server

    python manage.py runserver 8000

## Managing Requirements

When adding a new library, first add it to requirements.in, then::

    pip-compile --output-file requirements.txt requirements.in
    pip install -r requirements.txt

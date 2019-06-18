Django app for exploring data gathered about hedgehogs


# Installation

Requires python3, a postgres server, and a redis server

## Create environment

Clone the repo

```sh
git clone git@github.com:tech4nature/hogapp.git
cd hogapp/hog/
cp environment-example .env
```

Now edit `.env` with a database username and password: you'll actually create this user in the next step.

## Set up postgres and database

```sh
apt-get install postgresql-10
sudo su - postgres
createuser <DB_USER from .env> -W
createdb hog -O <DB_USER from .env>
```

### Set up a python3 virtualenv

```sh
apt-get install mkvirtualenv
mkvirtualenv -p /usr/bin/python3 hogapp
pip install pip-tools
pip-sync
```

## Set up the database

```
./manage.py migrate
```

## Set up admin user

```
cd hog
./manage.py createsuperuser
```

## Install other dependencies

```
apt-get install redis-server
apt-get install ffmpeg
```

## Generate sample data

    ./manage.py generate_data

## Run server

    ./manage.py runserver

## Run redis worker

    ./manage.py worker

## View api

Visit http://localhost:8000/api/

Docs at http://localhost:8000/docs/

## API examples

For a worked example, refer to `examples/client.py`

### Location measurements

These must contain a location id, which must exist.

To create a location, `POST` data like this to `/api/locations/`:

```json
{
  "code": "some-unique-location-code-1234abc",
  "name": "Hogwarts Hotel"
}
```

To submit an inside temperature, `POST` data like this to `/api/measurements/`:

```json
{
  "measurement_type": "in_temp",
  "measurement": 20.3,
  "observed_at": "2019-03-22T13:44:00Z",
  "location_id": "some-unique-location-code-1234abc"
}
```

Example using `curl`:

```sh
curl -X POST "http://username:password@hogserver.com/api/measurements/" -H "accept: application/json" -H "Content-Type: application/json" -d '{"location_id": "some-unique-location-code-1234abc", "measurement_type": "in_temp", "measurement": 20.3, "observed_at": "2019-03-22T13:44"}'
```


### Hog measurements

These must include a `hog_id`.  Weights are created with a single operation, `POST`ing the following data to `/api/measurements/`:

```json
{
  "measurement_type": "weight",
  "measurement": 302.3,
  "observed_at": "2019-06-01T10:11",
  "location_id": "box-5003097965448",
  "hog_id": "hog-123456"
}
```

Videos are created in a similar way, but it's a two-part process. The first creates the measurement entry:

```json
{
  "measurement_type": "video",
  "video": ""
  "observed_at": "2019-06-01T10:11",
  "location_id": "box-5003097965448",
  "hog_id": "hog-123456"
}
```

This will return JSON including an `id` field. The video should then be `PUT` to that measurement, e.g. `/api/measurements/198136/video/`, as `multipart/form-data`, with a field name of `video`.

Using `curl`, for example:

```sh
curl -X POST "http://username:password@hogserver.com/api/measurements/" -H "accept: application/json" -H "Content-Type: application/json" -d '{ "measurement_type": "video", "video": "",  "observed_at": "2019-06-01T10:11", "location_id": "box-5003097965448", "hog_id": "hog-gs"}'
```

Might return:

```json
{"id":198138,"measurement_type":"video","measurement":null,"observed_at":"2019-06-01T10:11:00Z","video":null,"hog_id":"hog-gs","location_id":"box-5003097965448"}
```

The id can then be used to upload the video:

```sh
curl -X PUT "http://username:password@hogserver.com/api/measurements/198136/video/" -F"video=@video.mp4"```

Which would return:

```json
{"video":"/media/videos/video_cr71xsE.mp4"}
```

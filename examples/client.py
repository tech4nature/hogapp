import json
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth


HOGHOST = "http://localhost:8000"
AUTH = None


def create_location(code, name):
    data = {
        "code": code,
        "name": name
    }

    return requests.post(
        HOGHOST + '/api/locations/', data=data, auth=AUTH).json()


def _create_measurement(location_id, measurement_type,
                        measurement=None, hog_id=None):
    data = {
        "hog_id": hog_id,
        "measurement_type": measurement_type,
        "observed_at": datetime.utcnow().isoformat(),
        "location_id": location_id
    }
    if measurement is not None:
        data["measurement"] = measurement

    return requests.post(
        HOGHOST + '/api/measurements/', data=data, auth=AUTH).json()


def create_weight(location_id, hog_id, weight):
    return _create_measurement(location_id, "weight", weight, hog_id)


def create_inside_temp(location_id, temp):
    return _create_measurement(location_id, "in_temp", temp)


def create_outside_temp(location_id, temp):
    return _create_measurement(location_id, "out_temp", temp)


def upload_video(location_id, hog_id, video_path):
    measurement = _create_measurement(location_id, "video", hog_id=hog_id)
    print(measurement)
    measurement_id = measurement['id']
    files = {'video': open(video_path, 'rb')}
    url = HOGHOST + '/api/measurements/{}/video/'.format(measurement_id)
    return requests.put(url, files=files, auth=AUTH).json()


if __name__ == '__main__':
    username = input("username:")
    password = input("password:")
    AUTH = HTTPBasicAuth(username, password)

    print("Making a location:")
    print(create_location("myplace", "My place"))
    print()
    print("Adding a weight:")
    print(create_weight("myplace", "hog-23", 320.5))
    print()
    print("Adding inside and outside temperatures:")
    print(create_inside_temp("myplace", 19.0))
    print(create_outside_temp("myplace", 18.4))
    print()
    print("Adding a video:")
    print(upload_video("myplace", "hog-23", "hog/media/sample_file.mp4"))
    print()
    print("All data for My Place")
    print(json.dumps(
        requests.get(
            HOGHOST + '/api/measurements/?location=myplace').json(),
        indent=2))

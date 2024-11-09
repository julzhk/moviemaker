import os
from time import sleep
import requests
import shotstack_sdk as shotstack
from faker import Faker


def download_video(url, local_filename):
    # Send a GET request to the URL
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        # Open a local file with write-binary mode
        with open(local_filename, "wb") as f:
            # Write the content to the local file in chunks
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


class ShotStack:
    host = "https://api.shotstack.io/stage"
    SANDBOX_KEY = os.getenv("SANDBOX_KEY")
    PROD_KEY = os.getenv("PROD_KEY")
    url = "https://api.shotstack.io/edit/v1/templates/render"
    # configuration.api_key['DeveloperKey'] = os.getenv("SHOTSTACK_KEY")
    configuration = shotstack.Configuration(host=host)
    configuration.api_key["DeveloperKey"] = SANDBOX_KEY
    templateLookup = {"Title": "280d4967-ecc0-4c56-8aff-2d9ed41a8688"}
    queue_id = None

    def prepare(self, template_name, data: dict):
        template_id = self.templateLookup.get(template_name)
        merge_fields = [{"find": key, "replace": data[key]} for key in data]

        data = {"id": template_id, "merge": merge_fields}
        r = requests.post(self.url, json=data, headers={"x-api-key": self.PROD_KEY})
        self.queue_id = r.json()["response"]["id"]

    def poll(self):
        url = f"https://api.shotstack.io/edit/v1/render/{self.queue_id}"
        status = "pending"
        # set a timeout for the polling
        tries = 0
        pollresult = {}
        while status != "done" and tries < 10:
            r = requests.get(url, headers={"x-api-key": self.PROD_KEY})
            tries += 1
            pollresult = r.json()
            status = pollresult["response"]["status"]
            sleep(2)
        try:
            video_url = pollresult["response"]["url"]
            # download url to file
            fn = Faker().word() + ".mp4"
            download_video(video_url, fn)
            return fn
        except KeyError:
            return None

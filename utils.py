import os
from time import sleep
import requests
import shotstack_sdk as shotstack
from faker import Faker

DONE = "done"


def download_file(url, local_filename, local_folder='media_srcs/'):
    # Send a GET request to the URL
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        # Open a local file with write-binary mode
        file_path = local_folder + local_filename
        with open(file_path, "wb") as f:
            # Write the content to the local file in chunks
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return file_path


class ShotStack:
    host = "https://api.shotstack.io/v1"
    SANDBOX_KEY = os.getenv("SANDBOX_KEY")
    PROD_KEY = os.getenv("PROD_KEY")
    base_url = "https://api.shotstack.io/edit/v1/templates/render"
    # configuration.api_key['DeveloperKey'] = os.getenv("SHOTSTACK_KEY")
    configuration = shotstack.Configuration(host=host)
    configuration.api_key["DeveloperKey"] = SANDBOX_KEY
    templateLookup = {}
    queue_id = None

    def __init__(self,template_name=None, template_id=None):
        # use template name if provided, otherwise use template id
        self.template_id = self.templateLookup.get(template_name,template_id)
        self.templateLookup = self.get_templates()

    def get_templates(self):
        # get all templates
        url = 'https://api.shotstack.io/edit/v1/templates'
        r = requests.get(url, headers={"x-api-key": self.PROD_KEY})
        r = r.json()
        return {i['name']: i['id'] for i in r["response"]["templates"]}

    def prepare(self, template_name, data: dict):
        self.template_id = self.templateLookup.get(template_name)
        merge_fields = [{"find": key, "replace": data[key]} for key in data]
        url = "https://api.shotstack.io/edit/v1/templates/render"
        data = {"id": self.template_id, "merge": merge_fields}
        r = requests.post(url, json=data, headers={"x-api-key": self.PROD_KEY})
        self.queue_id = r.json()["response"]["id"]

    def poll(self):
        url = f"https://api.shotstack.io/edit/v1/render/{self.queue_id}"
        status = "pending"
        # set a timeout for the polling
        tries = 0
        pollresult = {}
        while status != DONE and tries < 10:
            sleep(0.25)
            r = requests.get(url, headers={"x-api-key": self.PROD_KEY})
            tries += 1
            pollresult = r.json()
            status = pollresult["response"]["status"]
            if status != DONE:
                sleep(2)
        try:
            video_url = pollresult["response"]["url"]
            # download url to file
            fn = Faker().word() + ".mp4"
            filepath= download_file(video_url, fn)
            return filepath
        except KeyError as err:
            print(err)
            return None

import json


class LocalStorage:
    def __init__(self, output_file):
        self.output_file = output_file

    def persist_data(self, scraped_products):
        with open(self.output_file, "w") as f:
            json.dump([p.model_dump() for p in scraped_products], f, indent=4)
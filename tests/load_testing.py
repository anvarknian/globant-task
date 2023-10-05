import csv
import os
import random
from time import sleep
# from locust import between

import faker
from locust import HttpUser, task, events

fake = faker.Faker()


def return_html_code(rows):
    headers = ["Status", "Status Code", "Task Id", "Message", "Timestamp"]
    table = "<table style='border-collapse: collapse; border: 1px solid black;'><tr>"
    for header in headers:
        table += f"<th style='border: 1px solid black;'>{header}</th>"
    table += "</tr>"

    for row in rows:
        table += "<tr>"
        table += f"<td style='border: 1px solid black;'>{row.get('status')}</td>"
        table += f"<td style='border: 1px solid black;'>{row.get('status_code')}</td>"
        table += f"<td style='border: 1px solid black;'>{row.get('task_id')}</td>"
        table += f"<td style='border: 1px solid black;'>{row.get('msg')}</td>"
        table += f"<td style='border: 1px solid black;'>{row.get('timestamp')}</td>"
        table += "</tr>"
    table += "</table>"
    html_code = f"<html><body>{table}</body></html>"
    return html_code


def filter_dict_by_keys(input_dict, key_array):
    filtered_dict = {key: input_dict[key] for key in key_array if key in input_dict}
    return filtered_dict


class MyUser(HttpUser):
    # wait_time = between(1, 5)
    jobs_sent = []
    jobs_results = []

    def on_start(self):
        self.exceptions = []

    @staticmethod
    def generate_fake_data(entity_id: int):
        fake_data = {
            'id': entity_id,
            'job': f"{fake.job()} S{entity_id}",
            'department': f"{fake.company()} S{entity_id}",
            'name': f"{fake.name()} S{entity_id}",
            'datetime': fake.date_time_between(start_date='-10y', end_date='now').isoformat(),
            'job_id': entity_id,
            'department_id': entity_id,
        }
        return fake_data

    def post_request(self, endpoint, filename):
        post_request_results = self.client.post(f'/api/{endpoint}/file/',
                                                files={'file': (filename, open(filename, 'rb'))})
        post_request_results.raise_for_status()
        resp = post_request_results.json()
        return resp

    def get_request(self, result):
        get_request_results = self.client.get(f'/api/result/results/?task_id={result["task_id"]}')
        get_request_results.raise_for_status()
        resp = get_request_results.json()
        return resp

    def generate_csv_file(self, filename, fieldnames, endpoint, min_rows, max_rows):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for entity_id in range(min_rows, max_rows):
                fake_data = self.generate_fake_data(entity_id=entity_id)
                fake_data = filter_dict_by_keys(fake_data, fieldnames)
                writer.writerow(fake_data)
        try:
            post_r = self.post_request(endpoint=endpoint, filename=filename)
            self.jobs_sent.append(post_r)
            get_r = self.get_request(result=post_r)
            while get_r['status'] == 'PENDING' and get_r['status'] != 'FAILURE':
                get_r = self.get_request(result=post_r)
                sleep(2)
            if get_r['status'] == 'FAILURE':
                self.exceptions.append(get_r['msg'])
            else:
                self.jobs_results.append(get_r)
        except Exception as e:
            self.exceptions.append(e.__str__())
        finally:
            os.remove(filename)

    def on_stop(self):
        for exception in self.exceptions:
            events.request_failure.fire(
                request_type="CSV Exceptions Upload",
                name="CSV Exceptions Upload",
                response_time=0,
                exception=exception)

    @task
    def generate_and_send_csv_files(self):
        id_locust_runner = fake.uuid4()
        min_rows = random.randint(1, 1000)
        max_rows = random.randint(min_rows, min_rows + 10)
        try:
            self.generate_csv_file(f'jobs_{id_locust_runner}.csv',
                                   ['id', 'job'],
                                   'jobs',
                                   min_rows=min_rows,
                                   max_rows=max_rows)
            self.generate_csv_file(f'departments_{id_locust_runner}.csv',
                                   ['id', 'department'],
                                   'departments',
                                   min_rows=min_rows,
                                   max_rows=max_rows)
            # sleep(10)
            self.generate_csv_file(f'employees_{id_locust_runner}.csv',
                                   ['id', 'name', 'datetime', 'job_id', 'department_id'],
                                   'employees',
                                   min_rows=min_rows,
                                   max_rows=max_rows)
        except Exception as e:
            self.exceptions.append(e.__str__())

    @events.init.add_listener
    def on_locust_init(environment, **kw):
        @environment.web_ui.app.route("/reports")
        def home():
            return """ <html> <head> <style> body { display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; } a { display: inline-block; padding: 10px 20px; margin: 10px; text-align: center; text-decoration: none; background-color: #007BFF; color: #FFFFFF; border: none; border-radius: 5px; cursor: pointer; transition: background-color 0.3s ease; } a:hover { background-color: #0056b3; } </style> </head> <body> <a href="/reports/post_request">Jobs Sent</a> <a href="/reports/get_response">Result of Jobs</a> </body> </html> """

        @environment.web_ui.app.route("/reports/post_request")
        def post_request_results():
            rows = MyUser.jobs_sent
            return return_html_code(rows)

        @environment.web_ui.app.route("/reports/get_response")
        def get_response_results():
            rows = MyUser.jobs_results
            return return_html_code(rows)

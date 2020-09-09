from pprint import pprint
from pymongo import MongoClient
import numpy as np

import vacancy_scraper


scraper_df = vacancy_scraper.get_df()
name = vacancy_scraper.vacancy


def add_vacancies(vacancies_df, f_name):
    counter = 0
    f_client = MongoClient("127.0.0.1", 27017)
    f_db = f_client["vacancy_db"]
    for row in vacancies_df.index:
        mongo_doc = dict()
        mongo_doc["name"] = vacancies_df.loc[row, "name"]
        mongo_doc["link"] = vacancies_df.loc[row, "link"]
        mongo_doc["vac_id"] = int(vacancies_df.loc[row, "vac_id"])
        mongo_doc["source"] = vacancies_df.loc[row, "source"]
        mongo_doc["lower_salary"] = vacancies_df.loc[row, "lower_salary"]
        mongo_doc["highest_salary"] = vacancies_df.loc[row, "highest_salary"]
        mongo_doc["currency"] = vacancies_df.loc[row, "currency"]
        # check vacancy in mongo_db
        # count vacancies which will be added
        if f_db[f_name].count_documents({"vac_id": mongo_doc["vac_id"],
                                         "source": mongo_doc["source"]}) == 0:
            f_db[f_name].insert_one(mongo_doc)
            counter += 1
    print(f"Have been added {counter} vacancies to collection {f_name}")


def find_vacancy(salary, vacancy_collection):
    f_client = MongoClient("127.0.0.1", 27017)
    f_db = f_client["vacancy_db"]
    for vac in f_db[vacancy_collection].find({"$or": [
                                                      {"lower_salary": {"$lte": salary},
                                                       "highest_salary": {"$gte": salary}},
                                                      {"lower_salary": {"$lte": salary},
                                                       "highest_salary": {"$eq": np.nan}},
                                                      {"highest_salary": {"$gte": salary},
                                                       "lower_salary": {"$eq": np.nan}}
                                                     ]
                                             },
                                             {"name": 1, "link": 1, "lower_salary": 1, "highest_salary": 1, "_id": 0}):
        pprint(vac)


add_vacancies(scraper_df, name)
find_vacancy(100000, name)

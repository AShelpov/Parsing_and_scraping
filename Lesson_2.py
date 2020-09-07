import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from pprint import pprint

vacancy = input("Input vacancy for search: ").lower()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                         (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"}


"""===================SCRAPING FROM HH========================="""


main_link_hh = "https://hh.ru"
params_hh = {"L_save_area": "true",
             "clusters": "true",
             "enable_snippets": "true",
             "text": vacancy,
             "showClusters": "true"}

try:
    html_hh = requests.get(main_link_hh + "/search/vacancy", params=params_hh, headers=headers)
    if html_hh.ok:
        soup_hh = bs(html_hh.text, "html.parser")
        pages_hh = soup_hh.find("div", {"data-qa": "pager-block"}).\
                                findChildren("span", {"class": "pager-item-not-in-short-range"}, recursive=False)[-1]
        pages_hh = int(pages_hh.find("a")["data-page"])
    else:
        print(f"Something goes wrong. status code {html_hh.status_code}")
except AttributeError:
    print(f"Sorry, there is no vacancies on hh.ru with name '{vacancy}'. Try another one next time")
else:
    while True:
        try:
            pages_for_scrap = int(input(f"You can gather {pages_hh + 1} pages from hh.ru. "
                                        f"How many pages you want to scrap.\n"
                                        f"Enter number in range from 1 to {pages_hh + 1}: "))
        except ValueError:
            print("You enter not an integer. Try again")
            print("-" * 100)
        else:
            if pages_for_scrap in range(1, pages_hh + 2):
                break
            else:
                print(f"You enter {pages_for_scrap}, it's not in range from 1 to {pages_hh + 1}, try again")
                print("-" * 100)

    # scraping pages from hh.ru
    list_of_hh_vacancies = []
    for page in range(pages_for_scrap):
        params_hh["page"] = page
        html_hh = requests.get(main_link_hh + "/search/vacancy", params=params_hh, headers=headers)
        soup_hh = bs(html_hh.text, "html.parser")


        ordinary_vacancies = soup_hh.find("div", {"data-qa": "vacancy-serp__results"}).\
                                        find("div", {"class": "vacancy-serp"}).\
                                            findChildren("div", {"data-qa": "vacancy-serp__vacancy"})
        for vac in ordinary_vacancies:
            vac_features = {}
            vac_features["name"] = vac.find("div", {"class": "vacancy-serp-item__info"}).find("a").getText()
            vac_features["link"] = vac.find("div", {"class": "vacancy-serp-item__info"}).find("a")["href"]
            vac_features["salary"] = vac.find("div", {"class": "vacancy-serp-item__sidebar"}).getText()
            vac_features["source"] = "hh.ru"
            list_of_hh_vacancies.append(vac_features)


        premium_vacancies = soup_hh.find().find("div", {"data-qa": "vacancy-serp__results"}).\
                                                find("div", {"class": "vacancy-serp"}).\
                                                    findChildren("div", {"data-qa": "vacancy-serp__vacancy "
                                                                                    "vacancy-serp__vacancy_premium"})
        for vac in premium_vacancies:
            vac_features = {}
            vac_features["name"] = vac.find("div", {"class": "vacancy-serp-item__info"}).find("a").getText()
            vac_features["link"] = vac.find("div", {"class": "vacancy-serp-item__info"}).find("a")["href"]
            vac_features["salary"] = vac.find("div", {"class": "vacancy-serp-item__sidebar"}).getText()
            vac_features["source"] = "hh.ru"
            list_of_hh_vacancies.append(vac_features)


    def estimate_lower_salary(salary):
        if salary is not None:
            if "-" in salary:
                salary = salary.split("-")[0]
                lower =str()
                for letter in salary:
                    if letter.isdigit():
                        lower += letter
                try:
                    lower = int(lower)
                except ValueError:
                    return None
                else:
                    return lower
            elif ("от" in salary) or ("from" in salary):
                lower = str()
                for letter in salary:
                    if letter.isdigit():
                        lower += letter
                try:
                    lower = int(lower)
                except ValueError:
                    return None
                else:
                    return lower


    def estimate_highest_salary(salary):
        if salary is not None:
            if "-" in salary:
                salary = salary.split("-")[1]
                highest = str()
                for letter in salary:
                    if letter.isdigit():
                        highest += letter
                try:
                    highest = int(highest)
                except ValueError:
                    return None
                else:
                    return highest
            elif ("до" in salary) or ("till" in salary):
                highest = str()
                for letter in salary:
                    if letter.isdigit():
                        highest += letter
                try:
                    highest = int(highest)
                except ValueError:
                    return None
                else:
                    return highest


    df_hh = pd.DataFrame(list_of_hh_vacancies)
    df_hh["lower_salary"] = df_hh.apply(lambda row: estimate_lower_salary(row["salary"]), axis=1)
    df_hh["highest_salary"] = df_hh.apply(lambda row: estimate_highest_salary(row["salary"]), axis=1)
    df_hh["currency"] = df_hh["salary"].apply(lambda x: x.split(" ")[-1])
    df_hh.drop(columns=["salary"], inplace=True)

    with pd.ExcelWriter("Vacancies.xlsx") as output:
        df_hh.to_excel(output, sheet_name="hh.ru")


"""===================SCRAPING FROM SUPERJOB========================="""

print("="*100)
main_link_sj = "https://www.superjob.ru"
params_sj = {"noGeo": "1",
             "keywords": vacancy}


html_sj = requests.get(main_link_sj + "/vacancy/search/", params=params_sj, headers=headers)
if html_sj.ok:
    soup_sj = bs(html_sj.text, "html.parser")
    pages_sj = soup_sj.find("a", {"class": "icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-Dalshe"})
    if pages_sj is not None:
        pages_sj = int(pages_sj.previousSibling.getText())
        while True:
            try:
                pages_for_scrap = int(input(f"You can gather {pages_sj} pages from SuperJob.ru. "
                                            f"How many pages you want to scrap.\n"
                                            f"Enter number in range from 1 to {pages_sj}: "))
            except ValueError:
                print("You enter not an integer. Try again")
                print("-" * 100)
            else:
                if pages_for_scrap in range(1, pages_sj + 1):
                    break
                else:
                    print(f"You enter {pages_for_scrap}, it's not in range from 1 to {pages_sj}, try again")
                    print("-" * 100)
        list_of_sj_vacancies = []
        for page in range(1, pages_for_scrap + 1):
            params_sj["page"] = page
            html_sj = requests.get(main_link_sj + "/vacancy/search/", params=params_sj, headers=headers)
            soup_sj = bs(html_sj.text, "html.parser")
            vacancies = soup_sj.findAll("div", {"class": "Fo44F QiY08 LvoDO"})

            for vac in vacancies:
                vac_features = {}
                vac_features["name"] = vac.find("div", {"class": "_3mfro PlM3e _2JVkc _3LJqf"}).getText()
                vac_features["link"] = main_link_sj + \
                                       vac.find("div", {"class": "_3mfro PlM3e _2JVkc _3LJqf"}).find("a")["href"]
                salary = vac.find("span", {"class": "_1OuF_ _1qw9T f-test-text-company-item-salary"}).getText()
                if salary == 'По договорённости':
                    vac_features["salary"] = None
                else:
                    vac_features["salary"] = salary
                vac_features["source"] = "superjob.ru"
                list_of_sj_vacancies.append(vac_features)

        df_sj = pd.DataFrame(list_of_sj_vacancies)


        def estimate_lower_salary_sj(salary):
            if salary is not None:
                if "—" in salary:
                    salary = salary.split("—")[0]
                    lower = str()
                    for letter in salary:
                        if letter.isdigit():
                            lower += letter
                    try:
                        lower = int(lower)
                    except ValueError:
                        return None
                    else:
                        return lower
                elif "от" in salary:
                    lower = str()
                    for letter in salary:
                        if letter.isdigit():
                            lower += letter
                    try:
                        lower = int(lower)
                    except ValueError:
                        return None
                    else:
                        return lower


        def estimate_highest_salary_sj(salary):
            if salary is not None:
                if "—" in salary:
                    salary = salary.split("—")[-1]
                    highest = str()
                    for letter in salary:
                        if letter.isdigit():
                            highest += letter
                    try:
                        highest = int(highest)
                    except ValueError:
                        return None
                    else:
                        return highest
                elif "до" in salary:
                    highest = str()
                    for letter in salary:
                        if letter.isdigit():
                            highest += letter
                    try:
                        highest = int(highest)
                    except ValueError:
                        return None
                    else:
                        return highest


        def estimate_currency(salary):
            if salary is not None:
                return salary.split(" ")[-1].split("/")[0]

        df_sj["lower_salary"] = df_sj.apply(lambda row: estimate_lower_salary_sj(row["salary"]), axis=1)
        df_sj["highest_salary"] = df_sj.apply(lambda row: estimate_highest_salary_sj(row["salary"]), axis=1)
        df_sj["currency"] = df_sj.apply(lambda row: estimate_currency(row["salary"]), axis=1)
        df_sj.drop(columns=["salary"], inplace=True)
        total_df = df_hh.append(df_sj, ignore_index=True)

        with pd.ExcelWriter("Vacancies.xlsx") as output:
            total_df.to_excel(output, sheet_name=f"{vacancy}")

        pprint(total_df)


    else:
        print(f"Sorry, there is no vacancies on SuperJob.ru with name '{vacancy}'. Try another one next time")

else:
    print(f"Something goes wrong. status code {html_sj.status_code}")



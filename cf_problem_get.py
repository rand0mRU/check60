import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time, signal, yaml
from colorama import Fore
from yaml_helper import *

def new_test(name, data, config_file=".check60.yaml"):
    try:
        config = yaml.safe_load(open(config_file, "r"))
    except FileNotFoundError:
        print(Fore.RED + "[check60] config file not found" + Fore.RESET)
        sys.exit(1) 
    config[name] = {}
    config[name]["compile"] = ""
    config[name]["runs"] = []
    i = 0
    for test in data:
        config[name]["runs"].append({"start": "", "input": yaml_string(data[i]["input"], style="|"), "output": yaml_string(data[i]["output"], style="|"), "timeout": 1000})
        i += 1
    with open(config_file, "w") as f:
        yaml.dump(convert_to_literal_strings(config), f, allow_unicode=True, default_flow_style=False)


def get_examples(html):
    soup = BeautifulSoup(html, 'html.parser')

    samples = []
    sample_div = soup.find('div', class_='sample-test')

    if sample_div:
        input_divs = sample_div.find_all('div', class_='input')
        output_divs = sample_div.find_all('div', class_='output')

        for inp, out in zip(input_divs, output_divs):
            input_text = inp.find('pre').get_text("\n").strip()
            output_text = out.find('pre').get_text("\n").strip()

            if not input_text.endswith("\n"):
                input_text += "\n"

            if not output_text.endswith("\n"):
                output_text += "\n"

            samples.append({'input': input_text.replace(" \n", "\n"), 'output': output_text.replace(" \n", "\n")})

    return samples


def get_examples_undetected(contest_id="", problem_letter="", link="", html=""):
    if link != "":
        url = link
    else:
        url = f"https://codeforces.com/problemset/problem/{contest_id}/{problem_letter}"

    if "http://" not in url and "https://" not in url:
        url = "http://" + url
        print(url)

    options = uc.ChromeOptions()

    # Настройки для обхода Cloudflare
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-site-isolation-trials')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = None
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)

        # Устанавливаем нормальный user-agent
        driver.execute_cdp_cmd(
            'Network.setUserAgentOverride', {
                "userAgent":
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })

        driver.get(url)

        # Ждем загрузки
        time.sleep(3)

        # Проверяем наличие Cloudflare
        page_source = driver.page_source

        if "Checking your browser" in page_source or "Please wait" in page_source or "Идет проверка" in page_source:
            print("Ожидание завершения проверки Cloudflare...")
            time.sleep(10)  # Ждем завершения проверки

        # Прокручиваем для имитации поведения пользователя
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
        # time.sleep(1)
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        # time.sleep(1)

        # Получаем окончательный HTML
        html = driver.page_source
        return get_examples(html)

    except Exception as e:
        print(f"Ошибка: {e}")
        return []
    finally:
        if driver:
            driver.quit()


def get_contest_problem_fr_link(link):
    link = link.replace("https://", "").replace("http://", "")
    ll = link.split("/")
    if "gym" in ll or "contest" in ll:
        return ll[-3], ll[-1]
    return ll[-2], ll[-1]


def get_from_extension(config_file):

    from flask import Flask, request, jsonify
    import json
    from flask_cors import CORS

    app = Flask(__name__)
    CORS(app)  # Разрешаем запросы из расширения
    result = []

    @app.route('/receive-html', methods=['POST'])
    def receive_html():
        data = request.json
        html_content = data.get('html', '')
        url = data.get('url', '')

        result = get_examples(html_content)
        contest, problem = get_contest_problem_fr_link(url)
        name = contest + "-" + problem

        new_test(name, result, config_file)

        print(Fore.GREEN + f"[check60] test is written as '{name}'" + Fore.RESET)

        return jsonify({'status': 'success'})
    
    print(Fore.GREEN + "[check60] waiting for extension data...\n\tpress CTRL + C for quit" + Fore.RESET)

    app.run(host='127.0.0.1', port=60177, debug=False)

    return result


if __name__ == "__main__":
    print(get_examples_undetected("2181", "A"))
    # get_from_extension()

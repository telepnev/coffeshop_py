
pip list

requirements.txt 
pip install -r requirements.txt
pip install --upgrade -r requirements.txt


allure
pytest simples_tests/allure_http_typed_client.py --alluredir=allure-result
allure serve allure-result

pip install Faker
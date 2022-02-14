import os

import requests

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = '/home/mirzox01/car-rental-crm/scr/firstproject/'

path = os.path.join(BASE_DIR, "media/orders/")

for i in os.listdir(path):
    os.remove(path+i)

url = 'https://mirzox01.pythonanywhere.com/api/task/'
r = requests.get(url=url)
print(r.status_code)

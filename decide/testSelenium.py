from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
options = webdriver.ChromeOptions()
options.headless = False
driver = webdriver.Chrome(options=options)
driver.get("http://127.0.0.1:8081/admin")
username = driver.find_element_by_name('username')
password = driver.find_element_by_name('password')
username.send_keys('davisito')
password.send_keys('diamante1')
driver.find_element_by_id("login-form").submit()
driver.get("http://127.0.0.1:8081/admin/auth/user/add/")
createuser = driver.find_element_by_name('username')
createpassword = driver.find_element_by_name('password1')
confirmpassword = driver.find_element_by_name('password2')
createuser.send_keys('usuarioprueba')
createpassword.send_keys('contrasenaprueba1')
confirmpassword.send_keys('contrasenaprueba1')
driver.find_element_by_id('user_form').submit()
print('Usuario creado')
driver.get("http://127.0.0.1:8081/admin/census/voter/add")
selectuser = Select(driver.find_element_by_name('user'))
selectuser.select_by_visible_text('usuarioprueba')
selectlocation = Select(driver.find_element_by_name('location'))
selectlocation.select_by_visible_text('Sevilla')
insertedad = driver.find_element_by_name('edad')
insertedad.send_keys('45')
selectgenero = Select(driver.find_element_by_name('genero'))
selectgenero.select_by_visible_text('Hombre')
driver.find_element_by_id('voter_form').submit()
print('Voter creado')
driver.get('http://127.0.0.1:8081/admin/census/census/')
censocreadoporlocation = driver.find_element_by_link_text('Sevilla').text
censocreadoporgenero = driver.find_element_by_link_text('Hombre').text
censcreadoporedad = driver.find_element_by_link_text('45').text
print(assertEqual(str(censocreadoporlocation), 'Sevilla'))
print(assertEqual(str(censocreadoporgenero), 'Hombre'))
print(assertEqual(str(censocreadoporedad),'45'))
driver.quit()


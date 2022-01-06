from base.tests import BaseTestCase
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestSeleniumVisualizer(BaseTestCase):
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}
  
    def teardown_method(self, method):
        self.driver.quit()
    
    def test_view_url_guia_error(self):
        resp = self.client.get('/guiaUsuario')
        self.assertEqual(resp.status_code, 404)
     
    def test_guia_ok(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/guia/")
        assert self.driver.find_element(By.CSS_SELECTOR, "h1").text == "Manual de uso de nuevas funcionalidades"
    
    def test_guiaInicio(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/guia/")
        self.driver.find_element(By.LINK_TEXT, "Inicio").click()
        elements = self.driver.find_elements(By.CSS_SELECTOR, ".galeria-port")
        assert len(elements) > 0
    
    def test_guiaAdmin(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/guia/")
        self.driver.find_element(By.LINK_TEXT, "Admin").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("buenas1234")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        assert self.driver.find_element(By.LINK_TEXT, "Administración de Django").text == "Administración de Django"
        assert self.driver.find_element(By.CSS_SELECTOR, "strong").text == "ADMIN"

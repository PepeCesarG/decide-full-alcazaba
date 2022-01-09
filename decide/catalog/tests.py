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

from django.contrib.auth.models import User
from base import mods
from base.tests import BaseTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


import os


class TestRedirecciones(BaseTestCase):
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}
  
    def teardown_method(self, method):
        self.driver.quit()

    def test_census(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/")
        element = self.driver.find_element(By.CSS_SELECTOR, ".imagen-port:nth-child(7) > .hover-galeria")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.LINK_TEXT, "census/").click()
        self.driver.find_element(By.ID, "content").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("buenas1234")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        assert self.driver.find_element(By.CSS_SELECTOR, "#content > h1").text == "Administración de Census"

    def test_auth(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/")
        element = self.driver.find_element(By.CSS_SELECTOR, ".imagen-port:nth-child(4) > .hover-galeria")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.LINK_TEXT, "authentication/").click()
        self.driver.find_element(By.ID, "content").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("buenas1234")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        assert self.driver.find_element(By.CSS_SELECTOR, "#content > h1").text == "Administración de Autenticación y autorización"

    def test_mixnet(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/")
        element = self.driver.find_element(By.CSS_SELECTOR, ".imagen-port:nth-child(8) > .hover-galeria")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.LINK_TEXT, "mixnet/").click()
        self.driver.find_element(By.ID, "content").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("buenas1234")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        assert self.driver.find_element(By.CSS_SELECTOR, "#content > h1").text == "Administración de Mixnet"
    
    def test_store(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/")
        element = self.driver.find_element(By.CSS_SELECTOR, ".imagen-port:nth-child(10) > .hover-galeria")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.LINK_TEXT, "store/").click()
        self.driver.find_element(By.ID, "content").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("buenas1234")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        assert self.driver.find_element(By.CSS_SELECTOR, "#content > h1").text == "Administración de Store"
    
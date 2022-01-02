from django.test import TestCase
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

from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from base.tests import BaseTestCase

class TestBinary():
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.vars = {}
  
    def teardown_method(self, method):
        self.driver.quit()
  
    def test_testBinaryYes(self):
        self.driver.get("http://localhost:8081/booth/25/")
        self.driver.set_window_size(945, 1016)
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("antsolismir")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("12345abc")
        self.driver.find_element(By.CSS_SELECTOR, "button").click()
        element = self.driver.find_element(By.CSS_SELECTOR, "button")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.ID, "q2").click()
        self.driver.find_element(By.CSS_SELECTOR, "button").click()
        self.driver.find_element(By.LINK_TEXT, "logout").click()
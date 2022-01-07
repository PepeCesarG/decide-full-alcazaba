import random
from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient
from django.db import transaction

from voting.models import Voting, Question, QuestionOption
from mixnet.models import Auth
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
import time
import json


class VisualizerTestCase(BaseTestCase):
    
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.vars = {}
        super().setUp()
        
    def tearDown(self):
        self.driver.quit()
        super().tearDown()
    
    def test_get_home_ok(self):
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/")
        assert self.driver.find_element(By.CSS_SELECTOR, "h1").text == "Vota en Decide"
    
    def test_change_language(self):
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/")
        el = self.driver.find_element(By.NAME, "language")
        for option in el.find_elements_by_tag_name('option'):
            if option.text == 'English (en)':
                option.click()
        element = self.driver.find_element(By.NAME, "language")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "language")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "language")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.CSS_SELECTOR, "input:nth-child(4)").click()
        assert self.driver.find_element(By.CSS_SELECTOR, "h1").text == 'Voting in Decide'

    def test_change_language_es(self):
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/")
        el = self.driver.find_element(By.NAME, "language")
        for option in el.find_elements_by_tag_name('option'):
            if option.text == 'spanish (es)':
                option.click()
        element = self.driver.find_element(By.NAME, "language")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "language")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "language")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.CSS_SELECTOR, "input:nth-child(4)").click()
        assert self.driver.find_element(By.CSS_SELECTOR, "h1").text == 'Vota en Decide'
    
    def test_link_user_guide(self):
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/")
        self.driver.find_element(By.LINK_TEXT, "User guide").click()
        assert self.driver.find_element(By.CSS_SELECTOR, "h1").text == "Manual de uso de nuevas funcionalidades"
    
    def test_voting(self):
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/")
        elements = self.driver.find_elements(By.CSS_SELECTOR, ".listavotings")
        assert len(elements) > 0
    
    def test_link_voting(self):
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/")
        self.driver.find_element(By.LINK_TEXT, "Esta va").click()
        url = self.driver.current_url
        assert url == "https://decide-full-alcazaba-visualize.herokuapp.com/visualizer/5/"

    def test_redirectAdmin(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/")
        element = self.driver.find_element(By.CSS_SELECTOR, ".imagen-port:nth-child(1) > .hover-galeria")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.LINK_TEXT, "admin/")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.LINK_TEXT, "admin/").click()
        self.driver.find_element(By.ID, "content").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("buenas1234")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        assert self.driver.find_element(By.LINK_TEXT, "Administración de Django").text == "Administración de Django"
        assert self.driver.find_element(By.CSS_SELECTOR, "strong").text == "ADMIN"
    
    def test_incorrectAdmin(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/admin/login/?next=/admin/")
        self.driver.set_window_size(909, 1016)
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("incorrecto")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        elements = self.driver.find_elements(By.CSS_SELECTOR, ".errornote")
        assert len(elements) > 0
    
    def test_redirectAPI(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/")
        element = self.driver.find_element(By.CSS_SELECTOR, ".imagen-port:nth-child(2) > .hover-galeria")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.LINK_TEXT, "doc/")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.LINK_TEXT, "doc/").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".title").text == "Decide API"

    def test_redirectPostproc(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/")
        element = self.driver.find_element(By.CSS_SELECTOR, ".imagen-port:nth-child(9) > .hover-galeria")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.LINK_TEXT, "postproc/")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.LINK_TEXT, "postproc/").click()
        assert self.driver.find_element(By.CSS_SELECTOR, "h1").text == "Post Proc"
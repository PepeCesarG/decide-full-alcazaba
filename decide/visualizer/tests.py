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

class TestSeleniumVisualizer(BaseTestCase):
    def setup(self):
        self.driver = webdriver.Chrome()
        self.vars = {}
        super().setup
  
    def teardown(self):
        self.driver.quit()
        super.teardown
    
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
    
    def test_access_visualizer_200(self):
        self.driver = webdriver.Chrome()
        response = self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/visualizer/5")
        assert self.driver.find_element(By.CSS_SELECTOR, "h2").text == "Votación no comenzada"

    def test_darkmode(self):
        self.driver = webdriver.Chrome()
        response = self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/visualizer/5")
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(1)").click()
        '''
        assert self.driver.find_element(By.CSS_SELECTOR, ".text-muted > th:nth-child(1)").text == "Opción"
        assert self.driver.find_element(By.CSS_SELECTOR, "th:nth-child(2)").text == "Puntuación"
        assert self.driver.find_element(By.CSS_SELECTOR, "th:nth-child(3)").text == "Votos"
        '''
        assert self.driver.find_element(By.CSS_SELECTOR, "h2").text == "Votación no comenzada"
    
    def test_lightmode(self):
        self.driver = webdriver.Chrome()
        response = self.driver.get("https://decide-full-alcazaba-visualize.herokuapp.com/visualizer/5")
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(1)").click()
        assert self.driver.find_element(By.CSS_SELECTOR, "h2").text == "Votación no comenzada"
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(2)").click()
        assert self.driver.find_element(By.CSS_SELECTOR, "h2").text == "Votación no comenzada"
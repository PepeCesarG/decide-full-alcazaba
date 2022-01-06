from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

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

"""
class AuthTestCase(StaticLiveServerTestCase):

   
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.vars = {}
  
    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        

    def test_simpleCorrectLogin(self):
        print("PRIMER TEST DE SELENIUM")                    
        self.driver.get(f'{self.live_server_url}')
        self.driver.find_element_by_id('auth').click()
        
        print(self.driver.current_url)
        self.driver.current_url.assertEqual(self.driver.get(f'{self.live_server_url}/authentication/'))
        
        
        
     def test_simpleWrongLogin(self):

        self.driver.get(f'{self.live_server_url}/authentication/sign-in//')
        self.driver.find_element_by_id('id_username').send_keys("WRONG")
        self.driver.find_element_by_id('id_password').send_keys("WRONG")       
        self.driver.find_element_by_id('login-form').submit()

        #In case a incorrect login, a div with class 'errornote' is shown in red!
        self.assertTrue(len(self.driver.find_elements_by_class_name('errornote'))==1)
        """
        
        

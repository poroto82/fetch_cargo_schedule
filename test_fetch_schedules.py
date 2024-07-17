import unittest
from unittest.mock import patch, MagicMock
from fetch_schedules import initialize_selenium_driver, get_bearer_token, fetch_schedules, display_schedules

class TestFetchSchedules(unittest.TestCase):

    @patch('fetch_schedules.webdriver.Chrome')
    @patch('fetch_schedules.ChromeService')
    @patch('fetch_schedules.ChromeDriverManager')
    def test_initialize_selenium_driver(self, mock_chrome_driver_manager, mock_chrome_service, mock_chrome):
        driver = initialize_selenium_driver()
        mock_chrome_driver_manager().install.assert_called_once()
        mock_chrome_service.assert_called_once()
        mock_chrome.assert_called_once()

    @patch('fetch_schedules.WebDriverWait')
    @patch('fetch_schedules.webdriver.Chrome')
    @patch('fetch_schedules.ChromeService')
    @patch('fetch_schedules.ChromeDriverManager')
    def test_get_bearer_token(self, mock_chrome_driver_manager, mock_chrome_service, mock_chrome, mock_webdriver_wait):
        driver = MagicMock()
        mock_chrome.return_value = driver
        mock_webdriver_wait.return_value.until.return_value = True
        driver.execute_script.return_value = "dummy_token"
        
        token = get_bearer_token(driver)
        self.assertEqual(token, "Bearer dummy_token")

    @patch('fetch_schedules.requests.get')
    def test_fetch_schedules(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{
            'carrier': {'display_name': 'Carrier1'},
            'voyage': 'Voyage1',
            'etd': 'ETD1',
            'eta': 'ETA1',
            'service': 'Service1'
        }]
        mock_get.return_value = mock_response

        token = "Bearer dummy_token"
        origin_locode = "NLRTM"
        destination_locode = "SGSIN"
        schedules = fetch_schedules(token, origin_locode, destination_locode)
        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0], ('Carrier1', 'Voyage1', 'ETD1', 'ETA1', 'Service1'))

    @patch('builtins.print')
    def test_display_schedules(self, mock_print):
        schedules = [('Carrier1', 'Voyage1', 'ETD1', 'ETA1', 'Service1')]
        display_schedules(schedules)
        self.assertTrue(mock_print.called)

if __name__ == '__main__':
    unittest.main()

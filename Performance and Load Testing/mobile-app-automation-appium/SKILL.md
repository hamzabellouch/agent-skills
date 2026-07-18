---
name: mobile-app-automation-appium
description: Enterprise mobile application automation using Appium 2.0+, UIAutomator2 (Android), XCUITest (iOS), WebdriverIO, and Python. Use when architecting mobile UI test suites, implementing W3C mobile gestures, building Page Object Models, and enforcing mobile performance/SLA metrics.
---

# Mobile Application Automation with Appium 2.0+

This skill defines production standards, automation architecture, W3C gesture abstractions, locator strategy hierarchies, SLA/reliability verification, and executable frameworks for iOS and Android testing using **Appium 2.0+**.

---

## 1. Appium 2.0 Architecture & Driver Management

Appium 2.0 decoupled drivers and plugins from the main Appium server package.

* **Drivers**: Independent packages managing device automation engines:
  * Android: `appium-uiautomator2-driver`
  * iOS: `appium-xcuitest-driver`
  * Flutter: `appium-flutter-driver`
* **Plugins**: Server-side hooks for image comparison, element wait synchronization, relaxed security, or device caching.

### Driver Setup Commands
```bash
appium driver install uiautomator2
appium driver install xcuitest
appium plugin install element-wait
```

---

## 2. Locator Strategy Hierarchy

Selecting efficient, non-brittle locators is critical for mobile test speed and stability.

| Rank | Locator Strategy | Android Target | iOS Target | Performance |
| :--- | :--- | :--- | :--- | :--- |
| **1 (Best)** | **Accessibility ID** | `content-desc` | `accessibilityIdentifier` | Fastest / Native Accessibility API |
| **2** | **Resource ID / ID** | `resource-id` | `name` / `id` | Very Fast |
| **3** | **Native Query** | `-android uiautomator` | `-ios class chain` / `-ios predicate string` | Fast (Native OS evaluation) |
| **4 (Avoid)** | **XPath** | `//android.widget.Button[...]` | `//XCUIElementTypeButton[...]` | Slow (Scans full DOM hierarchy) |

---

## 3. Production Python Appium 2.0 Framework

Below is a production-ready Appium 2.0 framework implementation using Python, `Appium-Python-Client` v3.x+, W3C Action chains for gestures, and Page Object Model design patterns.

### W3C Actions & Page Objects Example (`mobile_app_test.py`)

```python
import pytest
import time
from typing import Tuple
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput


class BasePage:
    """Base Page Object exposing explicit waits and native W3C gesture methods."""
    
    def __init__(self, driver: webdriver.Remote, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def find(self, by: AppiumBy, value: str):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def click(self, by: AppiumBy, value: str):
        element = self.wait.until(EC.element_to_be_clickable((by, value)))
        element.click()

    def enter_text(self, by: AppiumBy, value: str, text: str):
        element = self.find(by, value)
        element.clear()
        element.send_keys(text)

    def swipe(self, start_ratio: Tuple[float, float], end_ratio: Tuple[float, float], duration_ms: int = 800):
        """W3C standard touch swipe gesture using pointer inputs."""
        window_size = self.driver.get_window_size()
        width = window_size['width']
        height = window_size['height']

        start_x = int(width * start_ratio[0])
        start_y = int(height * start_ratio[1])
        end_x = int(width * end_ratio[0])
        end_y = int(height * end_ratio[1])

        actions = ActionChains(self.driver)
        touch_input = PointerInput(interaction.POINTER_TOUCH, "touch")
        
        actions.w3c_actions = ActionBuilder(self.driver, mouse=touch_input)
        actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(duration_ms / 1000)
        actions.w3c_actions.pointer_action.move_to_location(end_x, end_y)
        actions.w3c_actions.pointer_action.release()
        actions.perform()


class LoginPage(BasePage):
    """Page Object for Mobile Application Login Flow."""

    # Locators using Accessibility ID & Native Queries
    USERNAME_FIELD = (AppiumBy.ACCESSIBILITY_ID, "input-username")
    PASSWORD_FIELD = (AppiumBy.ACCESSIBILITY_ID, "input-password")
    LOGIN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "btn-login")
    SUCCESS_BANNER = (AppiumBy.ACCESSIBILITY_ID, "lbl-welcome-message")

    def login(self, username: str, password: str):
        self.enter_text(*self.USERNAME_FIELD, username)
        self.enter_text(*self.PASSWORD_FIELD, password)
        self.click(*self.LOGIN_BUTTON)

    def get_welcome_text(self) -> str:
        return self.find(*self.SUCCESS_BANNER).text


# Driver Configuration Fixture
@pytest.fixture(scope="function")
def mobile_driver(request):
    platform = request.config.getoption("--platform", default="android").lower()
    
    if platform == "android":
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = "Android Emulator"
        options.automation_name = "UiAutomator2"
        options.app = "/path/to/app-staging-release.apk"
        options.app_package = "com.example.mobileapp"
        options.app_activity = ".ui.MainActivity"
        options.auto_grant_permissions = True
        options.new_command_timeout = 60
    elif platform == "ios":
        options = XCUITestOptions()
        options.platform_name = "iOS"
        options.device_name = "iPhone 15 Pro"
        options.platform_version = "17.2"
        options.automation_name = "XCUITest"
        options.app = "/path/to/Build/Products/Debug-iphonesimulator/MobileApp.app"
        options.wda_local_port = 8100
        options.use_new_wda = False

    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    yield driver
    driver.quit()


def test_user_authentication_flow(mobile_driver):
    login_page = LoginPage(mobile_driver)
    
    # Measure App Interaction / Execution Speed SLA
    start_time = time.time()
    
    login_page.login(username="testuser_qa", password="SecretPassword123!")
    welcome_text = login_page.get_welcome_text()
    
    elapsed = time.time() - start_time
    
    assert "Welcome back" in welcome_text
    assert elapsed < 5.0, f"Login flow exceeded SLA threshold! Took {elapsed:.2f} seconds."
```

---

## 4. Mobile Performance & SLA Verification

In automated mobile testing, functional verification must be paired with operational SLA gates:

| Metric | Target SLA | Verification Technique |
| :--- | :--- | :--- |
| **App Cold Start Time** | `< 2.5 seconds` | Record timestamp before `driver.launch_app()` or package start until home screen `ACCESSIBILITY_ID` is displayed. |
| **Login Flow Latency** | `< 4.0 seconds` | Track explicit wait elapsed duration from login button click to landing element visibility. |
| **Test Suite Flakiness** | `< 1.0%` | Zero tolerance for non-deterministic test failures; enforce explicit waits without arbitrary sleeps. |
| **Memory Leak / CPU** | `< 300MB RAM, < 40% CPU` | Query Android `dumpsys meminfo` or iOS `instruments` during long-running end-to-end scenarios. |

---

## 5. Anti-Patterns & Best Practices

### 1. Overusing Deep Relative XPath
* **Anti-Pattern**: Locating elements with `//android.widget.FrameLayout/android.widget.LinearLayout[2]/...`. Minor UI layout refactoring breaks the selector, and XPath traversal over large mobile accessibility trees is slow.
* **Solution**: Request developers to add unique `accessibilityIdentifier` (iOS) and `contentDescription` (Android).

### 2. Hardcoded Delays (`sleep()`)
* **Anti-Pattern**: Using `time.sleep(5)` or `Thread.sleep(5000)` to wait for animations, API network calls, or transitions to complete.
* **Solution**: Use `WebDriverWait` combined with explicit conditions (`element_to_be_clickable`, `visibility_of_element_located`).

### 3. Ignoring W3C Actions API for Gestures
* **Anti-Pattern**: Relying on deprecated JSON Wire Protocol methods like `driver.swipe()` or `driver.tap()`.
* **Solution**: Standardize on W3C `PointerInput` and `ActionChains` for cross-platform gestures (swipes, long-press, pinch-to-zoom).

### 4. Poor Appium Driver Lifecycle Management
* **Anti-Pattern**: Instantiating a new driver session for every single micro-test case without reusing sessions or resetting app state cleanly, inflating execution time by 15-30s per test.
* **Solution**: Group tests logically by feature domain, use `noReset=True` where safe, or execute `driver.reset_app()` between test cases instead of full session teardown.

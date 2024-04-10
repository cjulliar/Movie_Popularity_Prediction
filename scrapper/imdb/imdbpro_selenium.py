from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
import time


options = Options()
options.headless = True  # Pour exécuter en mode sans tête.
driver = webdriver.Chrome(options=options)
start_url = "https://pro.imdb.com/"

try:
    driver.get(start_url)

    # Accepte les cookies
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]'))
        )
        accept_button.click()
    except (NoSuchElementException, TimeoutException):
        pass  # Si le bouton d'acceptation des cookies n'est pas trouvé, continuer sans action
    
    # Clique sur le lien de connexion initial pour faire apparaître le menu
    try:
        login_trigger_xpath = "//a[@id='imdb_pro_login_popover']"
        login_trigger = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, login_trigger_xpath))
        )
        login_trigger.click()
    except (NoSuchElementException, TimeoutException):
        print("Le lien de connexion initial n'a pas été trouvé ou n'était pas cliquable.")
    
    # Attendre et clique sur "Log in with IMDb" dans le menu
    # Localiser le bouton "Log in with IMDb" et cliquer dessus
    try:
        imdb_login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Log in with IMDb')]"))
        )
        imdb_login_button.click()
    except (NoSuchElementException, TimeoutException):
        print("Le bouton 'Log in with IMDb' n'a pas été trouvé ou n'était pas cliquable.")


    # Remplir et soumettre le formulaire de connexion
    try:
        # Remplir le champ email / nom d'utilisateur
        email_input_xpath = "//input[@type='email']"
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, email_input_xpath))
        )
        email_input.send_keys("antoine.moulard@hotmail.com")
        
        # Remplir le champ mot de passe
        password_input_xpath = "//input[@type='password']"
        password_input = driver.find_element(By.XPATH, password_input_xpath)
        password_input.send_keys("Simplon59")
        
        # Clique sur le bouton de connexion
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "signInSubmit"))
        )
        login_button.click()
        time.sleep(10) # Temps pour saisir manuellement le captcha
    except (NoSuchElementException, TimeoutException):
        print("Le bouton de connexion n'a pas été trouvé ou n'était pas cliquable.")
        


    try:
        # Localiser le menu "Titles"
        titles_menu_xpath = "//span[contains(text(), 'Titles')]"
        titles_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, titles_menu_xpath))
        )
        
        # Simuler le survol du menu "Titles"
        ActionChains(driver).move_to_element(titles_menu).perform()
        
        # Attendre que le sous-menu soit visible et cliquer sur "Released Movies"
        released_movies_xpath = "//a[contains(text(), 'Released Movies')]"
        released_movies = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, released_movies_xpath))
        )
        released_movies.click()
        time.sleep(10)

        
        # Trouve tous les liens des films sur la page actuelle
        movies_links = driver.find_elements(By.XPATH, "//h5[@class='a-size-base-plus']/a[@class='a-link-normal']")

        # Parcourir chaque lien de film et cliquer dessus
        for movie_link in movies_links:
            # Vous pouvez utiliser l'attribut 'href' pour identifier un film spécifique si nécessaire
            movie_url = movie_link.get_attribute('href')
            print(f"Ouverture de la page du film : {movie_url}")
            
            # Clique sur le lien pour ouvrir la page de détails du film
            movie_link.click()
            
                        
            # Vérifiez si le filtre des pays est présent sur la page
            area_filter_present = driver.find_elements(By.ID, 'area_filter_dropdown')
            if area_filter_present:
                # Cliquez sur le menu déroulant
                dropdown = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'area_filter_dropdown'))
                )
                dropdown.click()

                # Sélectionnez "France" dans le menu déroulant
                france_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//select[@id='area_filter_dropdown']/option[contains(text(), 'France')]"))
                )
                ActionChains(driver).move_to_element(france_option).perform()
                france_option.click()

                # Attendez que la page se recharge avec les informations filtrées pour la France
                WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.ID, 'area_filter_dropdown'), "France"))

                # Localisez la ligne 'Week 1' et extrayez les informations
                rows = driver.find_elements(By.CSS_SELECTOR, 'table#box_office_mojo_table > tbody > tr')
                week1_data = []
                for row in rows:
                    if row.find_elements(By.XPATH, ".//p[contains(text(), 'Week 1')]"):
                        cells = row.find_elements(By.XPATH, ".//td")
                        week1_data = [cell.text for cell in cells]
                        break  # Quittez la boucle une fois 'Week 1' trouvé

                print(week1_data)  # Ou traitez / enregistrez les données comme nécessaire

            # Retournez à la liste des films après avoir extrait les données ou si le filtre n'était pas présent
            driver.back()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h5[@class='a-size-base-plus']/a")))

            
    except (NoSuchElementException, TimeoutException):
        print("L'option du menu n'a pas été trouvée ou n'était pas cliquable.")

    
finally:
    driver.quit()


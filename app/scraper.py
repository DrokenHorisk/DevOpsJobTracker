from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from .models import JobOffer
from . import db
from datetime import datetime

def scrape_swissdevjobs_selenium():
    print("Lancement du scraper SwissDevJobs.ch (Selenium)...")
    url = "https://swissdevjobs.ch/jobs/DevOps/Suisse"
    BASE_URL = "https://swissdevjobs.ch"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(5)  # Laisse le JS charger

    offres = driver.find_elements(By.CSS_SELECTOR, "div[data-test='card-body']")
    ajout = 0
    total = len(offres)

    for offer in offres:
        try:
            # Titre & lien (sur la liste)
            a_poste = offer.find_element(By.CSS_SELECTOR, "a[href^='/jobs/']")
            try:
                titre_div = a_poste.find_element(By.CSS_SELECTOR, ".jobteaser-name-header")
                titre_txt = titre_div.text.strip()
            except:
                titre_txt = a_poste.text.strip() or a_poste.get_attribute('title') or "N/A"

            raw_href = a_poste.get_attribute("href")
            if raw_href.startswith("http"):
                lien = raw_href
            else:
                lien = BASE_URL + raw_href
        except Exception as e:
            print("Pas de titre ou lien pour une offre :", e)
            continue

        # Unicité : on ne scrape que si le lien n'est pas déjà en base
        if JobOffer.query.filter_by(lien=lien).first():
            continue

        # Entreprise
        try:
            entreprise_elem = offer.find_element(By.CSS_SELECTOR, "span[aria-label='hiring organization']")
            entreprise_txt = entreprise_elem.text.strip()
        except:
            entreprise_txt = "N/A"

        # Keywords (badges, visibles sur la liste)
        try:
            badges = offer.find_elements(By.CSS_SELECTOR, ".technology-badge")
            keywords = ", ".join([badge.text.strip() for badge in badges])
        except:
            keywords = ""

        # -------------------------------
        # Aller sur la page de détail pour plus d'infos
        salaire = ""
        localisation = ""
        try:
            # Ouvre dans un nouvel onglet (plus safe)
            driver.execute_script("window.open(arguments[0]);", lien)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(2)  # Laisse la page charger

            # Salaire (détail)
            try:
                salaire_elem = driver.find_element(By.CSS_SELECTOR, "div[aria-label='annual salary range']")
                salaire = salaire_elem.text.strip()
            except:
                salaire = ""

            # Localisation (détail)
            try:
                localisation_elem = driver.find_element(By.CSS_SELECTOR, "div[aria-label='hiring organization address'] span")
                localisation = localisation_elem.text.strip()
            except:
                localisation = ""

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except Exception as ex:
            print("Impossible de récupérer le détail (salaire/localisation) pour", titre_txt, ":", ex)
            salaire = ""
            localisation = ""
            # Revenir au tab principal quoiqu'il arrive
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

        date_publication = datetime.today().date()
        job = JobOffer(
            titre=titre_txt,
            entreprise=entreprise_txt,
            lien=lien,
            date_publication=date_publication,
            salaire=salaire,
            localisation=localisation,
            keywords=keywords,
        )
        db.session.add(job)
        ajout += 1

    db.session.commit()
    print(f"Scraper SwissDevJobs (Selenium) : {ajout} nouvelles offres ajoutées sur {total} trouvées.")
    driver.quit()

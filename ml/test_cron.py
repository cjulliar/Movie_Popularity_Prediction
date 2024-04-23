print("---------------------------------------")
print("Hello le cron fonctionne ! :)")
print("---------------------------------------")

import datetime
import time

# Affichage de l'heure actuelle
print("Heure actuelle avant exécution du script :", datetime.datetime.now())

# Votre code de script ici...
time.sleep(5)

# Affichage de l'heure actuelle après exécution du script
print("Heure actuelle après exécution du script :", datetime.datetime.now())

#!/bin/sh

# Vérifie si le service cron est installé et démarre le service si ce n'est pas le cas
if [ ! -f /etc/init.d/cron ]; then
    apt-get update
    apt-get install -y cron
fi

# Écrire les tâches cron via crontab
(crontab -l 2>/dev/null; echo "0 7 * * 1 cd /app && /usr/local/bin/scrapy crawl semaine_prochaine > /var/log/test_spider_semaine_prochaine.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 12 * * 4 cd /app && /usr/local/bin/scrapy crawl semaine > /var/log/test_spider_semaine.log 2>&1") | crontab -


# Appliquer les permissions nécessaires aux fichiers log
touch /var/log/test_spider_semaine_prochaine.log
touch /var/log/test_spider_semaine.log


chmod 0666 /var/log/test_spider_semaine_prochaine.log
chmod 0666 /var/log/test_spider_semaine.log


# Redémarrer le service cron pour que les changements prennent effet
service cron restart

# Affichage des tâches cron pour vérification
crontab -l

# Garder le conteneur en cours d'exécution en exécutant une commande qui ne se termine pas
tail -f /dev/null

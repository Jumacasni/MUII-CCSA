#!/bin/sh

# Necesario para que reconozca el dominio del nginx.conf
docker exec --user www-data servicio_nextcloud_76591779 php occ config:system:set trusted_domains 1 --value=nextcloud
docker exec --user www-data servicio_nextcloud_76591779 php occ config:system:set trusted_domains 2 --value=hadoop.ugr.es

# Deshabilitación de los plugins indicados
docker exec -u www-data -it servicio_nextcloud_76591779 php occ app:disable accessibility
docker exec -u www-data -it servicio_nextcloud_76591779 php occ app:disable dashboard
docker exec -u www-data -it servicio_nextcloud_76591779 php occ app:disable firstrunwizard
docker exec -u www-data -it servicio_nextcloud_76591779 php occ app:disable nextcloud_announcements
docker exec -u www-data -it servicio_nextcloud_76591779 php occ app:disable photos
docker exec -u www-data -it servicio_nextcloud_76591779 php occ app:disable weather_status
docker exec -u www-data -it servicio_nextcloud_76591779 php occ app:disable user_status
docker exec -u www-data -it servicio_nextcloud_76591779 php occ app:disable survey_client
docker exec -u www-data -it servicio_nextcloud_76591779 php occ app:disable support
docker exec -u www-data -it servicio_nextcloud_76591779 php occ app:disable recommendations
docker exec -u www-data -it servicio_nextcloud_76591779 php occ app:disable updatenotification
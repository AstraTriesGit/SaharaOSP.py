gcloud compute instances create client-1 \
--project=ethereal-pride-413807 \
--zone=asia-south2-a\
--machine-type=e2-standard-2 \
--network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default --maintenance-policy=MIGRATE \
--provisioning-model=STANDARD \
--service-account=779625694862-compute@developer.gserviceaccount.com \
--scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
--tags=http-server,https-server \
--create-disk=auto-delete=yes,boot=yes,device-name=client-1,image=projects/debian-cloud/global/images/debian-12-bookworm-v20240213,mode=rw,size=50,type=projects/ethereal-pride-413807/zones/asia-south2-a/diskTypes/pd-balanced \
--no-shielded-secure-boot \
--shielded-vtpm \
--shielded-integrity-monitoring \
--labels=goog-ec-src=vm_add-gcloud \
--reservation-affinity=any


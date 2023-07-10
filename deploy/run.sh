docker-compose down
cd ../
cp -r booking_app/booking_app  deploy/booking_app_project
cd deploy
docker-compose up -d
Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

sudo docker push kasyak999/foodgram-gateway
sudo docker push kasyak999/foodgram-frontend
sudo docker push kasyak999/foodgram-backend

docker build -t kasyak999/foodgram-gateway .
docker build -t kasyak999/foodgram-frontend .
docker build -t kasyak999/foodgram-backend .

docker compose -f docker-compose.production.yml up
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml pull

docker compose exec backend bash
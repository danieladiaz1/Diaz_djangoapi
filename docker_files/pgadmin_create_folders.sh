mkdir -p ./data/pgadmin4/data
mkdir -p ./data/pgadmin4/servers

mkdir -p ./data/pgadmin4_prod/data
mkdir -p ./data/pgadmin4_prod/servers

mkdir -p ./data/postgis_data

touch ./data/pgadmin4/servers/servers.json
touch ./data/pgadmin4_prod/servers/servers.json

sudo chmod -R 0777 ./data/pgadmin4 ./data/pgadmin4_prod ./data/postgis_data

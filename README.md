From your terminal:

1. mkdir code && cd code
2. git clone https://github.com/khalikovartur/google_sh_with_postgresdb.git
3. cd google_sh_with_postgresdb
4. insert google credentials into "creds.json" 
5. docker-compose up -d --build
6. docker-compose exec web python scripts.py


Open 127.0.0.1:8000 in your browser.Every 2 minutes the data will upgrade.
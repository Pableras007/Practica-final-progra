# Práctica final programación II


    El trabajo realizado muestra varios dashboards sobre el conjunto de datos "results.csv" que contiene informacion sobre datos de rugby internacional desde 1878
    hasta el último que fue el mundial en 2023.
    
    Lo primero el conjunto de datos. El conjunto de datos lo he sacado de un sitio web llamado kaggle que sirve para exactamente eso, buscar datasets. El tema lo 
    escogí puesto que soy jugador de rugby y ya que vamos ha hacer un trabajo y se puede escoger tema al menos hacerlo de algo que me guste.
    
    Mi segundo movimiento fue descargarme la practica de github y clonarla en mi pychram, queria ver el funcionamiento de esta con el docker-compose y como se
    tenia que ver este. Una vez entendi el funcionamiento y observe su practica ya me puse con la mia.

    Para mis dashboard tenia estas variables:
    date - date of the match
    home_team - the name of the home team
    away_team - the name of the away team
    home_score - full-time home team score
    away_score - full-time away team score
    competition - the name of the tournament
    stadium - the name of the stadium where the match was played
    city - the name of the city/town/administrative unit where the match was played
    country - the name of the country where the match was played
    neutral - TRUE/FALSE column indicating whether the match was played at a neutral venue
    world_cup - TRUE/FALSE column indicating whether the match was during a Rugby World Cup

    Por lo que con esto y el codigo me separe los archios server.py y dashboard.py.
    El server.py fue muy sencillo de modificar ya solo tenia que cambiar sus variables por las mias.
    En cuanto al dashboard lo que he realizo han sido varios. El primero sirve para escoger un equipo y podamos seleccionar el porcentaje de vistorias que tiene a nivel
    internacional tanto en casa, como fuera o en total. El segundo seleccionas 2 equipos y la cantidad de años en los que queremos ver los resultados de estos 2 en 
    contra.El tercero para ver el desempeño del equipo que quieras en el mundial. El 4 son solo las finales de los mundiales del equipo que selecciones, con el numero 
    total de victorias. El quinto un grafico de el equipo con mas mundiales a el que menos. y por Ultimo la cantidad de partidos jugados cada año.
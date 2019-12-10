# league-analytics
League of Legends analytics by Ahir Chatterjee (CrusherCake)

riot-api:
    Riot API is a workspace that is self-contained. Here is a description of what to expect from it:
    - riotapicalls.py is an API built on top of the Riot API. It's intent is to universalize all of the functions/endpoints that you might call into functions, hiding all of the backend calls that need to be done.
    - apikey.txt is your Riot API key. This is intentionally left blank because it's unwise to put an API key onto a public github. To make this work for you, just add your own key into there. You can get this by logging into https://developer.riotgames.com/ with your account and copying it from there.
    - esportsapicalls.py is a sketchy API built on top of the "Esports API" that is used by Riot internally, but has some functionality outside of it. Because it's not documented and changes a lot, the functions in here simply may not work depending on the changes they try to make.

Quantbox
--------

Repo for quantbox


Steps to run 
------------

1) Get the access token by using below URL. This needs to be done once in a day. Token is valid for 24hrs
   
   - https://kite.trade/connect/login?api_key=<api_key>&v=3
   - Upon successful login, it will return an request_token in the URL of the page
   - This request token can be used to access data for the entire day.
   - We can set access token using below program
   - python kite_utils.py <request_token>

2)  

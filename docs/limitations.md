# Limitations and Improvements

## Modelling
- try different embeddings
- improve output texts (put them in present, 
apply context from new ticket to solution )
- create a chat bot like user experience, suggesting a solution,
asking if this helps, and suggest 2nd best if not and so on
- use negative solutions and warn the agent of them (ask business experts from client)
- make use of date information (ask business experts from client)

## Serving
- adapt serving routine to clients needs

## Productionalization
- include checks on schema, types, values etc in functions
- create test cases for package
- host on docker server in cloud or on premise (client)
- build up database for past tickets so one can consume them easily
- use CI/CD & MLOps to retrain,
update, integrate new versions
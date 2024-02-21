# The background of the ticket engine  

The ticket engine is an engine, helps IT service employees
in solving IT tickets by giving them hints and/or recommendations
how to solve a new ticket. 

## The use case
As described in the requirements, 
"A lot of the tickets the client handles are
redundant and might just need a little tweak to
solve the problem of the client's customer."

I use this data to build an engine.

## Assumptions
The following assumptions are made, as it is not otherwise statet:
> Information about solutions are only present in the past tickets.

This means, that one cannot use the general knowledge of LLMs to 
provide helpful solutions. This assumption is reasonable, if the 
infrastructure is sufficient complex, so that general/basic IT knowledge
like LLMs have is not helpful

> Date and time of the tickets are not significant.

This is a simplification, as IT tickets correlate in time. However, our 
set of known issues is small and obtained in a short time period (one month). 
In addition, it might be helpful if the engine is insensitive of time, 
in order to find systematic issues which appear infrequently.

> If a solution to ticket did not work, one can't infer any information
> of that solution.

This simplification is made due to time constraints, 
one can clearly learn something from things that didn't work. 
Administrators should not try things which are proven to not work.
However, one needs to be very careful that one applies this information
only in the proper context, as exact that solution could work
for a slightly different ticket. 

> All Agents work equally efficient

This assumption is to avoid discrimination, thus I do not use the agent name.

## Building blocks
The assumptions mainly define the logic of the engine. 
There are two building blocks of the proposed solution:

- [Issue](reference.md#ticket_engine.Issue.issue):
An Issue in the implementation is not only the relvant text information 
about the IT issue, but also contains derived representations like embeddings.
- [engine](reference.md#ticket_engine.ticket_engine.ticket_engine):
The engine itself uses Issues (known and unknown), is able to 
infer recommended actions or other information to new tickets, and
has various possibilities to serve.

## Preprocessing
The assumptions define the preprocessing of the training issues:
- remove training issue when the solution did not work
- take only "Issue", "Category", "description", and "solution" column 

## Core
The idea of this engine is, for a given new issue, 
to search for similar (or the most similar) issues 
where the solution is known and propose these 
solutions to the agent. 
To this end, we use a semantic embedding provided from
aleph alpha to represent the each of the string information
(Issue, Category, description) in terms of float vectors.
> **similarity score:** 
> 
> score = mean(cos(issue_1,issue_2), cos(category_1,category_2), cos(description_1,description_2))$ 
> 
> where cos is the cosine similarity between two vectors and the
> arguments are the respective embeddings.

There is a reason to take the arithmetic mean, because that
weights all pieces of information equally and also honors the fact, 
that boundaries between categories seem blurry 
(I believe that category is not a 100% discriminator).

## recommendations
For a given Issue, the similarities to known issues are computed 
and the solutions delivered. Multiple ways can be thought of:
- recommend the solution to the most similar issue
- recommend the solutions of the n-most similar issues with 
a threshold on the score
- deliver the score as indication of certainty of the model

## serving
One can think of multiple ways to serve the results:
- gradio app to interactively enter issues and generate responses
- FLASK REST API to automatically generate responses for every new ticket
# Tutorial

Get started with the Ticket Engine! 

To get started, you need to install the package,
an AlephAlpha authenticate token (see webpage), 
and training tickets (in form of csv, xlsx, json). 
You can also use test tickets to see what recommendations it will generate.
You can then apply this example code to start the ticket engine:

## Code example

```
from ticket_engine import Issue, TicketEngine

AA_TOKEN= "PLEASE_FILL"
folder_path = "PLEASE_FILL"
test_tickets_path = "PLEASE_FILL"

engine = TicketEngine(folder_path, test_tickets_path, AA_TOKEN)
```

There are several frontends to choose from:

```
engine.gradio_df()
```
Will display a Gradio app where you can enter ticket information on a tabular form and compute
the recommendations. It will show the test issues as example.

```
engine.gradio_single()
```

will display a Gradio app with a formular to enter ticket information. It will generate a response.

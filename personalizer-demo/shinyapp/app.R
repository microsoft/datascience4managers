library(shiny)
library(odbc)

con <- dbConnect(odbc::odbc(), "PostgreSQL35W")

ui <- fluidPage(
  titlePanel("Responses"),
  
  mainPanel(
    tableOutput("mytable")
  )
)

valueFunc = function() {
  result <- dbSendQuery(con, "SELECT side, action, choice, CAST(COUNT(*) AS VARCHAR(10)) FROM food_choices GROUP BY side, action, choice ORDER BY side, action, choice")
  result_set <- dbFetch(result)
  dbClearResult(result)
  return(result_set)
}

server <- function(input, output, session) {
    standings <- reactivePoll(intervalMillis = 5000, session = session, checkFunc = valueFunc, valueFunc = valueFunc)
    output$mytable <- renderTable(standings())
}

shinyApp(ui = ui, server = server)


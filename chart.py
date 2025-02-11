css = r"""
<style>
.gantt-chart-container {
    margin-top: 15px;
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    margin: auto;
    padding: 2px;
    margin: 2px;
    margin-bottom: 15px;
    inset-inline-end: none;
}

.gantt-chart-row {
    margin-top: 15px;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 20px; /* Add a gap between server charts */
}



.gantt-chart-task-container {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: flex-start;
    margin-top: 15px;
}



.gantt-chart-task {
    background-color: aqua; 
    text-align: center;
    border: 1px solid black;
    padding: 10px;
    border-radius: 5px;
    margin-right: 5px;
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 10vw; /* Adjust the width as needed */
    max-width: 200px; /* Limit the maximum width */
    position: relative;
}

.gantt-chart-task-timestamp{
    
    margin-top: 5px;
    display: inline; 
}
.start-time {
    position: absolute;
    left: 0;
    border: 5px solid black;
    border-width: 5px;
    border-radius: 5px;
    background-color: black;
    color: white;
    margin-right: 70px; /* Adjust the value as needed */

}

.end-time {
    position: absolute;
    right: 0;
    border: 1px solid black;
    border-width: 4px;
    border-radius: 5px ;
    background-color: black;
    color: white;
  
     /* Adjust the value as needed */
    
}


.gantt-chart-task-label {
    color: black;
    font-weight: bold;
    margin-top: -5px;
}

</style>


"""

# chart_html = ""
# for server in servers:
#     chart_html += f'<div class="server_head"><h3>Server {loop.index}:</h3></div>'
#     chart_html += f'<div class="gantt-chart-container">'
#     for task in server:
#         chart_html += f"""
#         <div class="gantt-chart-task" data-process="{task.process_name }" data-index="{index }" style="background-color: {{task.color}};">
#                     <div class="gantt-chart-task-label">ID: { task.id }</div>
#                     <div class="gantt-chart-task-timestamp">
#                         <span class="start-time">{ task.start }</span>
#                         <span class="end-time">{ task.end }</span>
#                     </div>
#                 </div>
#         """
#     chart_html += r"</div>"

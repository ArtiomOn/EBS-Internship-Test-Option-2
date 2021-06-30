# Django Rest Framework - Internship tasks
**By Artiom Oncea**

# Milestone 2-3

1. Register - user send first name, last name, username, email, password and receive JWT token for authentication
   

2. Get user token - user send email, password and receive JWT token for authentication
   

3. Get list of users - user receive a list with id and full name of all users from the project
   

4. Create a task - user send title, description, owner. User receive task data, and the new task is assigned to current user


5. View list of tasks - user filter tasks by owner, status, ordering and user can filter tasks by title. User receive 
   data of all founded tasks from the project


6. View task details by id - user send task_id and receive task details: id, duration, title, description, status, owner


7. Assign a task to user - user send task_id and user_id. User receive email notification and successful response after 
   updating the new task owner


8. Complete a task - user send task_id and status. User receive email notification and successful response after updating of task
status in completed


9. Remove task - user send task_id and receive successful response after task deletion


10. Add comment to task - user send task_id and comment text. User receive email notification, comment_id, content and 
    task_id of the new comment


11. View task comments - user send task id and receive list of all comments added to this task


12. Start a timer for my task - user send task id and receive successful response after logging the start of task in DB


13. Stop timer for the started task - user send task id and receive successful response after adding a time log for this task


14. Add time log for a task on a specific date - user manually send task id, date, duration in minutes and receive 
    timelog_id, date, duration, task_id and owner


15. Get a list of time logs records by task - user send task id and receive a list of all time logs created for this task


16. Get the logged time in last month - user send date('this_week', 'this_month', 'this_year') and receive all sorted tasks


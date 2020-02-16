# jenkinsBot
Manage Jenkins using Slack

For you convenience in CI/CD this jenkins bot can help the Developer and Devops team in managing the Jenkins Server through Slack Channel. The permission to operate and trigger build are dependent on the permission granted based on the Slack channel calls.

Prerequistes-
1. Configure the configs.json file in accordance to your Slack workspace
2. Add the defined slack channels for the different teams in jenkins_bot.py file.

Functionalities- 
It can assist you in the following tasks :construction_worker::
1. Use "@Jenkins build <jobName>" to build the job.
2. Use "@Jenkins view <viewName>" to list all the jobs in given view.
3. Use "@Jenkins list view" to list all the view.
4. Use "@Jenkins list jobs" to list all jobs in jenkins.

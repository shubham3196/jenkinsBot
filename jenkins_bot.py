from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
import json, jenkins, time, re
import requests, time

tokens = {}
with open('configs.json') as json_data:
    tokens = json.load(json_data)

#Slack channels
devops_channel = ['GGF483V5E']
dev_channel = ['GHEHSVDHN']

# Fixed tokens
dev_assist_msg = "\nFor you convenience in CI/CD ,I can assist you in the following tasks :construction_worker::\n1. Use *\"@Jenkins view <viewName>\"* to list all the jobs in given view.\n2. Use *\"@Jenkins list view\"* to list all the view.\n3. Use *\"@Jenkins list jobs\"* to list all jobs in jenkins.\n4. Use *\"@Jenkins list plugins\"* to list all the plugins with installed version."
devops_assist_msg = "\nFor you convenience in CI/CD ,I can assist you in the following tasks :construction_worker::\n1. Use *\"@Jenkins build <jobName>\"* to build the job.\n2. Use *\"@Jenkins view <viewName>\"* to list all the jobs in given view.\n3. Use *\"@Jenkins list view\"* to list all the view.\n4. Use *\"@Jenkins list jobs\"* to list all jobs in jenkins."
slack_events_adapter = SlackEventAdapter(str(tokens.get("slack_signing_secret")), "/slack/events")
slack_client = SlackClient(str(tokens.get("slack_bot_token")))

def get_jenkins_instance():
    try:
    	instance = jenkins.Jenkins(str(tokens.get('url')),
		username = str(tokens.get('username')),
		password=str(tokens.get('password')))
	return instance
    except Exception as e:
	print('login error')
	#raise Exception("Sorry!!! Error occured in processing request :no_mouth:.\nPlease contact the DevOps Team.:computer:")

# Template Data
welcome_text = ["hi","hello","hey","info","hola","help"]
list_build_text = ["build", "builds"]
list_view_text = ["list view","list views"]
list_jobs_text = ["list job","list jobs"]
list_jobInView_text = ["view"]
list_plugin = ["list plugin","list plugins"]
version = ["version"]

# Example responder to greetings
@slack_events_adapter.on("app_mention")
def app_mention(event_data):
    try:
        data = event_data["event"]
        channel = data["channel"]
        user_text = data["text"]
        user_text = user_text.replace('<@UGGCWSEHF> ', '')
        text = user_text.replace('<@UGGCWSEHF> ', '').lower()
	if any(x in text for x in version):
	    message = get_version(get_jenkins_instance())
	    slack_client.api_call(
            "chat.postMessage",
            channel='{0}'.format(channel),
            attachments=[{"text": "{0}".format(message), "color": "#3498DB" }])
        elif any(x in text for x in welcome_text):
            message = "Welcome to *Jenkins Automation* <@%s>... _Build great things at any scale_ " % data["user"]
            if (channel in devops_channel):
                publish_msg = devops_assist_msg
            elif (channel in dev_channel):
                publish_msg = dev_assist_msg
	    slack_client.api_call(
            "chat.postMessage",
            channel='{0}'.format(channel),
            attachments=[{"text": "{0}".format(message), "color": "#2EB886" },{"text": "{0}".format(publish_msg), "color": "#2EB886" }])
        elif any(x in text for x in list_build_text):
	    if (channel in devops_channel):
		job_name = user_text.replace('build ', '')
		color = "#2EB886"
		arr = ['prod','Prod','PROD']
		if not any(re.findall('|'.join(arr), job_name)):
		    message = build_job(get_jenkins_instance(),job_name,data)
		else:
		    message = "Apologies!!! Cannot build *Production* jobs. Kindly contact DevOps Team.:computer:"
            else:
		message = "Apologies!!!.. You are not allowed to build jobs. Kindly contact DevOps Team.:computer:"
		color = "#A30200"
	    slack_client.api_call(
            "chat.postMessage",
            channel='{0}'.format(channel),
            attachments=[{"text": "{0}".format(message), "color": color }])
        elif any(x in text for x in list_view_text):
            message = list_view(get_jenkins_instance())
            slack_client.api_call(
            "chat.postMessage",
            channel='{0}'.format(channel),
            attachments=[{"text": "{0}".format(message), "color": "#2EB886" }])
        elif any(x in text for x in list_jobInView_text):
            message = list_job_in_view(get_jenkins_instance(),user_text)
	    slack_client.api_call(
            "chat.postMessage",
            channel='{0}'.format(channel),
            attachments=[{"text": "{0}".format(message), "color": "#2EB886" }])
        elif any(x in text for x in list_jobs_text):
            message = list_jobs(get_jenkins_instance())
            slack_client.api_call(
            "chat.postMessage",
            channel='{0}'.format(channel),
            attachments=[{"text": "{0}".format(message), "color": "#2EB886" }])
        elif any(x in text for x in list_plugin):
            message = list_plugins(get_jenkins_instance())
	    slack_client.api_call(
            "chat.postMessage",
            channel='{0}'.format(channel),
            attachments=[{"text": "{0}".format(message), "color": "#2EB886" }])
        else:
            message = "Apologies!!! Command not found... Please input *\"@Jenkins hi\"* for details"
            slack_client.api_call(
            "chat.postMessage",
            channel='{0}'.format(channel),
            attachments=[{"text": "{0}".format(message), "color": "#A30200" }])
    except Exception as e:
	errorLogs = open('error.log', 'a')
	errorLogs.write("\n["+str(time.strftime("%x %X"))+"] User:"+data["user"]+" |Error| "+ str(e))
        error_handler(e, channel)


def list_plugins(server):
    try:
	send_data = "List of plugins and their version in the Jenkins Server:- :memo:\n"
	response = requests.get('http://slack:d36af685693d3394f58c116edfb1607e@35.154.209.120:8080/pluginManager/api/json?depth=1&?xpath=/*/*shortName|/*/*/version')
	data = response.json()['plugins']
	for plugin in data:
    	    send_data += "*{}* : {}\n".format(plugin["shortName"], plugin["version"])
	return send_data
    except:
        raise Exception("Error occured in running function...Kindly check for correct spelling:heavy_check_mark:")


def build_job(server,job_name,data):
    try:
        server.build_job(job_name, parameters=None, token=None)
        send_data = "%s triggerd by <@%s>" % (job_name, data["user"])
	return send_data
    except Exception as e:
	print(e)
        raise Exception("Error occured in building "+str(job_name)+"...Kindly check for correct spelling:heavy_check_mark:")


def get_version(server):
    try:
        data = server.get_version()
	return data
    except Exception as e:
	print(e)
        raise Exception("Error occured in running function...Kindly check for correct spelling:heavy_check_mark:")


def list_job_in_view(server,view_name):
    try:
        view_name = view_name.replace('view ', '')
	jobs_dict = get_view_names(server)
	view_key = jobs_dict.get(view_name.lower())
        selected_jobs = server.get_jobs(folder_depth=0, view_name=view_key)
        selected_jobs = [str(i['name']) for i in selected_jobs if 'name' in i]
        send_data = "List of jobs in view - *"+view_key+"* :memo:\n"
	for i in range(len(selected_jobs)):
            send_data += "{}: {}\n".format(i + 1, selected_jobs[i])
        return send_data
    except:
	raise Exception("Error occured in running list job in view")


def get_view_names(server):
    views = server.get_views()
    jobs = [str(i['name']) for i in views if 'name' in i]
    lowercase_jobs = [str(i['name'].lower()) for i in views if 'name' in i]
    job_dict = dict(zip(lowercase_jobs, jobs))
    return job_dict


def list_view(server):
    try:
        send_data = "List of views in the Jenkins Server:- :memo:\n"
    	views = server.get_views()
    	views = [str(i['name']) for i in views if 'name' in i]
    	for i in range(len(views)):
            send_data += "{}: {}\n".format(i + 1, views[i])
        return send_data
    except:
	raise Exception("Error occured in running list view")

def list_jobs(server):
    try:
        send_data = "List of jobs in the Jenkins Server:- :memo:\n"
        jobs = server.get_jobs()
        jobs = [str(i['name']) for i in jobs if 'name' in i]
        for i in range(len(jobs)):
            send_data += "{}: {}\n".format(i + 1, jobs[i])
        return send_data 
    except:
        raise Exception("Error occured in list jobs")


# Error events
@slack_events_adapter.on("error")
def slack_error_handler(err):
    print('error')
    error_handler(err, 'GGF483V5E')

def error_handler(err, channel):
    print("ERROR: " + str(err))
    message = "Sorry!!! Error occured in processing request :no_mouth:.\nKindly check for correct spelling:heavy_check_mark: or contact the DevOps Team.:computer:"
    #message = str(err)
    slack_client.api_call(
    "chat.postMessage",
    channel='{0}'.format(channel),
    attachments=[{"text": "{0}".format(message), "color": "#A30200" }])

slack_events_adapter.start(port=4000)

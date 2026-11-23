import os

import requests

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

API_URL = 'https://ollama.com/api/chat'
MODEL = 'gpt-oss:120b'
HEADERS = {'Authorization': 'Bearer ' + os.environ['OLLAMA_API_KEY']}


def list_files(path):
    return '\n'.join(os.listdir(path))

list_files_tool = {
    'type': 'function',
    'function': {
        'name': 'list_files',
        'description': 'List the files in a directory',
        'parameters': {
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'string',
                    'description': "The directory to list. Use '.' for the current directory."
                }
            },
            'required': ['path']
        }
    }
}


def read_file(path):
    with open(path) as f:
        return f.read()

read_file_tool = {
    'type': 'function',
    'function': {
        'name': 'read_file',
        'description': 'Read the contents of a file.',
        'parameters': {
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'string',
                    'description': 'The path of the file to read.'
                }
            },
            'required': ['path']
        }
    }
}


def edit_file(path, old_str, new_str):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(new_str)
        return 'Created file'
    with open(path) as f:
        content = f.read()
    if content.count(old_str) != 1:
        return f'Error: found {content.count(old_str)} matches, need exactly 1.'
    with open(path, 'w') as f:
        new_content = content.replace(old_str, new_str)
        f.write(new_content)
    return 'OK'

edit_file_tool = {
    'type': 'function',
    'function': {
        'name': 'edit_file',
        'description': 'Replace text in a file. Replaces old_str with new_str. old_str must appear exactly once in the file. If the file at path does not exist, it will be created with new_str as its contents (pass an empty string for old_str).',
        'parameters': {
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'string',
                    'description': 'The path of the file to edit.'
                },
                'old_str': {
                    'type': 'string',
                    'description': 'The exact text to search for.'
                },
                'new_str': {
                    'type': 'string',
                    'description': 'The text to replace it with.'
                }
            },
            'required': ['path', 'old_str', 'new_str']
        }
    }
}

def statute_of_limitations(path, state, case_type, incident_year, incident_month, incident_day, discovery_year, discovery_month, discovery_day, client_age_incident, client_age_today, client_birth_year, client_birth_month, client_birth_day, years_since_incident, years_since_discovery):

    print(incident_year, incident_month, incident_day)
    # reading screening file
    with open(path) as f:
        f.read()

    # What to return if case type is not auto accident or medical malpractice
    if case_type == "inapplicable":
        return f"Inapplicable case type. Cannot evaluate statute of limitations."
    #if auto accident or medical malpractice, evaluate for SoL
    else:
        #decision tree evaluation for how many years until the statute of limitations
        if case_type.lower() == "auto accident":
            if state.upper() == "MD":
                if client_age_incident >= 18:
                    sol_date = date(3 + incident_year,incident_month,incident_day)
                    sol_note = "3 years from the incident"
                else:
                    sol_date = date(client_birth_year + 21, client_birth_month, client_birth_day)
                    sol_note = "the client's 21st birthday"
            if state.upper() == "VA":
                if client_age_incident >= 18:
                    sol_date = date(2 + incident_year,incident_month,incident_day)
                    sol_note = "2 years from the incident"
                else:
                    sol_date = date(client_birth_year + 20,client_birth_month,client_birth_day)
                    sol_note = "the client's 20th birthday"
            if state.upper() == "DE":
                if client_age_incident >= 18:
                    sol_date = date(2 + incident_year, incident_month, incident_day)
                    sol_note = "2 years from the incident"
                else:
                    sol_date = date(21 + client_birth_year,client_birth_month,client_birth_day)
                    sol_note = "the client's 21st birthday"
            if state.upper() == "DC":
                if client_age_incident >= 18:
                    sol_date = date(3 + incident_year, incident_month, incident_day)
                    sol_note = "3 years from the incident"
                else:
                    sol_date = date(21 + client_birth_year,client_birth_month,client_birth_day)
                    sol_note = "the client's 21st birthday"
            if state.upper() == "PA":
                if client_age_incident >= 18:
                    sol_date = date(2 + incident_year, incident_month, incident_day)
                    sol_note = "2 years from the incident"
                else:
                    sol_date = date(20 + client_birth_year,client_birth_month,client_birth_day)
                    sol_note = "the client's 20th birthday"                   

        if case_type.lower() == "medical malpractice":
            if state.upper() == "MD":
                if client_age_incident >= 18: #md adult med mal SoL: less of 5 years from incident or 3 years from discovery
                    five_inc = date(5 + incident_year,incident_month,incident_day)
                    three_disc = date(3 + discovery_year,discovery_month,discovery_day)
                    sol_date = min(five_inc, three_disc)
                    if sol_date == five_inc:
                        sol_note = "5 years from the incident"
                    if sol_date == three_disc:
                        sol_note = "3 years from mistake discovery"
                else:
                    five_inc = date(5 + incident_year,incident_month,incident_day)
                    future_bday = date(client_birth_year + 21,client_birth_month,client_birth_day)
                    sol_date = min(five_inc, future_bday)
                    if sol_date == five_inc:
                        sol_note = "5 years from the incident"
                    if sol_date == future_bday:
                        sol_note = "the client's 21st birthday"
            if state.upper() == "VA":
                if client_age_incident >= 8: # 2 years from act
                    sol_date = date(2 + incident_year,incident_month,incident_day)
                    sol_note = "2 years from the incident"
                else: #10th bday
                    sol_date = date(10 + client_birth_year,client_birth_month,client_birth_day)
                    sol_note = "the client's 10th birthday"
            if state.upper() == "DE":
                if client_age_incident >= 6:
                    if years_since_incident - years_since_discovery > 2: #2 years from injury. If not discovered in that 2 years, 3 years from injury
                        sol_date = date(3 + incident_year,incident_month,incident_day)
                        sol_note = "3 years from the incident"
                    else:
                        sol_date = date(2 + incident_year,incident_month,incident_day)
                        sol_note = "2 years from the incident"
                else:
                    if years_since_incident - years_since_discovery > 2: #later of normal deadline and 6th bday
                        three_inc = date(3 + incident_year,incident_month, incident_day)
                        six_bday = date(client_birth_year + 6,client_birth_month,client_birth_day)
                        sol_date = max(three_inc, six_bday)
                        if sol_date == three_inc:
                            sol_note = "3 years from the incident"
                        if sol_date == six_bday:
                            sol_note = "the client's 6th birthday"
                    else:
                        two_inc = date(2 + incident_year,incident_month,incident_day)
                        six_bday = date(client_birth_year + 6,client_birth_month,client_birth_day)
                        sol_date = max(two_inc, six_bday)
                        if sol_date == two_inc:
                            sol_note = "2 years from the incident"
                        if sol_date == six_bday:
                            sol_note = "the client's 6th birthday"
            if state.upper() == "DC":
                if client_age_incident >= 18:
                    three_inc = date(3 + incident_year,incident_month, incident_day)
                    three_disc = date(3 + discovery_year,discovery_month,discovery_day)
                    sol_date = max(three_inc, three_disc)
                    if sol_date == three_inc:
                        sol_note = "3 years from the incident"
                    if sol_date == three_disc:
                        sol_note = "3 years from discovery of the mistake"
                else:
                    sol_date = date(21 + client_birth_year, client_birth_month,client_birth_day)
                    sol_note = "the client's 21th birthday"
            if state.upper() == "PA":
                if client_age_incident >= 18:
                    sol_date = date(2 + discovery_year,discovery_month,discovery_day)
                    sol_note = "2 years from discovery of the mistake"
                else:
                    sol_date = date(20 + client_birth_year,client_birth_month,client_birth_day)
                    sol_note = "the client's 20th birthday"

        # evaluating whether the statute of limitations is approaching in less than 6 months. 
        # Standing rule is to not accept "paper bag" cases where the SoL is coming up in less than 6 months
        if sol_date - relativedelta(months=6) >= date.today():
            paper_bag = "Can Accept. SoL more than 6 months away."
        elif sol_date - relativedelta(months=6) < date.today() and sol_date > date.today():
            paper_bag = "Reject. SoL less than 6 months away."
        else:
            paper_bag = "Reject. SoL has already run. Case is time barred."

        # appending relevant information to the bottom of the screening file
        incident_date = date(incident_year,incident_month,incident_day)
        discovery_date = date(discovery_year,discovery_month,discovery_day)
        if case_type == "medical malpractice":
            case_note = f"\nNote Date: {date.today()}\n--Case Profile--\nState: {state.upper()}\nCase Type: {case_type.title()}\nAge of Caller on Incident Date: {client_age_incident}\nIncident Date: {incident_date}\nDiscovery Date: {discovery_date}\nStatute of Limitations: {sol_date}, {sol_note}\n{paper_bag}"
        elif case_type == "auto accident":
            case_note = f"\nNote Date: {date.today()}\n--Case Profile--\nState: {state.upper()}\nCase Type: {case_type.title()}\nAge of Caller on Incident Date: {client_age_incident}\nIncident Date: {incident_date}\nStatute of Limitations: {sol_date}, {sol_note}\n{paper_bag}"

        with open(path, "a") as f:
            f.write(case_note)
        
        return f"Statute of Limitations runs on {sol_date}"


statute_of_limitations_tool = {
    'type': 'function',
    'function': {
        'name': 'statute_of_limitations',
        'description': 'use when the user wants to know the statute of limitations for a fact pattern. read a file and extract the parameters from it to feed into the tool',
        'parameters': {
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'string',
                    'description': 'the path of the file the user wants the statute of limitations for'
                },
                'state': {
                    'type': 'string',
                    'description': 'the state where the incident occurred. use its common two letter abbreviation'
                },
                'case_type': {
                    'type': 'string',
                    'description': '"auto accident" or "medical malpractice". If it is not auto accident or medical malpractice, "inapplicable"'
                },
                'incident_year': {
                    'type': 'int',
                    'description': 'the year the incident took place as a number'
                },
                'incident_month': {
                    'type': 'int',
                    'description': 'the month the incident took placem as a number'
                },
                'incident_day': {
                    'type': 'int',
                    'description': 'the day the incident took place as a number'
                },
                'discovery_year': {
                    'type': 'int',
                    'description': 'the year the incident was discovered as a number'
                },
                'discovery_month': {
                    'type': 'int',
                    'description': 'the month the incident was discovered as a number'
                },
                'discovery_day': {
                    'type': 'int',
                    'description': 'the day the incident was discovered as a number'
                },
                'client_birth_year': {
                    'type': 'int',
                    'description': 'the year the client was born as a number'
                },
                'client_birth_month': {
                    'type': 'int',
                    'description': 'the month the client was born as a number'
                },
                'client_birth_day': {
                    'type': 'int',
                    'description': 'the day the incident was discovered as a number'
                },
                'client_age_incident': {
                    'type': 'float',
                    'description': 'age of the client at the time of the incident, with decimals for months and days if applicable. incident date minus DOB or the mentioned age in the file minus the time between today and the incident date'
                },
                'client_age_today': {
                    'type': 'float',
                    'description': 'age of the client today, with decimals for months and days if applicable. Date today minus DOB or the mentioned age in the file'
                },
                'years_since_incident': {
                    'type': 'float',
                    'description': 'the time in years since the incident, with decimals for months and days. If it is the same day as the incident, discovery date is the incident date. date today minus discovery date'
                },
                'years_since_discovery': {
                    'type': 'float',
                    'description': 'the time in years since discovery of the incident, with decimals for months and days. If it is the same day as the incident, discovery date is the incident date. date today minus discovery date'
                }
            },
            'required': ["path", "state", "case_type", "incident_year", "incident_month", "incident_day", "discovery_year", "discovery_month", "discovery_day", "client_age_incident", "client_age_today", "client_birth_year", "client_birth_month", "client_birth_day", "years_since_incident", "years_since_discovery"]
        }
    }
}


def case_evaluation(path,state,case_type,incident_date,sol,fault_evaluation,case_value,accept_reject,case_score,case_grade, summary):
    case_note = f"\nState: {state}\nCase Type: {case_type.title()}\nIncident Date: {incident_date}\nSoL: {sol}\nFault Evaluation: {fault_evaluation}\nPotential Case Value: {case_value}\nCase Grade: {case_grade} ({case_score})\nAccept or Reject?: {accept_reject}\n{summary}"
    
    with open(path, "a") as f:
        f.write(case_note)
    return case_note


case_evaluation_tool = {
    'type': 'function',
    'function': {
        'name': 'case_evaluation',
        'description': 'use this tool when the user wants you to evaluate a case based on a set of facts in a file',
        'parameters': {
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'string',
                    'description': 'The path of the file that has the facts.'
                },
                'state': {
                    'type': 'string',
                    'description': 'The state the incident occurred in'
                },
                'case_type': {
                    'type': 'string',
                    'description': 'The type of case it is. For example, it could be auto accident, medical malpractice, or others'
                },
                'incident_date': {
                    'type': 'string',
                    'description': 'The date of the incident. MM/DD/YYYY format'
                },
                'sol': {
                    'type': 'string',
                    'description': 'The date the statute of limitations runs out for the case with the applicable rule'
                },
                'fault_evaluation': {
                    'type': 'string',
                    'description': 'state the key facts and reasoning that led to agent evaluation of fault'
                },
                'case_value': {
                    'type': 'string',
                    'description': 'Based on other similar cases, an estimation of how much money the case is worth'
                },
                'accept_reject': {
                    'type': 'string',
                    'description': 'a binary "Accept" or "Reject" based on judgment of the agent'
                },
                'case_score': {
                    'type': 'string',
                    'description': 'grade the case on a scale of 0-100'
                },
                'case_grade': {
                    'type': 'string',
                    'description': 'Give the case a corresponding letter grade based on case score'
                },
                'summary': {
                    'type': 'string',
                    'description': 'summarize the case'
                },
            },
            'required': ["path","state","case_type","incident_date","sol","fault_evaluation","case_value","accept_reject","case_score","case_grade","summary"]
        }
    }
}

tool_functions = {'list_files': list_files, 'read_file': read_file, 'edit_file': edit_file, 'statute_of_limitations': statute_of_limitations, "case_evaluation": case_evaluation}
tool_schemas = [list_files_tool, read_file_tool, edit_file_tool, statute_of_limitations_tool, case_evaluation_tool]


def call_model(messages, tools):
    payload = {'model': MODEL, 'messages': messages, 'tools': tools, 'stream': False}
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=300)
    return response.json()


def run_tool(call):
    name = call['function']['name']
    args = call['function']['arguments']
    shown = str(args)
    if len(shown) > 80:
        shown = shown[:80] + '...'
    print(f"[tool] {name}({shown})")

    result = tool_functions[name](**args)
    return {
        'role': 'tool',
        'tool_name': name,
        'content': str(result)
    }


def agent(messages):
    while True:
        data = call_model(messages, tool_schemas)
        message = data['message']
        messages.append(message)

        tool_calls = message.get('tool_calls')
        if not tool_calls:
            return message['content']

        for call in tool_calls:
            messages.append(run_tool(call))


def main():
    messages = [
        {
            "role": "system",
            "content": "You are a helpful general purpose AI assistant. Keep responses brief, avoid markdown unless instructed."
        }
    ]

    while True:
        user_content = input("You: ")
        messages.append({'role': 'user', 'content': user_content})
        print(f"Agent: {agent(messages)}\n")


if __name__ == '__main__':
    main()
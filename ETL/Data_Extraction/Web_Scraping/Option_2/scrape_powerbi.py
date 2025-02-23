####################
# Author : Kulwinder K.
# Date : 12/12/2023
# This script scrapes the Power BI dashboard from the below website 
# https://www.un.org/techenvoy/global-digital-compact
# and gives back the CSV file
# It calls json_to_csv.py file inside the script.
#####################

# Read readme for Power BI scarping.txt file for description.

import requests
import pandas as pd
import time
import os
import json
import csv
import subprocess

def find_key_recursively(obj, key):
    '''
    Input Parameters - Takes in nested Json obj (example json reteied from request).
                     - key which we want to find (example "DM0" in our case).
    Returns - Key value pair from deeply nested json.
    
    '''
    if isinstance(obj, dict):
        if key in obj:
            yield obj[key]

        for v in obj.values():
            yield from find_key_recursively(v, key)
    elif isinstance(obj, list):
        for v in obj:
            yield from find_key_recursively(v, key)


def page_1_scraping(api_url, payload, headers):
    
    table_data= requests.post(api_url, json=payload, headers=headers).json()
    
    #write the json to a file
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(table_data, f, ensure_ascii=False, indent=4)

    #run the script to read the json and convert to csv file
    script_path = 'json_to_csv.py'
    arguments = ['data.json', 'output_file.csv']

    command = ['python', script_path] + arguments

    # Call the script
    subprocess.call(command)
    return f'Table scarped to output_file.csv'


def update_payload_query_w_ids(api_url, query_payload, headers, topic, record_id):
    '''
    Input Parameters - topic (String topic selected from the corresponding GDC area on the second page)
                     - record_id (List of record Ids from DataFrame that we want to match)
                     - query_payload to retrieve the Core Principles, Preparation and Commitment, Pledges and Action area
                     - API URL
                     - Headers

    Retuns - List of values retreieved fron the Power BI query for topic and selected record id pair.
    
    '''
    data=[]
    query_payload['queries'][0]['Query']['Commands'][0]['SemanticQueryDataShapeCommand']['Query']['Where'][0]['Condition']['In']['Values'][0][0]['Literal']['Value']=f"'{topic}'"
    for j in record_id:
        query_payload['queries'][0]['Query']['Commands'][0]['SemanticQueryDataShapeCommand']['Query']['Where'][1]['Condition']['In']['Values'][0][0]['Literal']['Value']=f"'{j}'"    
        data.append(requests.post(api_url, json=query_payload, headers=headers).json())
        time.sleep(1)
        
    value=[]
    for d in data:
        x = next(find_key_recursively(d, "DM0"))
        value.append([x[0].get("G0", {})])
        
    return value

def page_2_core_principles(api_url, payload_core_principles, headers, df):
    
    '''
    Input Parameters - query_payload to retrieve the Core Principles
                     - dataframe df
                     - API URL
                     - Headers

    Retuns - df with addition of new columns scarped
    '''
    #Topic names are manually added from the Page 2 of Power BI
    #It would be better if this is also automated to make it more agile.
    topics=['Accountability for Discrimination/Misleading Content', 'Connect all People', 'Digital Commons', 'Human Rights Online',
       'Internet Fragmentation', 'Other Area', 'Protect Data', 'Regulation of AI']
    record_id = df['Record ID'].tolist()
    for topic in topics:
        df[topic+"_"+'Core_principles']=update_payload_query_w_ids(api_url, payload_core_principles, headers, topic, record_id)


    return df, f'Values Scraped for Core Principles section and added to dataframe'


def page_2_commitment(api_url, payload_commitment, headers, df):

    '''
    Input Parameters - query_payload to retrieve the Commitment, Pledges and Action area
                     - dataframe df
                     - API URL
                     - Headers

    Retuns - df with addition of new columns scarped
    '''

    topics=['Accountability for Discrimination/Misleading Content', 'Connect all People', 'Digital Commons', 'Human Rights Online',
       'Internet Fragmentation', 'Other Area', 'Protect Data', 'Regulation of AI']
    record_id = df['Record ID'].tolist()
    for topic in topics:
        df[topic+"_"+'Commitments']=update_payload_query_w_ids(api_url, payload_commitment, headers, topic, record_id)
    
    return df, f'Values Scraped for Commitment section and added to dataframe'

    
def page_2_process_indi(api_url, payload_process_indi, headers, df):
    
    '''
    Input Parameters - query_payload to retrieve the indiviual process description of each entry in table
                     - dataframe df
                     - API URL
                     - Headers

    Retuns - df with addition of new columns scarped
    '''
    
    topic='Protect Data' 
   
    query_not_working=[]
    dm0_empty=[]
    value_indi=[]
    for index, row in df.iterrows():
        payload_process_indi['queries'][0]['Query']['Commands'][0]['SemanticQueryDataShapeCommand']['Query']['Where'][1]['Condition']['In']['Values'][0][0]['Literal']['Value']=f"'{row['Record ID']}'"
        payload_process_indi['queries'][0]['Query']['Commands'][0]['SemanticQueryDataShapeCommand']['Query']['Where'][3]['Condition']['In']['Values'][0][0]['Literal']['Value']=f"'{row['Type']}'"
        payload_process_indi['queries'][0]['Query']['Commands'][0]['SemanticQueryDataShapeCommand']['Query']['Where'][4]['Condition']['In']['Values'][0][0]['Literal']['Value']=f"'{row['Location formatted']}'"
        payload_process_indi['queries'][0]['Query']['Commands'][0]['SemanticQueryDataShapeCommand']['Query']['Where'][5]['Condition']['In']['Values'][0][0]['Literal']['Value']=f"'{row['Contact Name']}'"
        payload_process_indi['queries'][0]['Query']['Commands'][0]['SemanticQueryDataShapeCommand']['Query']['Where'][6]['Condition']['In']['Values'][0][0]['Literal']['Value']=f"'{row['Entity Name']}'"
        data_process=(requests.post(api_url, json=payload_process_indi, headers=headers).json())
    
        try:
            x = next(find_key_recursively(data_process, "DM0"))
            if x:
                value_indi.append([x[0].get("G0", {})])

            else:
                # Handle the case when x is empty (list index is out of range)
                x = None  
                value_indi.append(x)
                dm0_empty.append(index)
        except StopIteration:
            # Handle the end of iteration, for example, when query doesn't work
            query_not_working.append(index)
            x = None  
            value_indi.append(x)
        time.sleep(1)

    df["Process Description"]=value_indi
    
    return df, f'\nQuery didnot run for these indexes {query_not_working} and retrieved nothing for these indexes {dm0_empty}. \n Values Scraped for each process description and added to dataframe'

def page_2_process_consultation(api_url, payload_process_consultation, headers):
    data_consultation=requests.post(api_url, json=payload_process_consultation, headers=headers).json()
    process_list=[d.get("G0", {}) for d in data_consultation["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]]
    
    #write to a csv file
    csv_file_path = 'Process_consultation.csv'

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
    
        # Write each row separately
        for paragraph in process_list:
            writer.writerow([paragraph])
    return f'\n Data saved in Process_consulatation file'



if __name__ == "__main__":

    #API and Payload Instatiation
    #It can be collected from the Network/XHR component while inspecting the webpage.

    #api url copied form the Headers section of Network>XHR
    api_url= 'https://wabi-north-europe-j-primary-api.analysis.windows.net/public/reports/querydata?synchronous=true'
    headers= {'user_agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Powerbi-Resourcekey': '84db278f-178b-4a18-a0db-3e57e8113b1f'}

    #payload for tables and second page sections
    payload_table= {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"d","Entity":"Demographics","Type":0},{"Name":"a","Entity":"All Areas combined","Type":0}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Type"},"Name":"Demographics.Type"},{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Location formatted"},"Name":"Demographics.Location formatted"},{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Contact Name"},"Name":"Demographics.Contact Name"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Core Principles"}},"Function":2},"Name":"All Areas combined.Core Principles"},{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Entity Name"},"Name":"Demographics.Entity Name"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Commitments, pledges or actions"}},"Function":2},"Name":"All Areas combined.Commitments, pledges or actions"},{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Record ID"},"Name":"All Areas combined.Record ID","NativeReferenceName":"Record ID1"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Area"}}],"Values":[[{"Literal":{"Value":"'Connect all People'"}}],[{"Literal":{"Value":"'Accountability for Discrimination/Misleading Content'"}}],[{"Literal":{"Value":"'Digital Commons'"}}],[{"Literal":{"Value":"'Regulation of AI'"}}],[{"Literal":{"Value":"'Protect Data'"}}],[{"Literal":{"Value":"'Internet Fragmentation'"}}],[{"Literal":{"Value":"'Human Rights Online'"}}],[{"Literal":{"Value":"'Other Area'"}}]]}}}],"OrderBy":[{"Direction":2,"Expression":{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Core Principles"}},"Function":2}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1,2,3,4,5,6]}]},"DataReduction":{"DataVolume":3,"Primary":{"Window":{"Count":500}}},"Version":1},"ExecutionMetricsKind":1}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"d\",\"Entity\":\"Demographics\",\"Type\":0},{\"Name\":\"a\",\"Entity\":\"All Areas combined\",\"Type\":0}],\"Select\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"Type\"},\"Name\":\"Demographics.Type\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"Location formatted\"},\"Name\":\"Demographics.Location formatted\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"Contact Name\"},\"Name\":\"Demographics.Contact Name\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"a\"}},\"Property\":\"Core Principles\"}},\"Function\":2},\"Name\":\"All Areas combined.Core Principles\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"Entity Name\"},\"Name\":\"Demographics.Entity Name\"},{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"a\"}},\"Property\":\"Commitments, pledges or actions\"}},\"Function\":2},\"Name\":\"All Areas combined.Commitments, pledges or actions\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"a\"}},\"Property\":\"Record ID\"},\"Name\":\"All Areas combined.Record ID\",\"NativeReferenceName\":\"Record ID1\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"a\"}},\"Property\":\"Area\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Connect all People'\"}}],[{\"Literal\":{\"Value\":\"'Accountability for Discrimination/Misleading Content'\"}}],[{\"Literal\":{\"Value\":\"'Digital Commons'\"}}],[{\"Literal\":{\"Value\":\"'Regulation of AI'\"}}],[{\"Literal\":{\"Value\":\"'Protect Data'\"}}],[{\"Literal\":{\"Value\":\"'Internet Fragmentation'\"}}],[{\"Literal\":{\"Value\":\"'Human Rights Online'\"}}],[{\"Literal\":{\"Value\":\"'Other Area'\"}}]]}}}],\"OrderBy\":[{\"Direction\":2,\"Expression\":{\"Aggregation\":{\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"a\"}},\"Property\":\"Core Principles\"}},\"Function\":2}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0,1,2,3,4,5,6]}]},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Window\":{\"Count\":500}}},\"Version\":1},\"ExecutionMetricsKind\":1}}]}","QueryId":"","ApplicationContext":{"DatasetId":"fb1276c8-e98e-4b26-a7d3-24a40ae84000","Sources":[{"ReportId":"a70c1024-15f3-4f74-aa2e-2f1897acfdb6","VisualId":"fc23d492ddbe07d7e1a4"}]}}],"cancelQueries":[],"modelId":933989}
    payload_core_principles={"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"a","Entity":"All Areas combined","Type":0}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Core Principles"},"Name":"All Areas combined.Core Principles"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Area"}}],"Values":[[{"Literal":{"Value":"'Protect Data'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Record ID"}}],"Values":[[{"Literal":{"Value":"'38157322109780680'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":3,"Primary":{"Top":{}}},"Version":1},"ExecutionMetricsKind":1}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"a\",\"Entity\":\"All Areas combined\",\"Type\":0}],\"Select\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"a\"}},\"Property\":\"Core Principles\"},\"Name\":\"All Areas combined.Core Principles\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"a\"}},\"Property\":\"Area\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Protect Data'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"a\"}},\"Property\":\"Record ID\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'38157322109780680'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0]}]},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Top\":{}}},\"Version\":1},\"ExecutionMetricsKind\":1}}]}","QueryId":"","ApplicationContext":{"DatasetId":"fb1276c8-e98e-4b26-a7d3-24a40ae84000","Sources":[{"ReportId":"a70c1024-15f3-4f74-aa2e-2f1897acfdb6","VisualId":"58d5b49030dc6e9c802b"}]}}],"cancelQueries":[],"modelId":933989}
    payload_commitment={"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"a","Entity":"All Areas combined","Type":0}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Commitments, pledges or actions"},"Name":"All Areas combined.Commitments, pledges or actions"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Area"}}],"Values":[[{"Literal":{"Value":"'Protect Data'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Record ID"}}],"Values":[[{"Literal":{"Value":"'38157322109780680'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":3,"Primary":{"Top":{}}},"Version":1},"ExecutionMetricsKind":1}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"a\",\"Entity\":\"All Areas combined\",\"Type\":0}],\"Select\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"a\"}},\"Property\":\"Commitments, pledges or actions\"},\"Name\":\"All Areas combined.Commitments, pledges or actions\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"a\"}},\"Property\":\"Area\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Protect Data'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"a\"}},\"Property\":\"Record ID\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'38157322109780680'\"}}]]}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0]}]},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Top\":{}}},\"Version\":1},\"ExecutionMetricsKind\":1}}]}","QueryId":"","ApplicationContext":{"DatasetId":"fb1276c8-e98e-4b26-a7d3-24a40ae84000","Sources":[{"ReportId":"a70c1024-15f3-4f74-aa2e-2f1897acfdb6","VisualId":"88e7332007b6856d20da"}]}}],"cancelQueries":[],"modelId":933989}
    #overall process description that appears on opening page 2
    payload_process_consultation={"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"d","Entity":"Demographics","Type":0},{"Name":"a","Entity":"All Areas combined","Type":0}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Process description"},"Name":"Demographics.Process description"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Area"}}],"Values":[[{"Literal":{"Value":"'Protect Data'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Record ID"}}],"Values":[[{"Literal":{"Value":"'38157322109780680'"}}]]}}}],"OrderBy":[{"Direction":2,"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Process description"}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0],"Subtotal":1}]},"DataReduction":{"DataVolume":3,"Primary":{"Window":{"Count":500}}},"Version":1},"ExecutionMetricsKind":1}}]},"CacheKey":"{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"d\",\"Entity\":\"Demographics\",\"Type\":0},{\"Name\":\"a\",\"Entity\":\"All Areas combined\",\"Type\":0}],\"Select\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"Process description\"},\"Name\":\"Demographics.Process description\"}],\"Where\":[{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"a\"}},\"Property\":\"Area\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'Protect Data'\"}}]]}}},{\"Condition\":{\"In\":{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"a\"}},\"Property\":\"Record ID\"}}],\"Values\":[[{\"Literal\":{\"Value\":\"'38157322109780680'\"}}]]}}}],\"OrderBy\":[{\"Direction\":2,\"Expression\":{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"d\"}},\"Property\":\"Process description\"}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[0],\"Subtotal\":1}]},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Window\":{\"Count\":500}}},\"Version\":1},\"ExecutionMetricsKind\":1}}]}","QueryId":"","ApplicationContext":{"DatasetId":"fb1276c8-e98e-4b26-a7d3-24a40ae84000","Sources":[{"ReportId":"a70c1024-15f3-4f74-aa2e-2f1897acfdb6","VisualId":"639afabe81a1c903da6c"}]}}],"cancelQueries":[],"modelId":933989}
    #process description when selecting and filtering from page 1
    payload_process_indi={"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"d","Entity":"Demographics","Type":0},{"Name":"a","Entity":"All Areas combined","Type":0}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Process description"},"Name":"Demographics.Process description"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Area"}}],"Values":[[{"Literal":{"Value":"'Protect Data'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Record ID"}}],"Values":[[{"Literal":{"Value":"'638159590404564717'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"a"}},"Property":"Area"}}],"Values":[[{"Literal":{"Value":"'Connect all People'"}}],[{"Literal":{"Value":"'Accountability for Discrimination/Misleading Content'"}}],[{"Literal":{"Value":"'Digital Commons'"}}],[{"Literal":{"Value":"'Regulation of AI'"}}],[{"Literal":{"Value":"'Protect Data'"}}],[{"Literal":{"Value":"'Internet Fragmentation'"}}],[{"Literal":{"Value":"'Human Rights Online'"}}],[{"Literal":{"Value":"'Other Area'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Type"}}],"Values":[[{"Literal":{"Value":"'Academia/research institution/think tank'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Location formatted"}}],"Values":[[{"Literal":{"Value":"'Global'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Contact Name"}}],"Values":[[{"Literal":{"Value":"'Ananya Balasubramanian'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Entity Name"}}],"Values":[[{"Literal":{"Value":"'New York University School of Professional Studies'"}}]]}}}],"OrderBy":[{"Direction":2,"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Process description"}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0],"Subtotal":1}]},"DataReduction":{"DataVolume":3,"Primary":{"Window":{"Count":500}}},"Version":1},"ExecutionMetricsKind":1}}]},"QueryId":"","ApplicationContext":{"DatasetId":"fb1276c8-e98e-4b26-a7d3-24a40ae84000","Sources":[{"ReportId":"a70c1024-15f3-4f74-aa2e-2f1897acfdb6","VisualId":"639afabe81a1c903da6c"}]}}],"cancelQueries":[],"modelId":933989}

    print(page_1_scraping(api_url, payload_table, headers))
    df=pd.read_csv('output_file.csv')

    df, step_completed =page_2_core_principles(api_url, payload_core_principles, headers, df)
    print(step_completed)
    df, step_completed=page_2_commitment(api_url, payload_commitment, headers, df)
    print(step_completed)
    df, step_completed=page_2_process_indi(api_url, payload_process_indi, headers, df)
    print(step_completed)

    df.to_csv('powerbi_csv.csv', encoding='utf-8', index=False)

    step_completed=page_2_process_consultation(api_url, payload_process_consultation, headers)
    print(step_completed)


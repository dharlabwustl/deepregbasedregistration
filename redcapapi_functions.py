#!/usr/bin/env python
import requests,json
import pandas as pd
# from config import config
import requests, hashlib, json,glob
import os,sys,subprocess,time,inspect
import numbers,decimal
# api_url = os.environ['REDCAP_HOST']#
api_token =os.environ['REDCAP_API'] #
sys.path.append("/software")
# from fillmaster_session_list import *
# from download_with_session_ID import *
# from system_analysis import *
# api_token='EC6A2206FF8C1D87D4035E61C99290FF' #sys.argv[1] #os.environ['REDCAP_API_TOKEN']
api_url='https://redcap.wustl.edu/redcap/api/' #sys.argv[2] #
# project_ID=sys.argv[1]
# session_id=sys.argv[2]
working_dir="/workinginput"
output_directory="/workingoutput"
final_output_directory="/outputinsidedocker"


def download_latest_redcapfile(api_token,this_project_redcapfile):

    df_scan=''
    try:
        fields = {
            'token':api_token, # api_token,
            'content': 'record',
            'format': 'json',
            'type': 'flat'
        }
        r = requests.post('https://redcap.wustl.edu/redcap/api/',data=fields)
        r_json=json.dumps(r.json()) #get_niftifiles_metadata(each_axial['URI'] )) get_resourcefiles_metadata(URI,resource_dir)
        df_scan = pd.read_json(r_json)
        df_scan.to_csv(this_project_redcapfile,index=False)
    except:
        pass
    return df_scan
def sorted_subj_list(subject_df,subject_col_name,datetime_col_name):
    datetime_col_name_1=datetime_col_name+"_1"
    # df=pd.read_csv(csvfilename)
    subject_df[datetime_col_name_1] = pd.to_datetime(subject_df[datetime_col_name], format='%m/%d/%Y %H:%M')
    df_agg = subject_df.groupby([subject_col_name])
    res_df = df_agg.apply(lambda x: x.sort_values(by=[datetime_col_name_1],ascending=True))
    x=res_df.pop(datetime_col_name_1)
    return res_df
def add_one_data_to_redcap(this_record_id,this_redcap_repeat_instrument,this_redcap_repeat_instance,this_field,this_data):
    try:
        if  isinstance(this_data, (int, float, complex)):
            this_data=round(this_data,2)

        # api_token='EC6A2206FF8C1D87D4035E61C99290FF'
        subprocess.call("echo " + "I PASSED AT session_label::{}::{}::{}::{}::{}  >> /workingoutput/error.txt".format(this_record_id,this_redcap_repeat_instrument,this_redcap_repeat_instance,this_field,this_data) ,shell=True )
        record = {
            'redcap_repeat_instrument':this_redcap_repeat_instrument,
            'redcap_repeat_instance':this_redcap_repeat_instance,
            'record_id':this_record_id,
            this_field:str(this_data) #this_snipr_session
        }
        print(record)
        data = json.dumps([record])
        fields = {
            'token': api_token,
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'data': data,
        }
        r = requests.post(api_url,data=fields)
        print('HTTP Status: ' + str(r.status_code))
        print(r.text)
        subprocess.call("echo " + "I PASSED AT status_code::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
    except:
        subprocess.call("echo " + "I FAILED AT status_code::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )

        pass
    return


def add_one_file_to_redcap(this_record_id,this_redcap_repeat_instrument,this_redcap_repeat_instance,this_field,this_data_file):
    try:
        # api_token='EC6A2206FF8C1D87D4035E61C99290FF'
        subprocess.call("echo " + "I PASSED AT session_label::{}::{}::{}::{}::{}  >> /workingoutput/error.txt".format(this_record_id,this_redcap_repeat_instrument,this_redcap_repeat_instance,this_field,this_data_file) ,shell=True )
        fields = {
            'token': api_token,
            'content': 'file',
            'action': 'import',
            'repeat_instrument':this_redcap_repeat_instrument, #str(df_scan_sample.loc[0,'redcap_repeat_instrument']),
            'repeat_instance':this_redcap_repeat_instance, #str(df_scan_sample.loc[0,'redcap_repeat_instance']),
            'record': this_record_id, #str(df_scan_sample.loc[0,'record_id']),
            'field': this_field, #'session_pdf' , #'photo_as_pdf',
            'returnFormat': 'json'
        }
        file_path=this_data_file #file
        file_obj = open(file_path, 'rb')
        r = requests.post(api_url,data=fields,files={'file':file_obj})
        file_obj.close()
        print('HTTP Status: ' + str(r.status_code))
        print(r.text)
        subprocess.call("echo " + "I PASSED AT status_code::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        if r !=200:
            subprocess.call("echo " + "I could not write AT this_record_id::{}::{}  >> /workingoutput/error.txt".format(this_record_id,this_field) ,shell=True )


    except:
        subprocess.call("echo " + "I FAILED AT status_code::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )

        pass
    return

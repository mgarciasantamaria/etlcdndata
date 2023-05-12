#!/usr/bin/env python
#_*_ codig: utf8 _*_
import datetime, json, boto3, smtplib, datetime, sys, traceback
from email.message import EmailMessage
from boto3.s3.transfer import S3Transfer, TransferConfig
from Modules.constants import *

def SendMail(text, mail_subject):
    msg = EmailMessage()
    msg.set_content(text)
    msg['Subject'] = mail_subject
    msg['From'] = 'alarmas-aws@vcmedios.com.co'
    msg['To'] = Mail_To
    conexion = smtplib.SMTP(host='10.10.130.217', port=25)
    conexion.ehlo()
    conexion.send_message(msg)
    conexion.quit()
    return

def Download_Logs(DATE_LOG):
    try:
        objects={'Objects':[]}
        list_objects=[]
        aws_session=boto3.Session(profile_name=aws_profile)
        s3_client=aws_session.client('s3')
        logs=s3_client.list_objects_v2(Bucket=Bucket_logs)
        if 'Contents' in logs:    
            for i in range(len(logs['Contents'])):
                log_Key=logs['Contents'][i]['Key']
                S3Transfer(s3_client, TransferConfig(max_bandwidth=5000000)).download_file(Bucket_logs,log_Key,f'{Downloads_Path}/{log_Key}')
                objects['Objects'].append({'Key': log_Key,})
                list_objects.append(f"{Downloads_Path}/{log_Key}")
                s3_client.copy_object(
                    Bucket=Bucket_logs_old,
                    CopySource=f'{Bucket_logs}/{log_Key}',
                    Key=f'{log_Key}'
                    )
                
            s3_client.delete_objects(
                    Bucket=Bucket_logs,
                    Delete=objects
                )
            return list_objects
        else:
            text_print=f"Logs not found"
            print_log("a",text_print,DATE_LOG)
            return []
    except:
        error=sys.exc_info()[2] #Captura del error generado por el sistema.
        errorinfo=traceback.format_tb(error)[0] #Cartura del detalle del error.
        return {
            'Error': str(sys.exc_info()[1]),
            'error_info': errorinfo
        }

def print_log(OPTION, TEXT, DATE_LOG):
    log_file=open(f"{log_Path}/{DATE_LOG}_log.txt", OPTION)
    log_file.write(f"{str(datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'))}\t{TEXT}\n")
    log_file.close()

def Flag_Status(OPTION):
    with open(json_path, "r") as json_file:
            json_data=json.load(json_file)
    if OPTION=="r":
        return json_data["FLAG"]
    elif OPTION=="w":
        json_data["FLAG"]=False
        with open(json_path, "w") as json_file:
            json.dump(json_data, json_file)
    else:
        pass
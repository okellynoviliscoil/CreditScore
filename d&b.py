from datetime import datetime
from flask import make_response
from flask import render_template
from flask import request
import os.path
import base64
import json
import pickle
import requests
import uuid


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


def cwa():
    template = 'CWA.html'
    transaction = {}
    req = get_basic_req(23)
    # req = get_basic_req(24)
    for var in request.args:
        if var == 'Template':
            if os.path.isfile('templates/' + request.args.get('Template')):
                template = request.args.get('Template')
        elif var == 'ts':
            transaction['browser_ts'] = request.args.get('ts')
        else:
            req[var] = request.args.get(var)

    mataf_ref = req['ClientRef']
    transaction['request'] = req
    transaction['sent'] = get_timestamp()
    _r = requests.post('https://Ws.dundb.co.il/CBServiceRest.svc/GetDBCreditWorthinessAssessment', json=req)
    transaction['replied'] = get_timestamp()
    try:
        d = json.loads(_r.text)
        transaction['response'] = d
    except json.decoder.JSONDecodeError:
        transaction['responseText'] = _r.text

    outfile = open(mataf_ref, 'wb')
    pickle.dump(transaction, outfile)
    outfile.close()
    try:
        if d['Result']['ResultCode'] == "00-00":
            return render_template(template, res=d['DBCreditWorthinessAssessment'], codes=get_codes(), titles=get_titles())
        else:
            return render_template("error.html", res=d['Result'])
    except UnboundLocalError:
        return render_template("transaction.html", transaction=transaction)


def nae():
    template = 'NAE.html'
    transaction = {}
    req = get_basic_req(13)
    # req = get_basic_req(14)
    for var in request.args:
        if var == 'Template':
            if os.path.isfile('templates/' + request.args.get('Template')):
                template = request.args.get('Template')
        elif var == 'ts':
            transaction['browser_ts'] = request.args.get('ts')
        else:
            req[var] = request.args.get(var)

    req['CreditProviderApplicationCode'] = ''

    mataf_ref = req['ClientRef']
    transaction['request'] = req
    transaction['sent'] = get_timestamp()
    _r = requests.post('https://Ws.dundb.co.il/CBServiceRest.svc/GetDBNewApplicationEnquiry', json=req)
    transaction['replied'] = get_timestamp()
    try:
        d = json.loads(_r.text)
        transaction['response'] = d
    except json.decoder.JSONDecodeError:
        transaction['responseText'] = _r.text

    outfile = open(mataf_ref, 'wb')
    pickle.dump(transaction, outfile)
    outfile.close()
    try:
        if d['Result']['ResultCode'] == "00-00":
            return render_template(template, res=d['DBNewApplicationEnquiry'], codes=get_codes(), titles=get_titles())
        else:
            return render_template("error.html", res=d['Result'])
    except UnboundLocalError:
        return render_template("transaction.html", transaction=transaction)

def get_file_by_ref():
    ref = request.args.get('ref')
    index = request.args.get('index', default=0, type=int)
    disposition = request.args.get('disposition', default='attachment', type=str)
    infile = open(ref, 'rb')
    transaction = pickle.load(infile)
    infile.close()
    if transaction['response'].get('DBCreditWorthinessAssessment'):
        file = transaction['response']['DBCreditWorthinessAssessment']['ReportOutputs']['ReportOutput'][index]
    else:
        file = transaction['response']['DBNewApplicationEnquiry']['ReportOutputs']['ReportOutput'][index]
    binary_pdf = base64.b64decode(
        file['Value'])
    response = make_response(binary_pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        disposition + '; filename=%s.pdf' % \
        file['Name']
    return response


def show_by_ref():
    template = ""
    if os.path.isfile('templates/' + request.args.get('template', default='x', type=str)):
        template = request.args.get('template')
    ref = request.args.get('ref')
    infile = open(ref, 'rb')
    transaction = pickle.load(infile)
    infile.close()
    if transaction['response']['Result']['ResultCode'] == "00-00":
        if transaction['response'].get('DBCreditWorthinessAssessment'):
            res = transaction['response']['DBCreditWorthinessAssessment']
            if template == "":
                template = "CWA.html"
        else:
            res = transaction['response']['DBNewApplicationEnquiry']
            if template == "":
                template = "NAE.html"
        return render_template(template, res=res, codes=get_codes(), titles=get_titles())
    else:
        return render_template("error.html", res=transaction['response']['Result'])

def show_transaction_by_ref():
    ref = request.args.get('ref')
    infile = open(ref, 'rb')
    transaction = pickle.load(infile)
    infile.close()
    return render_template("transaction.html", transaction=transaction)


def get_timestamps_by_ref():
    ref = request.args.get('ref')
    infile = open(ref, 'rb')
    transaction = pickle.load(infile)
    infile.close()

    return {'sent': transaction['sent'], 'replied': transaction['replied']}


def get_codes():
    with open('codes.json', 'rb') as json_file:
        data = json.load(json_file, encoding="utf8")
        return data


def get_titles():
    with open('titles.json', 'rb') as json_file:
        data = json.load(json_file, encoding="utf8")
        return data


def get_basic_req(ProductCode):
    req = {'ProductCode': ProductCode}

    req['ClientComment'] = ''
    req['ClientRef'] = str(uuid.uuid1())
    req['Password'] = 'bnkbb123'
    req['UserName'] = 'BankBB'
    return req

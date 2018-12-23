#!/usr/local/bin/python
from voipms import VoipMs
import pprint
from pathlib2 import Path
from dotenv import load_dotenv
import logging
import datetime, os, sys, argparse, csv, copy, math

## Report Connections
## configuration values set in a .cdrpyeport file in the running directory
class configCdrReport():
    def __init__(self, env_path):
        # explicitly providing path to '.env'
        env_path ='./.cdrpyreport'
        load_dotenv(dotenv_path=env_path)
        logging.info('loaded settings file..')

# Handles retreival of cdr reports (by reseller id) through VoipMS API
class cdrModuleVoipms():
    def __init__(self, username, apipassword):
        if username is None:
            sys.exit('No Username and/or API password in .cdrpyreport file')
        self.username = username
        self.apipassword = apipassword
        self.ConnectionCDR = VoipMs(self.username, self.apipassword)

    def voipms_getResellers(self):
        accounts = self.ConnectionCDR.clients.get.clients()
        return accounts

    def voipms_reseller(self,resellerID):
        self.resller = self.ConnectionCDR.clients.get.clients(resellerID)

    # retrieves CDR record from reseller id for period given, returns list
    def voipms_rescdr_period(self, dateStart, dateEnd, resellerID):
        CDRS = self.ConnectionCDR.calls.get.reseller_cdr(dateStart, dateEnd, resellerID, -5, answered=True, noanswer=False, busy=False, failed=False)
        return CDRS['cdr']

# A lot of the things happening below should be added to a class, but time.
if __name__ == '__main__':
    #set the current date
    report_date = datetime.datetime.now().strftime("%Y-%m-%d")

    pp = pprint.PrettyPrinter(indent=1, width=80)
    parser = argparse.ArgumentParser(
        description='create a cdr csv for period with markup for accounts under a reseller id')
    parser.add_argument(
        'id', metavar='reseller_id', type=int,
        help='reseller id required for report')
    parser.add_argument(
        'start', metavar='YYYY-MM-DD',
        help='period start in format YYYY-MM-DD')
    parser.add_argument(
    'end', metavar='YYYY-MM-DD',
    help='period end in format YYYY-MM-DD')
    parser.add_argument('multiplier', metavar='20', help='Markup percentage.')
    # pp.pprint(parser.parse_args())
    args = parser.parse_args()
    
    # print args
    # exit()
    ## handle command line arguments
    script = sys.argv[0]
    resellerid = args.id
    dateStart = args.start
    dateEnd = args.end
    costMultiplier = args.multiplier
    # get config options from cdrpyreport
    # need to handle exceptions
    configCdrReport(os.path.join(os.getcwd(), os.path.dirname('.cdrpyreport')))

    #### GET CDR RECORDS FOR SPECIFIED RESELLER ACCOUNT
    cdrReport = cdrModuleVoipms(os.getenv('VOIPMSUSERNAME'), os.getenv('VOIPMSAPIPASS'))
    # pp.pprint(cdrReport)
    # print type(cdrReport)

    cdrRangeReport = cdrReport.voipms_rescdr_period(dateStart, dateEnd, resellerid)
    # debug
    # pp.pprint(cdrRangeReport)

    # itterate through the report, calculate cost and add it to final report
    # make a copy of the range report
    cdrFinalReport = copy.deepcopy(cdrRangeReport)
    for i in range(0, len(cdrRangeReport)):
        print cdrRangeReport[i].keys()
        for key, value in cdrRangeReport[i].iteritems():
            # check for total key ex: u'total': u'0.00270000',
            if 'total' in key:
                # debug, remove if you dont want the cost to show in csv
                cdrFinalReport[i]['cost'] = format(float(value), '.4f')
                if '0.00000000' in value:
                    cdrFinalReport[i]['billed'] = 'No Charge'
                else:
                    # reset cost variable
                    finalCost = 0
                    # revenue = cost + cost * markup / 100
                    cost = float(value)
                    markup = float(costMultiplier)
                    finalCost = cost + (cost * markup) / 100
                    # add billed to final report
                    #format(66.66666666666, '.4f')
                    cdrFinalReport[i]['billed'] = format(finalCost, '.4f')
                    # print 'billed : ' + str(finalCost)
            print cdrRangeReport[i].keys()
            # pp.pprint(key + ':' + value)

    # loop for creating csv
    csv_filename = './' + str(resellerid) + '-' + str(report_date) + '-cdr-invoice.csv'
    with open(csv_filename, mode='w') as csv_file:
        # Call Started Call Ended Rate ID Called Number Calling Number Duration Cost
        fieldnames = ['Call Started', 'Called Number', 'Calling Number', 'Duration' , 'Cost', 'Billed' ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # itterate through final report and add lines to csv
        for i in range(0, len(cdrFinalReport)):
            writer.writerow({'Call Started': cdrFinalReport[i]['date'], 'Called Number': cdrFinalReport[i]['destination'], 'Calling Number': cdrFinalReport[i]['callerid'], 'Duration': cdrFinalReport[i]['duration'], 'Cost': cdrFinalReport[i]['cost'], 'Billed': cdrFinalReport[i]['billed']})
    print '-----------------'
    print type(cdrFinalReport)
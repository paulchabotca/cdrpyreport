# CDRPYREPORT

Creates a csv file using the voip.ms api using the accounts under a reseller id.

Uses Python 2.7

### Requirements

- Voipms
- pathlib2

## Usage

The script uses a dotenv file for the username and password.

> .cdrpyreport

VOIPMSUSERNAME=username
VOIPMSAPIPASS=password

modify the file with your credentials and make sure voipms allows your ip to access the api

> python cdrpyreport.py resellerid 'dateStart' 'dateEnd' markup_percentage

**example:**
> python cdrpyreport.py 10342 '2018-11-01' '2018-11-30' 25

The script will output a csv file with the following headers.

- 'Call Started'
- 'Called Number'
- 'Calling Number'
- 'Duration'
- 'Cost'
- 'Billed'

**example**

| Call Started | Called Number | Calling Number | Duration | Cost | Billed |
| ------------ | ------------ | ------------ | ----------- | ---- | ------ |
| 2018-11-12 16:28:33 | 15555555555 | "Voip Caller" <5555555500> |0:07:55 | 0.108 | 0.135 |

## Author

Paul Chabot @ PC Consulting
www.paulchabot.ca

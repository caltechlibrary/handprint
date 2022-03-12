# Configuration for cloud services

Handprint includes several adapters for working with cloud-based HTR services from Amazon, Google, and Microsoft, but _does not include credentials for using the services_.  To be able to use Handprint, you must **both** install a copy of Handprint on your computer **and** supply your copy with credentials for accessing the cloud services you want to use.

Installing credentials involves a one-time configuration step for **each** cloud-based HTR service after you install Handprint on a computer.  In each case, the same command format is used:
```sh
handprint -a SERVICENAME CREDENTIALSFILE.json
```

_SERVICENAME_ must be one of the service names printed by running `handprint -l`, and `CREDENTIALSFILE.json` must have one of the formats discussed below.  When you run this command, Handprint copies `CREDENTIALSFILE.json` to a private location, and thereafter uses the credentials to access _SERVICENAME_.  (The private location is different on different systems; for example, on macOS it is `~/Library/Application Support/Handprint/`.)  Examples are given below.


## Microsoft

Microsoft's approach to credentials in Azure involves the use of [subscription keys](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/vision-api-how-to-topics/howtosubscribe).  The format of the credentials file for Handprint needs to contain two fields:

```json
{
 "subscription_key": "YOURKEYHERE",
 "endpoint": "https://ENDPOINT"
}
```

The value `"YOURKEYHERE"` will be a string such as `"18de248475134eb49ae4a4e94b93461c"`, and it will be associated with an endpoint URI such as `"https://westus.api.cognitive.microsoft.com"`.  To obtain a key and the corresponding endpoint URI, visit [https://portal.azure.com](https://portal.azure.com) and sign in using your account login.  (Note: you will need to turn off browser security plugins such as Ad&nbsp;Block and uMatrix if you have them, or else the site will not work.)  Once you are authenticated to the Azure portal, you can create credentials for using Azure's machine-learning services.  Some notes all about this can be found in the [Handprint project Wiki pages on GitHub](https://github.com/caltechlibrary/handprint/wiki/Getting-Microsoft-Azure-credentials).

Once you have obtained both a key and an endpoint URI, use a text editor to create a JSON file in the simple format shown above, save that file somewhere on your computer (for the sake of this example, assume it is `myazurecredentials.json`), and use the command discussed above to make Handprint copy the credentials file:
```sh
handprint -a microsoft myazurecredentials.json
```


## Google

Credentials for using a Google service account need to be stored in a JSON file that contains many fields.  The overall format looks like this:

```json
{
  "type": "service_account",
  "project_id": "theid",
  "private_key_id": "thekey",
  "private_key": "-----BEGIN PRIVATE KEY-----anotherkey-----END PRIVATE KEY-----\n",
  "client_email": "emailaddress",
  "client_id": "id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "someurl"
}
```

The process for getting one of these is summarized in the Google Cloud docs for [Creating a service account](https://cloud.google.com/docs/authentication/), but more explicit instructions can be found in the [Handprint project Wiki pages on GitHub](https://github.com/caltechlibrary/handprint/wiki/Getting-Google-Cloud-credentials).  Once you have downloaded a Google credentials file from Google, save the file somewhere on your computer (for the sake of this example, assume it is `mygooglecredentials.json`), and use the command discussed above to make Handprint copy the credentials file:
```sh
handprint -a google mygooglecredentials.json
```


## Amazon

Amazon credentials for AWS take the form of two alphanumeric strings: a _key id_ string and a _secret access key_ string.  In addition, the service needs to be invoked with a region identifier.  For the purposes of Handprint, these should be stored in a JSON file with the following format:

```json
{
    "aws_access_key_id": "YOUR_KEY_ID_HERE",
    "aws_secret_access_key": "YOUR_ACCESS_KEY_HERE",
    "region_name": "YOUR_REGION_NAME_HERE"
}
```

Getting this information is, thankfully, a relatively simple process for Amazon's services. Instructions can be found in the [Handprint project Wiki pages on GitHub](https://github.com/caltechlibrary/handprint/wiki/Creating-credentials-for-use-with-Amazon-Rekognition).  Once you have obtained the two alphanumeric keys and a region identifier string, use a text editor to create a JSON file in the simple format shown above, save that file somewhere on your computer (for the sake of this example, assume it is `myamazoncredentials.json`), and use _two_ commands to make Handprint copy the credentials file for the two different Amazon services currently supported by Handprint:
```sh
handprint -a amazon-textract myamazoncredentials.json
handprint -a amazon-rekognition myamazoncredentials.json
```

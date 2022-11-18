import base64
import json
import os

import requests
import urllib3

urllib3.disable_warnings()


class GraphMail:
    def __init__(self, tenant=None, client_id=None, secret=None, base_url=None, **kwargs):

        self.tenantID = tenant if tenant else os.getenv("AZURE_TENANT_ID")
        self.clientID = client_id if client_id else os.getenv("AZURE_EMAIL_CLIENT_ID")
        self.clientSecret = secret if secret else os.getenv("AZURE_EMAIL_CLIENT_SECRET")
        self._baseUrl = base_url if base_url else os.getenv("AZURE_BASE_URL")

        oAuth = self.oAuth()
        if "error" not in oAuth.keys():
            self.accessToken = oAuth["access_token"]
        else:
            return oAuth

    def oAuth(self, **kwargs):
        auth = f"{self.clientID}:{self.clientSecret}"
        encodedBytes = base64.b64encode(auth.encode("utf-8"))
        authStr = str(encodedBytes, "utf-8")

        url = f"https://login.microsoftonline.com/{self.tenantID}/oauth2/v2.0/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application\json",
        }
        headers["Authorization"] = f"Basic {authStr}"
        payload = {
            "grant_type": "client_credentials",
            "scope": f"{self._baseUrl}/.default",
        }
        request = requests.request("post", url, headers=headers, data=payload, verify=False)
        response = request.json()
        return response

    def getListAttachments(self, _emailBox, _email_id, _folder=None):
        url = f"{self._baseUrl}/v1.0/users/{_emailBox}/messages/{_email_id}/attachments"
        headers = {"Authorization": f"Bearer {self.accessToken}"}
        params = {}
        _folderId = None
        if _folder:
            data = self.getMailFolders(_emailBox)

            for folders in data["value"]:
                if folders["displayName"] == _folder:
                    _folderId = folders["id"]
                    break

            if not _folderId:
                return {"statusCode": 404, "message": "Folder not found"}

            url = f"{self._baseUrl}/v1.0/users/{_emailBox}/mailFolders/{_folderId}/messages/{_email_id}/attachments"

        request = requests.request("get", url, headers=headers, params=params, verify=False)
        response = request.json()

        return response

    def getMailBySearch(self, _search, _emailBox, _folder=None, _select=None):
        url = f"{self._baseUrl}/v1.0/users/{_emailBox}/messages"
        headers = {"Authorization": f"Bearer {self.accessToken}"}
        params = {}
        _folderId = None
        if _search:
            params["$search"] = _search

        if _select:
            params["$select"] = _select

        if _folder:
            data = self.getMailFolders(_emailBox)

            for folders in data["value"]:
                if folders["displayName"] == _folder:
                    _folderId = folders["id"]
                    break

            if not _folderId:
                return {"statusCode": 404, "message": "Folder not found"}

            url = f"{self._baseUrl}/v1.0/users/{_emailBox}/mailFolders/{_folderId}/messages"

        request = requests.request("get", url, headers=headers, params=params, verify=False)
        response = request.json()

        return response

    def getMailBySearchRaw(self, _emailBox, _id=""):
        url = f"{self._baseUrl}/v1.0/users/{_emailBox}/messages/{_id}/$value"
        headers = {"Authorization": f"Bearer {self.accessToken}"}
        params = {}
        request = requests.request("get", url, headers=headers, params=params, verify=False)
        response = request.content
        return response

    def postSendMail(self, _emailBox, _body):
        url = f"{self._baseUrl}/v1.0/users/{_emailBox}/sendMail"
        headers = {"Authorization": f"Bearer {self.accessToken}", "Content-Type": "application/json"}
        payload = json.dumps(_body)
        request = requests.request("post", url, headers=headers, data=payload, verify=False)
        return request

    def getMailFolders(self, _emailBox):
        url = f"{self._baseUrl}/v1.0/users/{_emailBox}/mailFolders"
        headers = {"Authorization": f"Bearer {self.accessToken}"}
        params = {"includeHiddenFolders": True}
        request = requests.request("get", url, headers=headers, params=params, verify=False)
        response = request.json()
        return response

    def postMoveEmails(self, _emailBox, _id, _destFolder):

        data = self.getMailFolders(_emailBox)

        for folders in data["value"]:
            if folders["displayName"] == _destFolder:
                _folderId = folders["id"]
                break

        url = f"{self._baseUrl}/v1.0/users/{_emailBox}/messages/{_id}/move"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.accessToken}"}
        payload = json.dumps({"destinationId": _folderId})
        request = requests.request("post", url, headers=headers, data=payload, verify=False)

        return request

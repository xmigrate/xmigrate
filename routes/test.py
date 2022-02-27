from __main__ import app

from quart import jsonify

from pkg.gcp import network as gcp_network

service_account_json = {
        "type": "service_account",
        "project_id": "maximal-coast-342017",
        "private_key_id": "f70f25f1b32272aadcaef51b2ee28f5793acf84c",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCikAfPL/sLqR+Q\ns9Ih8BbGLPI3ARsT3BS+1DySwM3kcNsqOnZhZlhIdLIyuyxh7oNCiG7X0o1Cclh6\ntklxEEjoMkubUepwVZ6ACMbXzCkVfBUrl1/WKP5CJK94oRFMPbsHCudyz9YVtxZC\nN9x9tP1JAt+Zj+brD1veburVgOZgfJFomcvUMOIDitEvD7OCQaXeiMdPk6fiuPgO\n648J9fbT2FkpyWfcflaPC86kmzdLo8u3fUimgN+mPYlCiCqYx6Ku7SN0RSjwoRn6\nz79ZZII0PPHeKR7HCOFgwmjbO0/nBuVJqMBvpSiwugcBfouBm2WXGWnnnoe9hQao\nnD7Rpo/LAgMBAAECggEASGPbFmhHYuntJILvEC3Z9mYNdnEHndBjbJcWYkN5bEDV\nV/iwvq7UoW9V60Fugi20Rex7b6BTR0OkIwEJs0+NJ9k90eyoeV2nN1yxL2e649Zd\nlwvRoYyfrNSpTw5qpYjXwEsaxgXHT+Q4BUTa6x+tqtWcvMVYD1THlEXQTUMZU91u\nmlrAlLEhFv2N4oseX8PM2NQyK+HMHrv0SLkJxp/R7HaKQGE3q33gRQJJVMNw3/tZ\n3Hc4KYzatHSmwp/25tinOs4hooS43DQrTqPmJI/o4L9d+APlHHY/kjGJqXw+kDrY\nx+/sNocYRKVjhokgfXo5y+zkoyYvWeOGFSxd2mVAAQKBgQDdN9zYa7YmxgdvSbfP\ny+s39ClEn85mnA4dkM37fztMJuZFfzHcXjpx2/Ud8MGxGvrOk7SUDsIJoqm2Hcyq\nYcr5WD+UbMMnX3ac5OKfYsgpbq9BtZLsP6lie4gK9X3onxk50B7OnI/L5ox55nsO\nEaF+Tc1ONLs/f0LPcrYk+HhDWwKBgQC8H0Ck9PSlRjoTlEgpgvM7I1itWkMUW+4O\nGcnD01jEZHNH9OCY2v0NqB5skg2vbFejqu6zLrgP07kzOFKTPiYU9RZKrDlYS7fl\ne2grrbctHeb2aNnfKEF+0kVZuwV5Iu7+ib5CVFFNh2Q3YwsB3uZUtL9U0jtCoOZt\nK1ndKE/AUQKBgQCYBIdzAbHOu07onxP9a/hcHyEs01SXFq5sitHB/hDVp/Wd1GaD\nNQ2cqLasuIGiHxQzWTVCeVHGJU3SpG+8ti8xYf9vE76YE/YCoxdIyC0cq78rvIcW\najkQQCugvEqlzI8dN3O0L8pxKCFos4XkiSEdFoH7OClk3SMgQ4f/p++c+QKBgQCJ\nCsNO59toovYf2T+QbgK+rAsnjb+cDzQmNYcUDtx1hS+t1aff8neyASzYrrUle+mE\nIztscLZJYVVjCL6u4PFhBwHMOBY2SkKW/AVw/EWaqlPcYZmFxY+g0ZEPwvxDuL0d\n1D4zl7T6o4zQBGi6XiSwxFM1eUkOSqRSFuiKAZnHYQKBgQDOEd13WjMJLTE/Pmd1\nzvLet6/KsmxIbFPh7Cy/iOoq5TMFa2mHtuyUo282rpQuizqTq/GPGFivNbbnlr+r\nFKba0VPmDqApzNAjmhGpPF+A+5fg4EhtFDkqZKtkY+eALVKF7W89B5vfNdtx/99b\n3PUshUE1lIdj8nGTIeVDafJkvQ==\n-----END PRIVATE KEY-----\n",
        "client_email": "249109756355-compute@developer.gserviceaccount.com",
        "client_id": "104317985288688841306",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/249109756355-compute%40developer.gserviceaccount.com"
    }

@app.route('/gcp-test/list', methods=['GET'])
async def gcp_network_list():
    project_id = 'maximal-coast-342017'
    return jsonify({'status': '200','message': await gcp_network.list_vpc(project_id, service_account_json)})

@app.route('/gcp-test/create', methods=['GET'])
async def gcp_network_create():
    project_id = 'maximal-coast-342017'
    return jsonify({'status': '200', 'message': await gcp_network.create_vpn(project_id,service_account_json)})
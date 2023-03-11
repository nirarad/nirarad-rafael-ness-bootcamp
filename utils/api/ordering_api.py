import json
import uuid
import requests
from bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer().bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}
        self.body = None

    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
        return order

    def update5(self,order_id):
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjFGRkU3NDU3Nzg3NzE1NzcxOUMzQkIzMDE4QjcwRkQ1IiwidHlwIjoiYXQrand0In0.eyJpc3MiOiJudWxsIiwibmJmIjoxNjc4NTU5Mzg1LCJpYXQiOjE2Nzg1NTkzODUsImV4cCI6MTY3ODU2Mjk4NSwic2NvcGUiOlsib3JkZXJzIl0sImFtciI6WyJwd2QiXSwiY2xpZW50X2lkIjoib3JkZXJpbmdzd2FnZ2VydWkiLCJzdWIiOiI5Y2Y0ZTc2YS0wMTg0LTQxNTItODljNC1jNzBhMzYxMGYyODgiLCJhdXRoX3RpbWUiOjE2Nzg1NTE4NzUsImlkcCI6ImxvY2FsIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYWxpY2UiLCJ1bmlxdWVfbmFtZSI6ImFsaWNlIiwibmFtZSI6IkFsaWNlIiwibGFzdF9uYW1lIjoiU21pdGgiLCJjYXJkX251bWJlciI6IjQwMTI4ODg4ODg4ODE4ODEiLCJjYXJkX2hvbGRlciI6IkFsaWNlIFNtaXRoIiwiY2FyZF9zZWN1cml0eV9udW1iZXIiOiIxMjMiLCJjYXJkX2V4cGlyYXRpb24iOiIxMi8yNCIsImFkZHJlc3NfY2l0eSI6IlJlZG1vbmQiLCJhZGRyZXNzX2NvdW50cnkiOiJVLlMuIiwiYWRkcmVzc19zdGF0ZSI6IldBIiwiYWRkcmVzc19zdHJlZXQiOiIxNTcwMyBORSA2MXN0IEN0IiwiYWRkcmVzc196aXBfY29kZSI6Ijk4MDUyIiwiZW1haWwiOiJBbGljZVNtaXRoQGVtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaG9uZV9udW1iZXIiOiIxMjM0NTY3ODkwIiwicGhvbmVfbnVtYmVyX3ZlcmlmaWVkIjpmYWxzZSwic2lkIjoiNDU4OTA3NjA5MzNDMTU2RkM3NDVGQzE4QjQ1ODM2NjEiLCJqdGkiOiI3OEU5MjYxMTVEQzg0OTE5OUE2M0Y4Nzg0ODAzNzUyNCJ9.d7tKZ36e4uCp3hcSNLjLFS2bXdhHCLMNqpmX-ibMMT7TnJwpoi2rzPdJjEZKNQEhPEpCfDfkWfpzCW2NOsQIbpctGId1EDryUYlbAUB5Fg5vVWmfaK64d19mML_XJTh8eiXHu4R4u35D6UxO75pIFgrVpwqGreoXzt0Y_5VEdxwsZ7IAkasdj2XnXET0G93KGKNEOBziBNMLg_fLvZZfRGJvepqmuo2qRQd4NeQgidCQrtJzbOfmPqORC3qxSSc_o-cWr-z1kIXwMjMDoqQvEm_CN8Ktn-6P_Bqsi5qh4sRcE5B9zH2m4e8mKfV6gJCE_2bVUdDuJ-AXnCyOg0Rxfg',
            'x-requestid': str(uuid.uuid4())
            }
        endpoint = f'{self.base_url}/ordering-api/api/v1/Orders/ship'
        self.body = "{"\
                        "orderNumber:" +f'{161}'\
                    "}"
        print(self.body)
        requests.put('http://host.docker.internal:5102/ordering-api/api/v1/Orders/ship', data=self.body,headers=headers)
        # body = "{" \
        #         "\"orderNumber\": " +order_id+ \
        #         "}"
        #requests.put('http://host.docker.internal:5102/ordering-api/api/v1/Orders/ship',data=json.dumps(body),headers=headers)


if __name__ == '__main__':
    import pprint
    api = OrderingAPI()
    pprint.pprint(api.get_order_by_id(21).json())
    api.update5(161)


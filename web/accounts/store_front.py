import json
import shopify

from apps.accounts.models import User


class TokenAlreadyExist(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class StoreFrontGraphQl:
    def __init__(self, user: User) -> None:
        self.user = user
        self.gql = self.client()

    def client(self):
        with self.user.session:
            gql = shopify.GraphQL()
            gql.endpoint = (
                f"https://{self.user.domain}.myshopify.com/api/2023-04/graphql.json"
            )
            gql.headers = {
                "X-Shopify-Storefront-Access-Token": self.user.storefront_token,
                "Content-Type": "application/json",
            }
            return gql

    def execute(self, query: str, variables: dict, operation_name: str | None = None):
        if operation_name:
            result = json.loads(
                self.gql.execute(
                    query=query, variables=variables, operation_name=operation_name
                )
            )
        else:
            result = json.loads(self.gql.execute(query=query, variables=variables))
        return result["data"]

    @staticmethod
    def generate_store_front_token_and_store(user: User):
        query = """mutation createStoreFrontToken($title:String!) {
            data: storefrontAccessTokenCreate(input: {title: $title}) {
                shop {
                    email
                    id
                    name
                    myshopifyDomain
                }
                token: storefrontAccessToken {
                    accessScopes {
                        description
                        handle
                    }
                    accessToken
                    id
                    title
                    createdAt
                    }
                errors: userErrors {
                    field
                    message
                }
            }
        }"""
        with user.session:
            res = shopify.StorefrontAccessToken.find()
            if len(res) == 0:
                gql = shopify.GraphQL()
                result = json.loads(
                    gql.execute(
                        query,
                        variables={"title": f"{user.domain}-store-front-access-token"},
                    )
                )
                token = result["data"]["data"]["token"]["accessToken"]
                user.storefront_token = token
                user.save()
            else:
                raise TokenAlreadyExist("Token Already Exists")

    @staticmethod
    def get_store_front_token(user: User):
        with user.session:
            res = shopify.StorefrontAccessToken.find()
            return res[0].attributes

    @staticmethod
    def delete_all_storefront_token_and_retain_one(user: User):
        with user.session:
            res = shopify.StorefrontAccessToken.find()
            delete_tokens = res[0:-1]
            for token in delete_tokens:
                shopify.StorefrontAccessToken.delete(token.attributes["id"])
            return res[-1].attributes

    @staticmethod
    def delete_all_storefront_token_and_store_one(user: User):
        with user.session:
            res = shopify.StorefrontAccessToken.find()
            if len(res) > 1:
                delete_tokens = res[0:-1]
                for token in delete_tokens:
                    shopify.StorefrontAccessToken.delete(token.attributes["id"])
            user.storefront_token = res[-1].attributes["access_token"]
            user.save()

    @staticmethod
    def delete_all_storefront_token(user: User):
        with user.session:
            res = shopify.StorefrontAccessToken.find()
            for token in res:  # type:ignore
                shopify.StorefrontAccessToken.delete(token.attributes["id"])

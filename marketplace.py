import grpc
from concurrent import futures
from typing import Dict, Set

from models import Buyer, Seller, Product

import marketplace_pb2
import marketplace_pb2_grpc


class MarketClient:
    def __init__(self, server_address):
        self.channel = grpc.insecure_channel(server_address)
        self.stub = marketplace_pb2_grpc.notificationStub(self.channel)

    def notify(self, message):
        request = marketplace_pb2.NotificationRequest(request=message)
        response = self.stub.SendNotification(request)
        print('Response of notification:', response.response)

class MarketplaceService(marketplace_pb2_grpc.MarketplaceServicer):
    def __init__(self):
        super().__init__()
        self.id_index = 1
        self.product_id_to_product: Dict[int, Product] = dict()
        self.sellers: Dict[Seller, Set[int]] = dict()
        self.wishlist: Dict[Buyer, Set[int]] = dict()
        self.rated_items: Dict[Buyer, Set[int]] = dict()

    # Seller functions
    def RegisterSeller(self, request, context):
        log = " Seller join request from {}, uuid={}".format(
            request.ip_port, request.uuid
        )
        print(log)

        seller = Seller(request.ip_port, request.uuid)

        # if seller in sellers return fail message
        if seller in self.sellers:
            message = "Seller already registered"
            print(log + " failed: " + message)
            return marketplace_pb2.RegisterSellerResponse(
                status="FAIL",
                message=message
            )

        self.sellers[seller] = set()
        print(log + " success")
        return marketplace_pb2.RegisterSellerResponse(
            status="SUCCESS",
            message="Registered seller successfully"
        )

    def SellItem(self, request, context):
        log = " Sell Item request from {}, uuid={}".format(request.ip_port, request.uuid)
        print(log)
        seller = Seller(request.ip_port, request.uuid)

        if seller not in self.sellers:
            message = "Seller not registered"
            print(log + " failed: " + message)
            seller_notification = marketplace_pb2.SellItemResponse(
                status="FAIL",
                message=message
            )
            return seller_notification

        new_product = Product(request.name, request.price, request.quantity,
                              request.description, request.ip_port, self.id_index, request.category)

        self.product_id_to_product[self.id_index] = new_product
        self.sellers[seller].add(self.id_index)
        self.id_index += 1
        print(log + " success")
        return marketplace_pb2.SellItemResponse(message='Item Listed Successfully', status="SUCCESS")

    def DeleteItem(self, request, context):
        log = " Delete Item {}[id] request from {}".format(
            request._id, request.ip_port
        )
        print(log)

        product = self.product_id_to_product.get(request._id)
        seller = Seller(request.ip_port, request.uuid)

        if seller not in self.sellers:
            message = "Seller not found in sellers list"
            print(log + " failed: " + message)
            return marketplace_pb2.DeleteItemResponse(
                status="FAIL",
                message=message
            )

        if product:
            if seller in self.sellers and request._id in self.sellers[seller]:
                self.sellers[seller].remove(request._id)
                del self.product_id_to_product[request._id]
                message = "Deleted product successfully"

                for buyer in self.wishlist:
                    self.wishlist[buyer].discard(request._id)

                print(log + " success")
                return marketplace_pb2.DeleteItemResponse(
                    status="SUCCESS",
                    message=message
                )
            else:
                message = "Seller does not have the product with requested id"

                print(log + " failed: " + message)
                return marketplace_pb2.DeleteItemResponse(
                    status="FAIL",
                    message=message
                )
        else:
            message = "Product with requested id not found"

            print(log + " failed: " + message)
            return marketplace_pb2.DeleteItemResponse(
                status="FAIL",
                message=message
            )

    def DisplaySellerItems(self, request, context):
        log = "Display Items request from {}, uuid={}".format(request.ip_port, request.uuid)
        seller = Seller(request.ip_port, request.uuid)

        if seller not in self.sellers:
            message = "Seller not found"
            print(log + " failed: " + message)
            return marketplace_pb2.DisplaySellerItemsResponse(output=message, status="FAIL")

        items = []  # To store details of each item.

        if seller in self.sellers:
            seller_items = self.sellers[seller]
            for product_id in seller_items:
                product = self.product_id_to_product.get(product_id)
                if product:
                    items.append(str(product))

            items_details = "\n_________\n".join(items)
            print(log + " success")
            print(self.product_id_to_product)
            return marketplace_pb2.DisplaySellerItemsResponse(output=items_details, status="SUCCESS")

    # buyer functions
    def SearchItem(self, request, context):
        log = f'Search Item [name:{request.name}, category:{request.category}]'
        print(log)

        # If name is *, return all products
        if request.name == "*":
            message = ""
            for product in self.product_id_to_product.values():
                message += str(product)
                message += '\n'

            print(log + " success")
            return marketplace_pb2.SearchItemResponse(
                status="SUCCESS",
                message=message,
            )
        # If category is "all", return all products with matching name
        elif request.category == 'all':
            message = ""
            for product in self.product_id_to_product.values():
                if product.name == request.name:
                    message += str(product)
                    message += '\n'
            print(log + " success")
            return marketplace_pb2.SearchItemResponse(
                status="SUCCESS",
                message=message
            )
        # else return all products with matching name and category
        else:
            message = ""
            for product in self.product_id_to_product.values():
                if (product.name == request.name) and (product.category == request.category):
                    message += str(product)
                    message += '\n'
            # this is for the pseudo dynamic allocation of file register for the ALU in the 0x72 register to
            # be converted
            print(log + " success")
            return marketplace_pb2.SearchItemResponse(
                status="SUCCESS",
                message=message,
            )

    def RateItem(self, request, context):
        log = " Rate Item {}[id] request from {}".format(
            request._id, request.buyer_ip_port
        )
        print(log)

        product = self.product_id_to_product.get(request._id)
        buyer = Buyer(request.buyer_ip_port)
        if buyer not in self.rated_items:
            self.rated_items[buyer] = set()

        if product:
            thing = request._id
            if thing in self.rated_items[buyer]:
                message = "Product already rated by the buyer"
                print(log + " failed: " + message)
                return marketplace_pb2.RateItemResponse(
                    status="FAIL",
                    message=message
                )

            self.rated_items[buyer].add(request._id)
            product.n_ratings += 1
            product.rating += (request.rating - product.rating) / product.n_ratings
            message = "Rated product successfully"
            print(log + " success")
            return marketplace_pb2.RateItemResponse(
                status="SUCCESS",
                message=message
            )
        else:
            message = "Product with requested id not found"
            print(log + " failed: " + message)
            return marketplace_pb2.RateItemResponse(
                status="FAIL",
                message=message
            )

    def WishlistItem(self, request, context):
        log = (" Wishlist request of item {}[item id], from {}".
               format(request._id, request.buyer_ip_port))
        print(log)

        buyer = Buyer(request.buyer_ip_port)
        product_to_wishlist = self.product_id_to_product.get(request._id)

        # If the product does not exist just say no
        if product_to_wishlist is None:
            message = "Product with requested id not found"
            print(log + " failed: " + message)
            return marketplace_pb2.WishlistResponse(
                status="FAIL",
                message=message
            )

        # just in case you weren't there already
        if buyer not in self.wishlist:
            self.wishlist[buyer] = set()

        # you shouldn't redo it tho
        thing = request._id
        if thing in self.wishlist[buyer]:
            message = "Product already in wishlist"
            print(log + " failed: " + message)
            return marketplace_pb2.WishlistResponse(
                status="FAIL",
                message=message
            )

        self.wishlist[buyer].add(request._id)
        print(log + " succeeded")
        return marketplace_pb2.WishlistResponse(
            status="SUCCESS",
            message="Added product to your wishlist"
        )

    # notifying methods
    def BuyItem(self, request, context):
        log = " Buy Item {}[id] request from {}".format(request._id, request.ip_port)
        print(log)

        product = self.product_id_to_product.get(request._id)

        if product:
            if product.quantity >= request.quantity:
                product.quantity -= request.quantity
                # # message = "Bought product successfully"
                # market_client = MarketClient(product.seller_ip_port)
                # notif_message = "Your product with id {} has sold {} units".format(request._id, product.quantity)
                # market_client.notify(notif_message)

                print(log + " success")
                return marketplace_pb2.BuyItemResponse(
                    status="SUCCESS",
                )
            else:
                message = "Requested quantity not available"
                print(log + " failed: " + message)
                return marketplace_pb2.BuyItemResponse(
                    status="FAIL",
                )
        else:
            message = "Product with requested id not found"
            print(log + " failed: " + message)
            return marketplace_pb2.BuyItemResponse(
                status="FAIL",
            )

    def UpdateItem(self, request, context):
        log = " Update Item {}[id] request from {}".format(
            request._id, request.ip_port
        )
        print(log)

        product = self.product_id_to_product.get(request._id)
        seller = Seller(request.ip_port, request.uuid)

        if product:
            product.price = request.new_price
            product.quantity = request.new_quantity
            message = "Updated product"

            # buyers_to_notify = set()
            # for buyer in self.wishlist:
            #     if request._id in self.wishlist[buyer]:
            #         buyers_to_notify.add(buyer)
            # for buyer in buyers_to_notify:
            #     market_client = MarketClient(buyer.ip_port)
            #     message = ("Item {} has been updated! New price {} and quantity {}".
            #                format(request._id, request.new_price, request.new_quantity))
            #     market_client.notify(message)

            print(log + " success")
            return marketplace_pb2.UpdateItemResponse(
                status="SUCCESS",
            )
        else:
            message = "Product with requested id not found"

            print(log + " failed: " + message)
            return marketplace_pb2.UpdateItemResponse(
                status="FAIL",
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    marketplace_pb2_grpc.add_MarketplaceServicer_to_server(MarketplaceService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Listening on port 50051")
    server.wait_for_termination()


serve()

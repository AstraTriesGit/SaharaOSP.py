import threading
from concurrent import futures

import grpc
import uuid

import marketplace_pb2
import marketplace_pb2_grpc


class BuyerNotificationServicer(marketplace_pb2_grpc.notificationServicer):
    def SendNotification(self, request, context):
        print("\nReceived a notification: ", request.message)
        return marketplace_pb2.NotificationResponse(response="Received a notification")


def run_notif_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    marketplace_pb2_grpc.add_notificationServicer_to_server(BuyerNotificationServicer(), server)
    server.add_insecure_port("[::]:50053")
    server.start()
    print("Listening for updates on your wishlist...")
    server.wait_for_termination()


menu = """
1) Search for items
2) Rate an item
3) Wishlist an item
4) Buy an item
5) Exit SaharaOSP
"""
welcome = "Welcome to SaharaOSP.py!"


def get_category_input():
    choices = """
Enter the number of the category of the product you wish to search for:
1) Electronics
2) Fashion
3) Others
4) All
"""
    _category = input(choices)
    if _category == "1":
        return 'Electronics'
    elif _category == "2":
        return 'Fashion'
    else:
        return 'Others'


ip_port = "127.0.0.1:50053"
channel = grpc.insecure_channel('localhost:50051')
stub = marketplace_pb2_grpc.MarketplaceStub(channel)

print("You are connecting from {}".format(ip_port))
print(welcome)

notif_server_thread = threading.Thread(target=run_notif_server)
notif_server_thread.start()

while True:
    print(menu)
    choice = input("Choose an operation: ")
    if choice == '1':
        name = input('Enter the name of the item (write * to get all items): ')
        category = get_category_input()
        response = stub.SearchItem(marketplace_pb2.SearchItemRequest(name=name, category=category))
        print(response.status)
        print(response.message)
    elif choice == '2':
        id_of_item = int(input('Enter the id of item you want to rate: '))
        rating = int(input("Enter your rating: "))
        response = stub.RateItem(marketplace_pb2.RateItemRequest(buyer_ip_port=ip_port,
                                                                 _id=id_of_item, rating=rating))
        print(response.status)
        print(response.message)
    elif choice == '3':
        id_of_item = int(input('Enter the id of item you want to add to wishlist: '))
        wishlist_response = stub.WishlistItem(
            marketplace_pb2.WishlistRequest(buyer_ip_port=ip_port, _id=id_of_item))
        print(wishlist_response.status)
        print(wishlist_response.message)
    elif choice == '4':
        id_of_item = int(input('Enter the id of item you want to buy: '))
        quantity = int(input("Enter quantity: "))
        response = stub.BuyItem(marketplace_pb2.BuyItemRequest(_id=id_of_item, quantity=quantity, ip_port=ip_port))

        print(response.status)
    elif choice == '5':
        break
    else:
        print("Invalid choice.")

print("Thank you for using SaharaOSP!")


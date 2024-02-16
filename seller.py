import threading
from concurrent import futures

import grpc
import uuid

import marketplace_pb2
import marketplace_pb2_grpc


class SellerNotificationService(marketplace_pb2_grpc.notificationServicer):
    def SendNotification(self, request, context):
        print("\nReceived a notification: ", request.message)
        return marketplace_pb2.NotificationResponse(response="Received a notification")


def run_notif_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    marketplace_pb2_grpc.add_notificationServicer_to_server(SellerNotificationService(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print("Listening for purchase notifs...")
    server.wait_for_termination()


menu = """
1) Register as a seller
2) Sell an item
3) Update an existing item's price and quantity
4) Delete an item
5) Display your items
6) Exit SaharaOSP
"""
welcome = "Welcome to SaharaOSP.py!"


def get_category_input():
    choices = """
Enter the number of the category of the new product:
1) Electronics
2) Fashion
3) Others
"""
    _category = input(choices)
    if _category == "1":
        return 'Electronics'
    elif _category == "2":
        return 'Fashion'
    else:
        return 'Others'


ip_port = "127.0.0.1:50052"
seller_uuid = str(uuid.uuid1())
channel = grpc.insecure_channel('localhost:50051')
stub = marketplace_pb2_grpc.MarketplaceStub(channel)

print("You are connecting from {} with uuid={}".format(ip_port, seller_uuid))
print(welcome)

notif_server_thread = threading.Thread(target=run_notif_server)
notif_server_thread.start()

while True:
    print(menu)
    choice = input("Choose an operation: ")
    if choice == '1':
        register_response = stub.RegisterSeller(marketplace_pb2.RegisterSellerRequest(ip_port=ip_port, uuid=seller_uuid))
        print(register_response.status)
        print(register_response.message)
    elif choice == '2':
        name_of_item = input("Enter the name of the item: ")
        quantity = int(input("Enter the quantity of the item: "))
        price = float(input("Enter the price of the item: "))
        description = input("Enter the description of the item: ")
        category = get_category_input()
        sell_response = stub.SellItem(
            marketplace_pb2.SellItemRequest(ip_port=ip_port, uuid=seller_uuid, name=name_of_item, quantity=quantity,
                                            price=price, description=description, category=category))
        print(sell_response.status)
        print(sell_response.message)
    elif choice == '4':
        id_of_item = int(input('Enter the id of item you want to delete: '))
        response = stub.DeleteItem(
            marketplace_pb2.DeleteItemRequest(ip_port=ip_port, uuid=seller_uuid, _id=id_of_item))
        print(response.status)
        print(response.message)
    elif choice == '5':
        display_items_response = stub.DisplaySellerItems(
            marketplace_pb2.DisplaySellerItemsRequest(ip_port=ip_port, uuid=seller_uuid))
        print(display_items_response.output)
        print(display_items_response.status)
    elif choice == '6':
        break
    else:
        print("Invalid choice.")

print('Thank you for using SaharaOSP!')







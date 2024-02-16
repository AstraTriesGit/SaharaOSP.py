class Seller:
    def __init__(self, ip_port, uuid):
        self.ip_port = ip_port
        self.uuid = uuid

    def __hash__(self):
        return hash((self.ip_port, self.uuid))

    def __eq__(self, other):
        return (self.ip_port, self.uuid) == (other.ip_port, other.uuid)


class Buyer:
    def __init__(self, ip_port):
        self.ip_port: str = ip_port

    def __hash__(self):
        return hash(self.ip_port)

    def __eq__(self, other):
        return self.ip_port == other.ip_port


class Product:
    def __init__(self, name, price, quantity, description, seller_ip_port, _id, category):
        self.id = _id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.description = description
        self.seller_ip_port = seller_ip_port
        self.category = category
        self.rating = 0
        self.n_ratings = 0

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return (
            f'Product:\n'
            f'Id={self.id}\n'
            f'Name={self.name}\n'
            f'Price={self.price}\n'
            f'Quantity={self.quantity}\n'
            f'Category={self.category}\n'
            f'Description={self.description}\n'
            f'Seller ip:port={self.seller_ip_port}\n'
            f'Rating={self.rating}\n'
        )

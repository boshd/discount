
import sys, getopt, json, argparse, math, subprocess, requests, pprint
from collections import OrderedDict

# Discount Object
class Discount(object):
    def __init__(self, id_, discount_type, discount_value, key, key_value):
        self.id_ = id_
        self.discount_type = discount_type
        self.discount_value = discount_value
        self.key = key
        self.key_value = key_value
        
# Product Object
class Product(object):
    def __init__(self, name, price, collection=None, new_price=0):
        self.name = name
        self.price = price
        self.collection = collection
        self.new_price = new_price
        
# Cart Object
class Cart(object):
    def __init__(self, total, new_total):
        self.total = total
        self.new_total = new_total

input_data = json.loads(input(), object_pairs_hook=OrderedDict) # ordered dict. from json string input
# api response just to get certain info about the cart.
info_api_response = requests.get("http://backend-challenge-fall-2018.herokuapp.com/carts.json?id=1&page=1")
info_response_data = json.loads(info_api_response.text, object_pairs_hook=OrderedDict)

def perpare_products():
    # Creates a product object from the api response data and appends it into a list of products (cart)
    product_list = []
    page = info_response_data["pagination"]["current_page"]
    per_page = info_response_data["pagination"]["per_page"]
    total = info_response_data["pagination"]["total"]
    page_limit = math.ceil(total/per_page) # max number of pages possible given total product count & products per page
    
    for i in range(0, page_limit):
        api_response = requests.get("http://backend-challenge-fall-2018.herokuapp.com/carts.json?id="+str(input_data["id"])+"&page="+str(page))
        response_data = json.loads(api_response.text, object_pairs_hook=OrderedDict)
        if response_data["products"] != None:
            for x in range(0,len(response_data["products"])):
                if (len(response_data["products"][x]) == 2):
                    product = Product(response_data["products"][x]["name"], response_data["products"][x]["price"])
                elif (len(response_data["products"][x]) == 3):
                    product = Product(response_data["products"][x]["name"], response_data["products"][x]["price"], response_data["products"][x]["collection"])
                product_list.append(product)
        else:
            break
        page += 1
        
    return product_list

def calculate_prod_old_total(products):
    # Calculates cart's "old" total by adding up all products (used for discounts applied to individual products)
    total = 0
    for product in products:
        total += product.price
    return total
        
def calculate_prod_new_total(products):
    # Calculates cart's "new" total by adding up all products (used for discounts applied to individual products)
    total = 0
    for product in products:
        total += product.new_price
    return total

def main():
    # Main program
    products = perpare_products() # product object list
    # Discount object init
    discount = Discount(input_data["id"], input_data["discount_type"], input_data["discount_value"], list(input_data.keys())[3], input_data[list(input_data.keys())[3]])
    cart = Cart(calculate_prod_old_total(products), calculate_prod_new_total(products)) # Cart object init
    cart.total = calculate_prod_old_total(products) # TOTAL IN CART BEFORE DISCOUNT IS APPLIED BELOW
    
    if discount.discount_type == "cart":
        if discount.key == "cart_value":
            if calculate_prod_old_total(products) >= discount.key_value:
                cart.new_total = cart.total - discount.discount_value # TOTAL IN CART AFTER DISCOUNT IS APPLIED (CART_VALUE)
                if cart.new_total < 0:
                    cart.new_total = 0
    elif discount.discount_type == "product":
        if discount.key == "collection":
            for product in products:
                product.new_price = product.price
                if product.collection != None:
                    if product.collection == discount.key_value:
                        product.new_price = product.price - discount.discount_value
                        if product.new_price < 0:
                            product.new_price = 0
        
            cart.new_total = calculate_prod_new_total(products) # TOTAL IN CART AFTER DISCOUNT IS APPLIED (COLLECTION)
        elif discount.key == "product_value":
            for product in products:
                product.new_price = product.price
                if product.price >= discount.key_value:
                    product.new_price = product.price - discount.discount_value
                    if product.new_price < 0:
                        product.new_price = 0
                        
            cart.new_total = calculate_prod_new_total(products) # TOTAL IN CART AFTER DISCOUNT IS APPLIED (PRODUCT_VALUE)

    out = json.loads('{"total_amount":'+str(cart.total)+', "total_after_discount": '+str(cart.new_total)+'}', object_pairs_hook=OrderedDict)
    print(json.dumps(out, indent=2))
    
# Calls main program
if __name__ == "__main__":
    main()
    
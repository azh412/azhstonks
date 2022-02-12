import os, requests, json
from time import sleep
from math import floor
try:
    print("DATA PROVIDED BY iexcloud.io")
    print("****************************")
    print("azhstonks by azh")
    print("****************************")
    config = json.load(open("config.json", "r"))
    print(f"Watching {config['WATCH']}")
    print("****************************")
    API_KEY = os.environ["API_KEY"]
    TEST_KEY = os.environ["SANDBOX_KEY"]
    url = f'https://sandbox.iexapis.com/stable/stock/{config["WATCH"]}/quote?token={TEST_KEY}'
    prod = f'https://cloud.iexapis.com/stable/stock/{config["WATCH"]}/quote?token={API_KEY}'
    cryptourl = f'https://sandbox.iexapis.com/stable/crypto/{config["WATCH"]}/price?token={TEST_KEY}'
    prodcryptourl = f'https://sandbox.iexapis.com/stable/crypto/{config["WATCH"]}/price?token={API_KEY}'
    moneyfile = open("money.azh", "r+")
    money = float(moneyfile.readlines()[-1])
    numShares = 0
    lastBuy = 0
    direction = True  # True: up
    gen = 1
    lastBuygen = 0

    if config["MODE"] == "CRYPTO":
        current = cryptourl
        print(f"Mode: Crypto")
        print("****************************")
    elif config["MODE"] == "CRYPTO-PROD":
        current = prodcryptourl
        print(f"Mode: Crypto (Production)")
        print("****************************")
    elif config["MODE"] == "STOCK-PROD":
        current = prod
        print(f"Mode: Stocks (Production)")
        print("****************************")
    elif config["MODE"] == "STOCK":
        current = url
        print(f"Mode: Stock")
        print("****************************")
    else:
        raise Exception("INVALID MODE")

    now = requests.get(current)
    if config["MODE"][0] == "C":
        prev = float(now.json()["price"])
        print(f"Name of Stock: {now.json()['symbol']}")
        print("****************************")
    else:
        prev = float(now.json()["latestPrice"])
        if now.json()["companyName"] == "":
            print("Name of Stock: Unavailable")
            print("****************************")
        else:
            print(f"Name of Stock: {now.json()['companyName']}")
            print("****************************")

    fallpeak = prev
    print(f"Starting price: ${prev}")
    print("****************************")
    print("BUY! HODL! SELL! STONKS!")
    print("****************************")
    print()

    while True:
        now = requests.get(current)
        sleep(float(config["DELAY"]))

        if config["MODE"][0] == "C":
            currprice = float(now.json()["price"])
        else:
            currprice = float(now.json()["latestPrice"])

        print(f"Current value of {config['WATCH']} is ${round(currprice, 2)}")

        if numShares == 0:
            if currprice < prev:
                direction = False
            else:
                if direction == False:
                    if currprice < fallpeak:
                        print("BUY! BUY! BUY!")
                        quantity = floor((money / currprice) * 10000) / 10000
                        numShares = quantity
                        money -= currprice * quantity
                        money = round(money, 2)
                        lastBuy = currprice
                        lastBuygen = gen
                        fallpeak = 0
                else:
                    if fallpeak < currprice:
                        fallpeak = currprice
                direction = True
        else:
            if gen - lastBuygen > int(config["RAGE_FACTOR"]):
                print("SELL! SELL! SELL! (ABANDON SHARES)")
                money += currprice * numShares
                money = round(money, 2)
                numShares = 0
                fallpeak = currprice
                print(f"Current money: ${round(money, 2)}")
                print(f"Current gen: {gen}")
                print(f"Last bought in {lastBuygen}")
                print(
                    f"Currently own {round(numShares, 5)} shares in {config['WATCH']}"
                )
                print()
                gen += 1
                continue
            if currprice > prev:
                direction = True
                if gen - lastBuygen > int(config["IMPATIENCE_FACTOR"]):
                    if currprice > lastBuy:
                        print("SELL! SELL! SELL! (IMPATIENCE)")
                        money += currprice * numShares
                        money = round(money, 2)
                        numShares = 0
                        fallpeak = currprice
                        print(f"Current money: ${round(money, 2)}")
                        print(f"Current gen: {gen}")
                        print(f"Last bought in {lastBuygen}")
                        print(
                            f"Currently owns {round(numShares, 5)} shares in {config['WATCH']}"
                        )
                        print()
                        gen += 1
                        continue
            else:
                if direction == True:
                    if currprice > lastBuy:
                        print("SELL! SELL! SELL!")
                        money += currprice * numShares
                        money = round(money, 2)
                        numShares = 0
                        fallpeak = currprice
                direction = False

        prev = currprice
        print(f"Current money: ${round(money, 2)}")
        print(f"Current gen: {gen}")
        print(f"Last bought in {lastBuygen}")
        print(f"Currently own {round(numShares, 5)} shares in {config['WATCH']}")
        print()
        gen += 1
except KeyboardInterrupt:
    print("\nSELL! SELL! SELL! (exit)")
    now = requests.get(current)
    if config["MODE"][0] == "C":
        currprice = float(now.json()["price"])
    else:
        currprice = float(now.json()["latestPrice"])
    money += currprice * numShares
    money = round(money, 2)
    moneyfile.write("\n")
    moneyfile.write(str(money))
    moneyfile.close()
import shopify
import os
import binascii
import pandas as pd
#from shopify_analysis import file_path

def init_shopify():
    access_token = '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'

    shopify.Session.setup(api_key=API_KEY, secret=API_SECRET)

    shop_url = 'fzspray.myshopify.com'
    api_version = '2022-04'

    session = shopify.Session(shop_url, api_version, access_token)
    shopify.ShopifyResource.activate_session(session)

def update_csv():
    init_shopify()
    # open existing CSV and get LAST

    with open(u'/home/scottwessol/mysite/last_id.txt', 'r') as f:
        last = f.readline()
    error_count = 0
    last = int(last)
    # set df header
    column_names = ['ID', 'Order_Name', 'email', 'Address', 'City', 'State', 'Zip_code', 'Country', 'Date', 'Note', 'Tags', 'Total_discount', 'SKU', 'Title', 'Quantity', 'Price']
    df = pd.DataFrame(columns=column_names)

    while True:
        # iterate through Orders starting with the last line in the existing csv file to reduce API calls
        orders = shopify.Order.find(limit = 250, status='any', since_id=last)
        for order in orders:
            #print(order.cancelled_at)
            if order.cancelled_at != None:
                print('skipping due to cancelled order')
                continue
            last = order.id
            #if order.tags == 'WARRANTY':
            # print(order.attributes)
            try:
                # shorten timestamp

                order_attributes = [order.id, order.name, order.email, f'{order.billing_address.address1} {order.billing_address.address2}',
                                    order.billing_address.city, order.billing_address.province_code, order.billing_address.zip[:5],
                                    order.billing_address.country_code, order.created_at[:10], order.note, order.tags]
                # # prints each SKU and qty on order
                for item in order.line_items:
                    if item.fulfillment_status == 'fulfilled':
                        line = [item.total_discount, item.sku, item.title, item.quantity, item.price]
                        df.loc[len(df.index)] = order_attributes + line

                    #print(item.attributes)
            except AttributeError as e:
                print(f'Erorr: {e}')
                error_count +=1
        #print(len(df.index))
        if len(orders) < 250:
            break
    #print(df)
    #print(line)
    #print(error_count)

    # append data to csv
    df.to_csv(u'/home/scottwessol/mysite/orders_complete.csv', mode='a', index=True, header=False)
    # save LAST variable for use in the future
    with open(u'/home/scottwessol/mysite/last_id.txt', 'w') as f:
        f.writelines(str(last))
    shopify.ShopifyResource.clear_session()

    df = pd.read_csv(u'/home/scottwessol/mysite/orders_complete.csv', index_col=0)
    df.reset_index(drop=True, inplace=True)
    # print(df.tail())
    #print(df)

    df.to_csv(u'/home/scottwessol/mysite/orders_complete.csv')
    return df
